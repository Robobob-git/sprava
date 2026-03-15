<#
.SYNOPSIS
    Crée une tâche planifiée Windows pour automatiser la synchronisation
    des sessions GitHub Copilot Chat au démarrage/fermeture de session Windows.

.DESCRIPTION
    Ce script configure deux tâches planifiées :
      1. "CopilotChatSync-Logon"  : exécute Sync-CopilotChat.ps1 -Direction pull
         à chaque ouverture de session Windows (pour récupérer la dernière version).
      2. "CopilotChatSync-Logoff" : exécute Sync-CopilotChat.ps1 -Direction push
         à chaque fermeture de session Windows (pour sauvegarder avant de partir).

    Requiert des droits administrateur pour créer les tâches planifiées.

.PARAMETER SharedFolder
    Chemin vers le dossier partagé (identique à celui utilisé dans Sync-CopilotChat.ps1).

.PARAMETER SyncScriptPath
    Chemin complet vers Sync-CopilotChat.ps1.
    Par défaut : même dossier que ce script.

.PARAMETER Uninstall
    Si présent, supprime les tâches planifiées créées par ce script.

.EXAMPLE
    # Installer les tâches planifiées (en tant qu'administrateur)
    .\Install-SyncTask.ps1 -SharedFolder "C:\Users\Bob\OneDrive\CopilotSync"

.EXAMPLE
    # Désinstaller
    .\Install-SyncTask.ps1 -SharedFolder "C:\Users\Bob\OneDrive\CopilotSync" -Uninstall

.NOTES
    Nécessite PowerShell 5.1+ et le module ScheduledTasks (inclus dans Windows 8+).
#>

[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory)]
    [string]$SharedFolder,

    [string]$SyncScriptPath,

    [switch]$Uninstall
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$TASK_NAME_LOGON  = "CopilotChatSync-Logon"
$TASK_NAME_LOGOFF = "CopilotChatSync-Logoff"
$TASK_FOLDER      = "\CopilotChat"

if (-not $SyncScriptPath) {
    $SyncScriptPath = Join-Path $PSScriptRoot "Sync-CopilotChat.ps1"
}

function Remove-SyncTasks {
    foreach ($taskName in @($TASK_NAME_LOGON, $TASK_NAME_LOGOFF)) {
        $fullPath = "$TASK_FOLDER\$taskName"
        try {
            Unregister-ScheduledTask -TaskPath $TASK_FOLDER -TaskName $taskName -Confirm:$false -ErrorAction Stop
            Write-Host "Tâche supprimée : $fullPath"
        } catch {
            Write-Warning "Tâche '$fullPath' introuvable ou déjà supprimée."
        }
    }
    # Supprimer le dossier de tâches s'il est vide
    try {
        $scheduler = New-Object -ComObject Schedule.Service
        $scheduler.Connect()
        $folder = $scheduler.GetFolder($TASK_FOLDER)
        if ($folder.GetTasks(0).Count -eq 0) {
            $root = $scheduler.GetFolder("\")
            $root.DeleteFolder($TASK_FOLDER, 0)
            Write-Host "Dossier de tâches '$TASK_FOLDER' supprimé."
        }
    } catch {
        # Ignore si le dossier n'existe pas
    }
}

function Register-SyncTask {
    param(
        [string]$TaskName,
        [string]$Direction,
        [string]$TriggerType   # "Logon" ou "SessionStateChange"
    )

    $psExe  = "powershell.exe"
    $args   = "-NonInteractive -WindowStyle Hidden -ExecutionPolicy Bypass " +
              "-File `"$SyncScriptPath`" " +
              "-SharedFolder `"$SharedFolder`" " +
              "-Direction $Direction"

    $action  = New-ScheduledTaskAction -Execute $psExe -Argument $args

    if ($TriggerType -eq "Logon") {
        $trigger = New-ScheduledTaskTrigger -AtLogOn -User "$env:USERDOMAIN\$env:USERNAME"
    } else {
        # Fermeture de session : utiliser un Event Trigger sur l'ID 4647 (déconnexion utilisateur).
        # Note : Windows ne fournit pas de déclencheur natif "at logoff" via New-ScheduledTaskTrigger.
        $trigger = New-CimInstance -Namespace ROOT\Microsoft\Windows\TaskScheduler `
            -ClassName MSFT_TaskEventTrigger `
            -ClientOnly `
            -Property @{
                Enabled       = $true
                Subscription  = "<QueryList><Query Id='0' Path='Security'>" +
                                "<Select Path='Security'>*[System[EventID=4647]]</Select>" +
                                "</Query></QueryList>"
            }
    }

    $principal = New-ScheduledTaskPrincipal `
        -UserId "$env:USERDOMAIN\$env:USERNAME" `
        -LogonType Interactive `
        -RunLevel Highest

    $settings = New-ScheduledTaskSettingsSet `
        -ExecutionTimeLimit (New-TimeSpan -Minutes 5) `
        -MultipleInstances IgnoreNew `
        -StartWhenAvailable

    $task = New-ScheduledTask -Action $action -Trigger $trigger `
                               -Principal $principal -Settings $settings `
                               -Description "Synchronise les sessions Copilot Chat ($Direction) — direction: $Direction"

    # Créer le dossier de tâches si nécessaire
    try {
        $scheduler = New-Object -ComObject Schedule.Service
        $scheduler.Connect()
        $root = $scheduler.GetFolder("\")
        try { $root.GetFolder($TASK_FOLDER) } catch {
            $root.CreateFolder($TASK_FOLDER) | Out-Null
            Write-Host "Dossier de tâches créé : $TASK_FOLDER"
        }
    } catch {
        Write-Warning "Impossible de créer le dossier de tâches COM : $_"
    }

    Register-ScheduledTask `
        -TaskName $TaskName `
        -TaskPath $TASK_FOLDER `
        -InputObject $task `
        -Force | Out-Null

    Write-Host "Tâche créée : $TASK_FOLDER\$TaskName (direction: $Direction)"
}

# ─────────────────────────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────────────────────────

# Vérifier les droits administrateur
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
    [Security.Principal.WindowsBuiltInRole]"Administrator"
)
if (-not $isAdmin) {
    Write-Error "Ce script nécessite des droits administrateur. Relancez en tant qu'administrateur."
}

if (-not (Test-Path $SyncScriptPath)) {
    Write-Error "Script de sync introuvable : $SyncScriptPath"
}

if ($Uninstall) {
    Write-Host "Désinstallation des tâches planifiées Copilot Chat Sync..."
    Remove-SyncTasks
    Write-Host "Désinstallation terminée."
} else {
    Write-Host "Installation des tâches planifiées Copilot Chat Sync..."
    Write-Host "  Dossier partagé : $SharedFolder"
    Write-Host "  Script          : $SyncScriptPath"

    # Tâche 1 : Pull au logon
    Register-SyncTask -TaskName $TASK_NAME_LOGON -Direction "pull" -TriggerType "Logon"

    # Tâche 2 : Push au logoff (Event Trigger Security 4647)
    Register-SyncTask -TaskName $TASK_NAME_LOGOFF -Direction "push" -TriggerType "SessionStateChange"

    Write-Host ""
    Write-Host "Installation terminée. Pour tester manuellement :"
    Write-Host "  Pull  : Start-ScheduledTask -TaskPath '$TASK_FOLDER' -TaskName '$TASK_NAME_LOGON'"
    Write-Host "  Push  : Start-ScheduledTask -TaskPath '$TASK_FOLDER' -TaskName '$TASK_NAME_LOGOFF'"
}
