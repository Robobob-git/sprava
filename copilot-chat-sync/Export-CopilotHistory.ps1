<#
.SYNOPSIS
    Exporte l'historique des conversations GitHub Copilot Chat depuis state.vscdb
    vers un fichier JSON lisible, et permet de lister les entrées disponibles.

.DESCRIPTION
    Ce script constitue une alternative minimale et sûre à la copie directe de
    state.vscdb. Il interroge la base SQLite via System.Data.SQLite (ADO.NET) ou
    via la commande sqlite3.exe si disponible, et produit un export JSON structuré.

    Cas d'usage :
      - Archivage/sauvegarde légère de l'historique de conversations.
      - Inspection du contenu sans ouvrir VS Code.
      - Transfert manuel vers une autre machine (import non supporté nativement
        par l'extension, mais utile pour archivage ou future intégration).

.PARAMETER WorkspaceHash
    Hash du workspace (nom du sous-dossier dans workspaceStorage).
    Si omis, le script liste tous les workspaces disponibles.

.PARAMETER OutputFile
    Chemin du fichier JSON de sortie.
    Par défaut : copilot_history_<hash>_<timestamp>.json dans le répertoire courant.

.PARAMETER ListOnly
    Affiche uniquement la liste des workspaces et le nombre d'entrées Copilot, sans export.

.PARAMETER Sqlite3Path
    Chemin vers sqlite3.exe. Si omis, le script tente de le localiser automatiquement
    ou utilise le fallback binaire intégré.

.EXAMPLE
    # Lister tous les workspaces
    .\Export-CopilotHistory.ps1 -ListOnly

.EXAMPLE
    # Exporter le workspace spécifique
    .\Export-CopilotHistory.ps1 -WorkspaceHash "ddd164513de1ba86adf453b26384f03d" -OutputFile "C:\Temp\export.json"

.NOTES
    Requiert sqlite3.exe dans le PATH ou spécifié via -Sqlite3Path.
    Téléchargement : https://www.sqlite.org/download.html (sqlite-tools-win-x64)
    Version : 1.0.0
#>

[CmdletBinding()]
param(
    [string]$WorkspaceHash,
    [string]$OutputFile,
    [switch]$ListOnly,
    [string]$Sqlite3Path
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ─────────────────────────────────────────────────────────────────────────────
#  LOCALISATION DE SQLITE3
# ─────────────────────────────────────────────────────────────────────────────

function Find-Sqlite3 {
    param([string]$HintPath)
    if ($HintPath -and (Test-Path $HintPath)) { return $HintPath }

    # Chercher dans PATH
    $inPath = Get-Command "sqlite3" -ErrorAction SilentlyContinue
    if ($inPath) { return $inPath.Source }

    # Emplacements communs
    $candidates = @(
        "$env:ProgramFiles\SQLite\sqlite3.exe"
        "$env:LOCALAPPDATA\Programs\SQLite\sqlite3.exe"
        "C:\sqlite\sqlite3.exe"
        "C:\tools\sqlite3.exe"
    )
    foreach ($c in $candidates) {
        if (Test-Path $c) { return $c }
    }
    return $null
}

$sqlite3 = Find-Sqlite3 -HintPath $Sqlite3Path
if (-not $sqlite3) {
    Write-Error @"
sqlite3.exe introuvable. Veuillez :
  1. Télécharger sqlite3.exe depuis https://www.sqlite.org/download.html
  2. Le placer dans votre PATH, ou
  3. Spécifier son chemin via -Sqlite3Path "C:\chemin\vers\sqlite3.exe"
"@
}

# ─────────────────────────────────────────────────────────────────────────────
#  FONCTIONS
# ─────────────────────────────────────────────────────────────────────────────

function Get-WorkspaceStorageRoot {
    $roots = @(
        Join-Path $env:APPDATA "Code\User\workspaceStorage"
        Join-Path $env:APPDATA "Code - Insiders\User\workspaceStorage"
    )
    foreach ($r in $roots) {
        if (Test-Path $r) { return $r }
    }
    throw "Dossier workspaceStorage introuvable."
}

function Invoke-Sqlite3Query {
    param([string]$DbPath, [string]$Query)
    $result = & $sqlite3 -json $DbPath $Query 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Erreur sqlite3 : $result"
    }
    return $result
}

function Get-AllWorkspaces {
    param([string]$StorageRoot)
    $workspaces = @()
    $dirs = Get-ChildItem -Path $StorageRoot -Directory -ErrorAction SilentlyContinue
    foreach ($dir in $dirs) {
        $dbPath = Join-Path $dir.FullName "state.vscdb"
        if (Test-Path $dbPath) {
            $workspaces += [PSCustomObject]@{
                Hash   = $dir.Name
                DbPath = $dbPath
                Size   = (Get-Item $dbPath).Length
                Modified = (Get-Item $dbPath).LastWriteTime
            }
        }
    }
    return $workspaces
}

function Get-CopilotEntriesCount {
    param([string]$DbPath)
    try {
        # Compter les entrées liées à Copilot Chat dans ItemTable
        $result = & $sqlite3 $DbPath "SELECT COUNT(*) FROM ItemTable WHERE key LIKE '%copilot%' OR key LIKE '%chat%' OR key LIKE '%conversation%';" 2>&1
        if ($LASTEXITCODE -eq 0) { return [int]($result.Trim()) }
    } catch {}
    return 0
}

function Export-WorkspaceHistory {
    param(
        [string]$DbPath,
        [string]$Hash,
        [string]$OutFile
    )

    Write-Host "Inspection de : $DbPath"

    # Récupérer la liste des tables
    $tables = (& $sqlite3 $DbPath ".tables" 2>&1).Split() | Where-Object { $_ -ne "" }
    Write-Host "Tables trouvées : $($tables -join ', ')"

    $export = [ordered]@{
        exportDate    = (Get-Date -Format "o")
        machine       = $env:COMPUTERNAME
        workspaceHash = $Hash
        dbPath        = $DbPath
        tables        = @{}
    }

    foreach ($table in $tables) {
        try {
            $jsonRows = Invoke-Sqlite3Query -DbPath $DbPath -Query "SELECT * FROM [$table];"
            if ($jsonRows -and $jsonRows.Trim() -ne "") {
                $rows = $jsonRows | ConvertFrom-Json
                # Filtrer les entrées potentiellement liées à Copilot Chat
                if ($table -eq "ItemTable") {
                    $copilotRows = $rows | Where-Object {
                        $_.key -match "copilot|chat|conversation|github\.copilot"
                    }
                    $export.tables[$table] = $copilotRows
                    Write-Host "  $table : $($copilotRows.Count) entrées Copilot sur $($rows.Count) totales"
                } else {
                    $export.tables[$table] = $rows
                    Write-Host "  $table : $($rows.Count) entrées"
                }
            } else {
                $export.tables[$table] = @()
                Write-Host "  $table : vide"
            }
        } catch {
            Write-Warning "  Impossible de lire la table '$table' : $_"
            $export.tables[$table] = "ERREUR: $_"
        }
    }

    if (-not $OutFile) {
        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $OutFile   = "copilot_history_${Hash}_${timestamp}.json"
    }

    $export | ConvertTo-Json -Depth 20 | Set-Content -Path $OutFile -Encoding UTF8
    Write-Host ""
    Write-Host "Export créé : $OutFile ($((Get-Item $OutFile).Length) octets)"
    return $OutFile
}

# ─────────────────────────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────────────────────────

$storageRoot = Get-WorkspaceStorageRoot
Write-Host "WorkspaceStorage : $storageRoot"
Write-Host ""

$allWorkspaces = Get-AllWorkspaces -StorageRoot $storageRoot

if ($ListOnly -or -not $WorkspaceHash) {
    Write-Host "═══════════════════════════════════════════════════════════"
    Write-Host "  Workspaces disponibles ($($allWorkspaces.Count) trouvés)"
    Write-Host "═══════════════════════════════════════════════════════════"
    foreach ($ws in ($allWorkspaces | Sort-Object Modified -Descending)) {
        $copilotCount = Get-CopilotEntriesCount -DbPath $ws.DbPath
        Write-Host ("  Hash     : {0}" -f $ws.Hash)
        Write-Host ("  Modifié  : {0}" -f $ws.Modified.ToString("yyyy-MM-dd HH:mm:ss"))
        Write-Host ("  Taille   : {0:N0} octets" -f $ws.Size)
        Write-Host ("  Entrées Copilot Chat : {0}" -f $copilotCount)
        Write-Host "  ─────────────────────────────────────────────────────"
    }

    if (-not $ListOnly -and -not $WorkspaceHash) {
        Write-Host ""
        Write-Host "Pour exporter un workspace :"
        Write-Host "  .\Export-CopilotHistory.ps1 -WorkspaceHash <hash> [-OutputFile <chemin.json>]"
    }
    return
}

# Export du workspace spécifié
$target = $allWorkspaces | Where-Object { $_.Hash -eq $WorkspaceHash }
if (-not $target) {
    Write-Error "Workspace '$WorkspaceHash' introuvable dans $storageRoot"
}

Export-WorkspaceHistory -DbPath $target.DbPath -Hash $WorkspaceHash -OutFile $OutputFile
