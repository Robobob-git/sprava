<#
.SYNOPSIS
    Synchronise les sessions GitHub Copilot Chat (state.vscdb) entre plusieurs machines
    via un dossier partagé (OneDrive, partage réseau, ou tout chemin local/cloud).

.DESCRIPTION
    Ce script réalise les opérations suivantes :
      1. Ferme VS Code proprement (optionnel, via -CloseVSCode).
      2. Détecte automatiquement tous les dossiers workspaceStorage contenant state.vscdb.
      3. Effectue un backup horodaté avant toute modification.
      4. Utilise un fichier sémaphore (.lock) pour éviter la corruption en cas
         d'accès concurrent depuis deux machines.
      5. Compare les timestamps pour décider qui est la version la plus récente
         (stratégie "last-write-wins").
      6. Copie (push ou pull) vers/depuis le dossier partagé.
      7. Remet VS Code en route (optionnel, via -LaunchVSCode).
      8. Loggue chaque action dans un fichier journalisé.

.PARAMETER SharedFolder
    Chemin vers le dossier partagé (ex: "C:\Users\VotreNom\OneDrive\CopilotChatSync").
    Ce dossier doit être accessible en lecture/écriture sur toutes les machines.

.PARAMETER Direction
    "push"  : envoie le state.vscdb local vers le dossier partagé.
    "pull"  : récupère le state.vscdb depuis le dossier partagé.
    "auto"  : compare les timestamps et choisit automatiquement (défaut).

.PARAMETER CloseVSCode
    Si présent, ferme VS Code avant la synchronisation.

.PARAMETER LaunchVSCode
    Si présent, relance VS Code après la synchronisation.

.PARAMETER MaxBackups
    Nombre de backups horodatés à conserver par workspace (défaut: 10).

.PARAMETER LockTimeoutSeconds
    Temps d'attente maximum (en secondes) pour acquérir le verrou (défaut: 30).

.PARAMETER LogFile
    Chemin du fichier de log. Par défaut : SharedFolder\sync.log

.EXAMPLE
    .\Sync-CopilotChat.ps1 -SharedFolder "C:\Users\Bob\OneDrive\CopilotSync" -Direction auto -CloseVSCode -LaunchVSCode

.EXAMPLE
    .\Sync-CopilotChat.ps1 -SharedFolder "\\serveur\partage\CopilotSync" -Direction push

.NOTES
    Testé sur Windows 10/11 avec PowerShell 5.1 et PowerShell 7+.
    Aucune dépendance externe requise.
    Auteur : généré pour le projet sprava / Robobob-git
    Version : 1.0.0
#>

[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory)]
    [string]$SharedFolder,

    [ValidateSet("push", "pull", "auto")]
    [string]$Direction = "auto",

    [switch]$CloseVSCode,
    [switch]$LaunchVSCode,

    [int]$MaxBackups = 10,
    [int]$LockTimeoutSeconds = 30,

    [string]$LogFile
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ─────────────────────────────────────────────────────────────────────────────
#  CONSTANTES
# ─────────────────────────────────────────────────────────────────────────────
$SCRIPT_VERSION   = "1.0.0"
$DB_FILENAME      = "state.vscdb"
$LOCK_FILENAME    = "sync.lock"
$BACKUP_SUBDIR    = "backups"
$VSCODE_PROCESSES = @("Code", "Code - Insiders")

# ─────────────────────────────────────────────────────────────────────────────
#  INITIALISATION DU LOG
# ─────────────────────────────────────────────────────────────────────────────
if (-not $LogFile) {
    $LogFile = Join-Path $SharedFolder "sync.log"
}

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "[$timestamp][$Level] $Message"
    Write-Host $line
    try {
        Add-Content -Path $LogFile -Value $line -Encoding UTF8
    } catch {
        Write-Warning "Impossible d'écrire dans le log : $_"
    }
}

# ─────────────────────────────────────────────────────────────────────────────
#  FONCTIONS UTILITAIRES
# ─────────────────────────────────────────────────────────────────────────────

function Initialize-SharedFolder {
    param([string]$Path)
    if (-not (Test-Path $Path)) {
        Write-Log "Création du dossier partagé : $Path"
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
    }
    $backupPath = Join-Path $Path $BACKUP_SUBDIR
    if (-not (Test-Path $backupPath)) {
        New-Item -ItemType Directory -Path $backupPath -Force | Out-Null
    }
}

function Get-WorkspaceStoragePaths {
    <#
    Retourne la liste de tous les fichiers state.vscdb trouvés dans
    %APPDATA%\Code\User\workspaceStorage (et la variante Insiders).
    #>
    $roots = @(
        Join-Path $env:APPDATA "Code\User\workspaceStorage"
        Join-Path $env:APPDATA "Code - Insiders\User\workspaceStorage"
    )
    $results = @()
    foreach ($root in $roots) {
        if (Test-Path $root) {
            $dbs = Get-ChildItem -Path $root -Recurse -Filter $DB_FILENAME -File -ErrorAction SilentlyContinue
            foreach ($db in $dbs) {
                $results += $db
            }
        }
    }
    return $results
}

function Get-FileHash-Fast {
    param([string]$FilePath)
    try {
        return (Get-FileHash -Path $FilePath -Algorithm SHA256).Hash
    } catch {
        return $null
    }
}

function Invoke-Backup {
    param(
        [string]$SourceFile,
        [string]$BackupDir,
        [string]$Prefix
    )
    $timestamp  = Get-Date -Format "yyyyMMdd_HHmmss"
    $machineName = $env:COMPUTERNAME
    $backupName = "${Prefix}_${machineName}_${timestamp}.vscdb"
    $dest       = Join-Path $BackupDir $backupName

    Copy-Item -Path $SourceFile -Destination $dest -Force
    Write-Log "Backup créé : $dest"

    # Rotation : ne garder que les $MaxBackups plus récents pour ce préfixe
    $existing = Get-ChildItem -Path $BackupDir -Filter "${Prefix}_*.vscdb" |
                Sort-Object LastWriteTime -Descending
    if ($existing.Count -gt $MaxBackups) {
        $toDelete = $existing | Select-Object -Skip $MaxBackups
        foreach ($f in $toDelete) {
            Remove-Item $f.FullName -Force
            Write-Log "Backup supprimé (rotation) : $($f.Name)"
        }
    }
    return $dest
}

function Wait-ForLock {
    param(
        [string]$LockPath,
        [int]$TimeoutSeconds
    )
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while (Test-Path $LockPath) {
        $content = Get-Content $LockPath -ErrorAction SilentlyContinue
        Write-Log "Verrou présent ($content). Attente..." "WARN"

        # Vérifier si le verrou est périmé (> 5 min) → stale lock
        $lockFile = Get-Item $LockPath -ErrorAction SilentlyContinue
        if ($lockFile -and $lockFile.LastWriteTime -lt (Get-Date).AddMinutes(-5)) {
            Write-Log "Verrou périmé détecté, suppression forcée." "WARN"
            Remove-Item $LockPath -Force
            break
        }

        if ((Get-Date) -gt $deadline) {
            throw "Timeout : impossible d'acquérir le verrou après $TimeoutSeconds secondes."
        }
        Start-Sleep -Seconds 2
    }
}

function Set-Lock {
    param([string]$LockPath)
    $info = "$($env:COMPUTERNAME) | PID:$PID | $(Get-Date -Format 'o')"
    Set-Content -Path $LockPath -Value $info -Encoding UTF8 -Force
    Write-Log "Verrou acquis : $LockPath"
}

function Remove-Lock {
    param([string]$LockPath)
    if (Test-Path $LockPath) {
        Remove-Item $LockPath -Force
        Write-Log "Verrou libéré : $LockPath"
    }
}

function Close-VSCode {
    foreach ($proc in $VSCODE_PROCESSES) {
        $running = Get-Process -Name $proc -ErrorAction SilentlyContinue
        if ($running) {
            Write-Log "Fermeture de VS Code ($proc)..."
            $running | ForEach-Object { $_.CloseMainWindow() | Out-Null }
            Start-Sleep -Seconds 3
            # Force kill si toujours là
            $stillRunning = Get-Process -Name $proc -ErrorAction SilentlyContinue
            if ($stillRunning) {
                Write-Log "Fermeture forcée de VS Code ($proc)..." "WARN"
                $stillRunning | Stop-Process -Force
            }
            Write-Log "VS Code ($proc) fermé."
        }
    }
}

function Start-VSCode {
    $codePaths = @(
        "$env:LOCALAPPDATA\Programs\Microsoft VS Code\Code.exe"
        "$env:ProgramFiles\Microsoft VS Code\Code.exe"
        "${env:ProgramFiles(x86)}\Microsoft VS Code\Code.exe"
    )
    foreach ($path in $codePaths) {
        if (Test-Path $path) {
            Write-Log "Relance de VS Code : $path"
            Start-Process -FilePath $path
            return
        }
    }
    # Fallback : chercher dans PATH
    $codeInPath = Get-Command "code" -ErrorAction SilentlyContinue
    if ($codeInPath) {
        Write-Log "Relance de VS Code via PATH : $($codeInPath.Source)"
        Start-Process -FilePath $codeInPath.Source
    } else {
        Write-Log "VS Code introuvable, relance manuelle requise." "WARN"
    }
}

function Compare-AndSync {
    param(
        [System.IO.FileInfo]$LocalDb,
        [string]$SharedDir,
        [string]$WorkspaceHash,
        [string]$BackupDir
    )

    $sharedDbPath = Join-Path $SharedDir "${WorkspaceHash}_${DB_FILENAME}"
    $lockPath     = Join-Path $SharedDir "${WorkspaceHash}_${LOCK_FILENAME}"

    # ── Attente et acquisition du verrou ──
    Wait-ForLock -LockPath $lockPath -TimeoutSeconds $LockTimeoutSeconds
    Set-Lock -LockPath $lockPath

    try {
        $effectiveDirection = $Direction

        if ($effectiveDirection -eq "auto") {
            if (-not (Test-Path $sharedDbPath)) {
                Write-Log "[$WorkspaceHash] Pas de fichier partagé → push initial."
                $effectiveDirection = "push"
            } else {
                $localTime  = $LocalDb.LastWriteTimeUtc
                $sharedTime = (Get-Item $sharedDbPath).LastWriteTimeUtc
                Write-Log "[$WorkspaceHash] Local: $localTime | Partagé: $sharedTime"

                if ($localTime -ge $sharedTime) {
                    Write-Log "[$WorkspaceHash] Local plus récent ou égal → push."
                    $effectiveDirection = "push"
                } else {
                    Write-Log "[$WorkspaceHash] Partagé plus récent → pull."
                    $effectiveDirection = "pull"
                }
            }
        }

        switch ($effectiveDirection) {
            "push" {
                # Backup du fichier partagé avant écrasement (si existe)
                if (Test-Path $sharedDbPath) {
                    Invoke-Backup -SourceFile $sharedDbPath -BackupDir $BackupDir -Prefix "shared_${WorkspaceHash}" | Out-Null
                }
                # Backup local
                Invoke-Backup -SourceFile $LocalDb.FullName -BackupDir $BackupDir -Prefix "local_${WorkspaceHash}" | Out-Null
                # Copie locale → partagé
                Copy-Item -Path $LocalDb.FullName -Destination $sharedDbPath -Force
                Write-Log "[$WorkspaceHash] PUSH OK : $($LocalDb.FullName) → $sharedDbPath"
            }
            "pull" {
                if (-not (Test-Path $sharedDbPath)) {
                    Write-Log "[$WorkspaceHash] Aucun fichier partagé à récupérer." "WARN"
                    return
                }
                # Backup local avant écrasement
                Invoke-Backup -SourceFile $LocalDb.FullName -BackupDir $BackupDir -Prefix "local_${WorkspaceHash}" | Out-Null
                # Copie partagé → local
                Copy-Item -Path $sharedDbPath -Destination $LocalDb.FullName -Force
                Write-Log "[$WorkspaceHash] PULL OK : $sharedDbPath → $($LocalDb.FullName)"
            }
        }

        # Vérification d'intégrité : le fichier doit exister et avoir une taille > 0
        $dest = if ($effectiveDirection -eq "push") { $sharedDbPath } else { $LocalDb.FullName }
        $destInfo = Get-Item $dest
        if ($destInfo.Length -eq 0) {
            throw "Fichier de destination vide après copie : $dest"
        }
        Write-Log "[$WorkspaceHash] Intégrité OK — taille: $($destInfo.Length) octets"

    } finally {
        Remove-Lock -LockPath $lockPath
    }
}

# ─────────────────────────────────────────────────────────────────────────────
#  POINT D'ENTRÉE PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────

$exitCode = 0

try {
    Write-Log "═══════════════════════════════════════════════════"
    Write-Log "Sync-CopilotChat v$SCRIPT_VERSION démarré"
    Write-Log "Machine : $env:COMPUTERNAME | Dossier partagé : $SharedFolder"
    Write-Log "Direction : $Direction"

    # 1. Initialiser le dossier partagé
    Initialize-SharedFolder -Path $SharedFolder
    $backupDir = Join-Path $SharedFolder $BACKUP_SUBDIR

    # 2. Fermer VS Code si demandé
    if ($CloseVSCode) {
        Close-VSCode
        Start-Sleep -Seconds 2
    }

    # 3. Trouver tous les state.vscdb locaux
    $localDbs = Get-WorkspaceStoragePaths
    if ($localDbs.Count -eq 0) {
        Write-Log "Aucun fichier state.vscdb trouvé dans workspaceStorage." "WARN"
    } else {
        Write-Log "Fichiers détectés : $($localDbs.Count)"
    }

    # 4. Synchroniser chaque workspace
    foreach ($db in $localDbs) {
        # Le hash du workspace = nom du dossier parent
        $workspaceHash = $db.Directory.Name
        Write-Log "─── Workspace : $workspaceHash ───"
        try {
            Compare-AndSync -LocalDb $db -SharedDir $SharedFolder `
                            -WorkspaceHash $workspaceHash -BackupDir $backupDir
        } catch {
            Write-Log "Erreur sur workspace $workspaceHash : $_" "ERROR"
            $exitCode = 1
        }
    }

    # 5. Relancer VS Code si demandé
    if ($LaunchVSCode) {
        Start-VSCode
    }

    Write-Log "Synchronisation terminée. Code de sortie : $exitCode"
    Write-Log "═══════════════════════════════════════════════════"

} catch {
    Write-Log "ERREUR FATALE : $_" "ERROR"
    $exitCode = 2
}

exit $exitCode
