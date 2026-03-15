# Copilot Chat Session Sync — Guide complet

> **Objectif** : synchroniser automatiquement l'historique des conversations
> GitHub Copilot Chat entre plusieurs machines Windows (et partiellement macOS/Linux).

---

## Table des matières

1. [Diagnostic : pourquoi state.vscdb n'est pas partagé](#1-diagnostic)
2. [Options disponibles (classées par préférence)](#2-options)
3. [Option 1 — Dossier partagé + scripts PowerShell (recommandé)](#3-option-1)
4. [Option 2 — Symlink / Junction vers OneDrive](#4-option-2)
5. [Gestion des conflits](#5-gestion-des-conflits)
6. [Sécurité et confidentialité](#6-securite)
7. [Feature request pour l'extension](#7-feature-request)
8. [Checklist de vérification post-implémentation](#8-checklist)
9. [Alternatives manuelles minimales](#9-alternatives-manuelles)
10. [Adaptation macOS / Linux](#10-macos-linux)

---

## 1. Diagnostic

### Pourquoi `state.vscdb` n'est-il pas partagé par défaut ?

| Cause | Détail |
|-------|--------|
| **Hash de workspace** | Le sous-dossier dans `workspaceStorage` est nommé d'après un hash SHA1 du chemin absolu du workspace sur la machine. Deux machines avec des chemins différents (`C:\Users\Alice\projet` vs `D:\travail\projet`) produisent des hashes différents → les données ne se trouvent jamais au même endroit. |
| **Scope de stockage** | `workspaceStorage` est délibérément local par VS Code. Il n'est ni versionné, ni sync, ni sauvegardé. |
| **Limites de Settings Sync** | VS Code Settings Sync synchronise : extensions, keybindings, snippets, settings, profiles. Il n'inclut **pas** `workspaceStorage`, `globalStorage` (sauf si l'extension l'active explicitement via `setKeysForSync`), ni les caches locaux. |
| **Absence d'API export/import** | L'extension `github.copilot-chat` ne propose pas (à ce jour) de fonctionnalité d'export ou de sync cloud des sessions. |

### Implications pratiques

- Un historique de conversation sur le PC portable est **invisible** sur le PC fixe.
- Copier manuellement `state.vscdb` peut corrompre la base si VS Code est ouvert.
- Il n'existe pas de mapping automatique entre les hashes de workspace entre deux machines.

---

## 2. Options disponibles

| Rang | Option | Avantages | Inconvénients |
|------|--------|-----------|---------------|
| ⭐ 1 | **Scripts PowerShell + dossier partagé OneDrive/réseau** | Automatique, contrôlé, backup intégré, Windows natif | Requiert OneDrive ou partage réseau |
| ⭐ 2 | **Symlink/Junction `workspaceStorage` → OneDrive** | Transparent pour VS Code, zéro effort après setup | Risque de conflit si les deux machines écrivent simultanément; hash toujours différent |
| 3 | **Settings Sync natif (si extension le supporte)** | Intégré, chiffré, aucun outil tiers | Non supporté actuellement par `github.copilot-chat` |
| 4 | **Export JSON via sqlite3 + import manuel** | Sûr, lisible, portable | Manuel, pas de sync automatique |
| 5 | **Copie manuelle de state.vscdb** | Simple | Risque de corruption, pénible à maintenir |

---

## 3. Option 1 — Scripts PowerShell + dossier partagé (recommandé)

### Prérequis

- Windows 10/11, PowerShell 5.1 ou 7+
- Un dossier partagé accessible sur les deux machines :
  - **OneDrive** (recommandé) : `C:\Users\<Nom>\OneDrive\CopilotChatSync`
  - **Partage réseau** : `\\serveur\partage\CopilotChatSync`
  - **Dropbox/Google Drive** : tout chemin local synchronisé

### Scripts disponibles

| Script | Rôle |
|--------|------|
| [`Sync-CopilotChat.ps1`](./Sync-CopilotChat.ps1) | Script principal : backup, verrou, push/pull, log |
| [`Install-SyncTask.ps1`](./Install-SyncTask.ps1) | Configure les tâches planifiées Windows |
| [`Export-CopilotHistory.ps1`](./Export-CopilotHistory.ps1) | Export JSON de l'historique (alternative légère) |

### Plan d'implémentation étape par étape

#### Étape 1 — Choisir et préparer le dossier partagé

```powershell
# Option OneDrive (recommandé)
# Note : le chemin OneDrive par défaut est indiqué ci-dessous. Si vous avez
# configuré un emplacement personnalisé, ajustez le chemin en conséquence.
# Vous pouvez vérifier votre chemin réel avec : (Get-ItemProperty "HKCU:\Software\Microsoft\OneDrive").UserFolder
$shared = "$env:USERPROFILE\OneDrive\CopilotChatSync"
New-Item -ItemType Directory -Path $shared -Force
```

#### Étape 2 — Tester le script de sync manuellement

```powershell
# Depuis le dossier copilot-chat-sync du projet
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# Premier test en mode "push" (envoie depuis ce PC)
.\Sync-CopilotChat.ps1 -SharedFolder "$env:USERPROFILE\OneDrive\CopilotChatSync" -Direction push -Verbose

# Vérifier le log
Get-Content "$env:USERPROFILE\OneDrive\CopilotChatSync\sync.log" -Tail 20
```

#### Étape 3 — Tester le pull sur la deuxième machine

```powershell
# Sur l'autre machine (après que OneDrive a synchronisé)
.\Sync-CopilotChat.ps1 -SharedFolder "$env:USERPROFILE\OneDrive\CopilotChatSync" -Direction pull
```

#### Étape 4 — Automatiser via tâches planifiées (droits admin requis)

```powershell
# Ouvrir PowerShell en tant qu'administrateur, puis :
.\Install-SyncTask.ps1 -SharedFolder "$env:USERPROFILE\OneDrive\CopilotChatSync"

# Vérifier les tâches créées
Get-ScheduledTask -TaskPath "\CopilotChat\"
```

#### Étape 5 — Configurer la deuxième machine

Répéter les étapes 2, 3, et 4 sur chaque machine supplémentaire.

### Usage courant du script principal

```powershell
# Sync automatique (compare les timestamps, choisit push ou pull)
.\Sync-CopilotChat.ps1 -SharedFolder "C:\Users\Bob\OneDrive\CopilotSync"

# Fermer VS Code, sync, relancer
.\Sync-CopilotChat.ps1 -SharedFolder "C:\Users\Bob\OneDrive\CopilotSync" `
    -CloseVSCode -LaunchVSCode

# Forcer un push (envoyer la version locale)
.\Sync-CopilotChat.ps1 -SharedFolder "C:\Users\Bob\OneDrive\CopilotSync" -Direction push

# Forcer un pull (récupérer la version partagée)
.\Sync-CopilotChat.ps1 -SharedFolder "C:\Users\Bob\OneDrive\CopilotSync" -Direction pull
```

### Paramètres du script principal

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `-SharedFolder` | String | **requis** | Dossier partagé source/destination |
| `-Direction` | `push\|pull\|auto` | `auto` | Sens de la synchronisation |
| `-CloseVSCode` | Switch | off | Ferme VS Code avant la sync |
| `-LaunchVSCode` | Switch | off | Relance VS Code après la sync |
| `-MaxBackups` | Int | 10 | Nombre de backups horodatés à conserver |
| `-LockTimeoutSeconds` | Int | 30 | Timeout pour l'acquisition du verrou |
| `-LogFile` | String | `<SharedFolder>\sync.log` | Fichier de journal |

### Structure du dossier partagé après synchronisation

```
OneDrive\CopilotChatSync\
├── sync.log                                        ← journal des opérations
├── <hash1>_state.vscdb                             ← base de données workspace 1
├── <hash1>_sync.lock                               ← verrou (temporaire)
├── <hash2>_state.vscdb                             ← base de données workspace 2
└── backups\
    ├── local_<hash1>_PC-PORTABLE_20260315_143000.vscdb
    ├── shared_<hash1>_PC-FIXE_20260315_143500.vscdb
    └── ...
```

---

## 4. Option 2 — Symlink / Junction vers OneDrive

> ⚠️ **Attention** : cette option redirige l'intégralité de `workspaceStorage`
> vers le cloud. Le hash de workspace reste différent entre machines, donc les
> sessions ne seront pas automatiquement partagées. Cette option est utile
> principalement pour la **sauvegarde automatique**, pas pour la sync cross-machine.

```powershell
# ATTENTION : fermer VS Code avant d'exécuter ces commandes
# Sauvegarder d'abord
$src  = "$env:APPDATA\Code\User\workspaceStorage"
$dest = "$env:USERPROFILE\OneDrive\VSCode-WorkspaceStorage"

# Déplacer le dossier existant
Move-Item $src $dest

# Créer un junction (lien symbolique de répertoire, ne nécessite pas de droits admin)
cmd /c "mklink /J `"$src`" `"$dest`""
```

**Limitation** : Les deux machines synchronisent leurs `workspaceStorage` respectifs
vers OneDrive, mais les hashes restent différents. Il faudrait combiner cette
approche avec `Sync-CopilotChat.ps1` pour copier les fichiers entre les deux hashes.

---

## 5. Gestion des conflits

### Stratégie recommandée : last-write-wins + verrou sémaphore

Le script `Sync-CopilotChat.ps1` implémente :

1. **Verrou fichier sémaphore** (`<hash>_sync.lock`) : empêche deux machines de
   modifier le fichier partagé simultanément. Contient le nom de machine, PID,
   et timestamp.

2. **Détection de verrou périmé** : si un verrou existe depuis plus de 5 minutes
   (VS Code crashé, machine éteinte en plein sync), il est supprimé automatiquement.

3. **Stratégie last-write-wins** : la version avec le `LastWriteTime` UTC le plus
   récent "gagne". Avant toute opération, un backup horodaté est créé.

4. **Backup de rotation** : les anciens backups sont supprimés après `MaxBackups`
   itérations pour éviter d'occuper trop d'espace.

### Cas limite : modification simultanée

Si les deux machines modifient `state.vscdb` pendant que OneDrive synchronise :

- La version locale la plus récente sera envoyée en `push`.
- L'ancienne version est sauvegardée dans `backups/`.
- **Récupération manuelle** : consulter `backups/` et copier la version souhaitée.

### Alternative manuelle si conflit détecté

```powershell
# Inspecter les backups
Get-ChildItem "$env:USERPROFILE\OneDrive\CopilotSync\backups" |
    Sort-Object LastWriteTime -Descending | Select-Object -First 10

# Restaurer une version spécifique
$backup = "C:\Users\Bob\OneDrive\CopilotSync\backups\local_abc123_PC-FIXE_20260315_143000.vscdb"
$dest   = "$env:APPDATA\Code\User\workspaceStorage\abc123\state.vscdb"
Copy-Item $backup $dest -Force
```

---

## 6. Sécurité et confidentialité

| Aspect | Recommandation |
|--------|----------------|
| **Chiffrement en transit** | OneDrive/Dropbox chiffrent les fichiers en transit (TLS). Pour un partage réseau interne, utiliser SMB avec chiffrement activé. |
| **Chiffrement au repos** | Activer le chiffrement OneDrive Personal Vault ou BitLocker pour le dossier de sync. |
| **Permissions du dossier partagé** | Restreindre le dossier partagé à votre seul compte utilisateur (`icacls`). |
| **Contenu sensible** | Les conversations Copilot peuvent contenir du code propriétaire ou des données personnelles. Ne jamais utiliser un stockage cloud public non chiffré. |
| **Backups** | Les backups locaux (`backups/`) sont stockés dans OneDrive — s'assurer que OneDrive lui-même est protégé par MFA. |

```powershell
# Restreindre les permissions du dossier partagé à l'utilisateur courant uniquement
$path = "$env:USERPROFILE\OneDrive\CopilotChatSync"
$acl  = Get-Acl $path
$acl.SetAccessRuleProtection($true, $false)
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
    "$env:USERDOMAIN\$env:USERNAME", "FullControl", "ContainerInherit,ObjectInherit",
    "None", "Allow"
)
$acl.SetAccessRule($rule)
Set-Acl -Path $path -AclObject $acl
```

---

## 7. Feature request pour l'extension

Le fichier [`feature-request.md`](./feature-request.md) contient un texte
prêt à poster comme issue GitHub sur le dépôt `microsoft/vscode-copilot-chat`
ou `github/copilot`.

**Instructions pour poster :**

1. Ouvrir [https://github.com/microsoft/vscode-copilot-chat/issues/new](https://github.com/microsoft/vscode-copilot-chat/issues/new)
   (ou le dépôt officiel de l'extension).
2. Copier le contenu de `feature-request.md`.
3. Adapter les informations de version à votre environnement.
4. Soumettre l'issue.

---

## 8. Checklist de vérification post-implémentation

### Vérification initiale (Machine A — push)

```powershell
# 1. Vérifier que le script s'est exécuté sans erreur
Get-Content "$env:USERPROFILE\OneDrive\CopilotSync\sync.log" -Tail 30

# 2. Vérifier que les fichiers partagés existent
Get-ChildItem "$env:USERPROFILE\OneDrive\CopilotSync" -Filter "*.vscdb"

# 3. Vérifier la taille (doit être > 0 et identique à la source)
$shared = Get-Item "$env:USERPROFILE\OneDrive\CopilotSync\<hash>_state.vscdb"
$local  = Get-Item "$env:APPDATA\Code\User\workspaceStorage\<hash>\state.vscdb"
Write-Host "Partagé: $($shared.Length) | Local: $($local.Length)"
# Les deux tailles doivent être identiques après un push récent

# 4. Vérifier que les backups sont créés
Get-ChildItem "$env:USERPROFILE\OneDrive\CopilotSync\backups" | Sort-Object LastWriteTime -Descending | Select-Object -First 5
```

### Vérification sur Machine B (pull)

```powershell
# 5. Attendre que OneDrive synchronise (ou forcer la sync OneDrive)
# 6. Exécuter le pull
.\Sync-CopilotChat.ps1 -SharedFolder "$env:USERPROFILE\OneDrive\CopilotSync" -Direction pull

# 7. Vérifier que le fichier local a été mis à jour
$local = Get-Item "$env:APPDATA\Code\User\workspaceStorage\*\state.vscdb" |
         Sort-Object LastWriteTime -Descending | Select-Object -First 1
Write-Host "Dernière modification locale : $($local.LastWriteTime)"

# 8. Ouvrir VS Code et vérifier l'onglet "Chat" de Copilot
# Les conversations de Machine A doivent apparaître
```

### Test de conflit simulé

```powershell
# Simuler un verrou périmé
Set-Content "$env:USERPROFILE\OneDrive\CopilotSync\<hash>_sync.lock" "TEST_MACHINE | PID:9999 | 2000-01-01T00:00:00"
# Exécuter le script → doit détecter le verrou périmé et le supprimer automatiquement
.\Sync-CopilotChat.ps1 -SharedFolder "$env:USERPROFILE\OneDrive\CopilotSync" -Direction auto
# Vérifier dans le log : "Verrou périmé détecté, suppression forcée."
```

### Vérification des tâches planifiées

```powershell
# Lister les tâches
Get-ScheduledTask -TaskPath "\CopilotChat\" | Select-Object TaskName, State

# Tester manuellement la tâche de pull (logon)
Start-ScheduledTask -TaskPath "\CopilotChat\" -TaskName "CopilotChatSync-Logon"
Start-Sleep -Seconds 5
Get-Content "$env:USERPROFILE\OneDrive\CopilotSync\sync.log" -Tail 10
```

---

## 9. Alternatives manuelles minimales

### Alternative 1 — Copie directe one-shot

```powershell
# FERMER VS CODE AVANT
$src  = "$env:APPDATA\Code\User\workspaceStorage\<hash_source>\state.vscdb"
$dest = "$env:APPDATA\Code\User\workspaceStorage\<hash_destination>\state.vscdb"

# Backup de sécurité
Copy-Item $dest "${dest}.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"

# Copie
Copy-Item $src $dest -Force
Write-Host "Copie effectuée."
```

### Alternative 2 — Export SQLite vers JSON (recommandé pour archivage)

Utiliser [`Export-CopilotHistory.ps1`](./Export-CopilotHistory.ps1) :

```powershell
# Lister les workspaces disponibles
.\Export-CopilotHistory.ps1 -ListOnly

# Exporter un workspace spécifique
.\Export-CopilotHistory.ps1 -WorkspaceHash "ddd164513de1ba86adf453b26384f03d" `
    -OutputFile "C:\Temp\copilot_export.json"
```

> **Note** : l'import d'un export JSON dans VS Code n'est pas supporté nativement.
> Cet export est utile pour archivage, audit, ou en attendant qu'une future version
> de l'extension supporte l'import.

### Alternative 3 — Robocopy planifié (simple)

```powershell
# Script minimaliste à ajouter dans le Planificateur de tâches
$src  = "$env:APPDATA\Code\User\workspaceStorage"
$dest = "$env:USERPROFILE\OneDrive\CopilotSync\workspaceStorage"
robocopy $src $dest "state.vscdb" /S /COPYALL /R:3 /W:5 /LOG+:"$dest\robocopy.log"
```

---

## 10. Adaptation macOS / Linux

### macOS

Remplacer les chemins Windows :

| Windows | macOS |
|---------|-------|
| `%APPDATA%\Code\User\workspaceStorage` | `~/Library/Application Support/Code/User/workspaceStorage` |
| `OneDrive` | `iCloud Drive` ou `Dropbox` |
| Tâches planifiées | `launchd` plist dans `~/Library/LaunchAgents/` |

**Script bash équivalent (macOS/Linux) :**

```bash
#!/usr/bin/env bash
# sync-copilot-chat.sh — Version macOS/Linux

SHARED_FOLDER="$HOME/Library/Mobile Documents/com~apple~CloudDocs/CopilotChatSync"
STORAGE_ROOT="$HOME/Library/Application Support/Code/User/workspaceStorage"
DIRECTION="${1:-auto}"   # push, pull, auto
LOG_FILE="$SHARED_FOLDER/sync.log"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')][$1] $2" | tee -a "$LOG_FILE"; }

mkdir -p "$SHARED_FOLDER/backups"

for db in "$STORAGE_ROOT"/*/state.vscdb; do
    hash=$(basename "$(dirname "$db")")
    shared_db="$SHARED_FOLDER/${hash}_state.vscdb"
    lock_file="$SHARED_FOLDER/${hash}_sync.lock"
    backup_prefix="$SHARED_FOLDER/backups/${hash}_$(hostname)_$(date +%Y%m%d_%H%M%S)"

    # Acquérir le verrou
    if [ -f "$lock_file" ]; then
        log "WARN" "[$hash] Verrou présent, attente..."
        sleep 5
        if [ -f "$lock_file" ]; then
            # Vérifier si périmé (> 5 min)
            if [ "$(find "$lock_file" -mmin +5)" ]; then
                log "WARN" "[$hash] Verrou périmé, suppression."
                rm -f "$lock_file"
            else
                log "ERROR" "[$hash] Impossible d'acquérir le verrou."
                continue
            fi
        fi
    fi
    echo "$(hostname) PID:$$ $(date -Iseconds)" > "$lock_file"

    dir="$DIRECTION"
    if [ "$dir" = "auto" ]; then
        if [ ! -f "$shared_db" ]; then
            dir="push"
        elif [ "$db" -nt "$shared_db" ]; then
            dir="push"
        else
            dir="pull"
        fi
    fi

    if [ "$dir" = "push" ]; then
        [ -f "$shared_db" ] && cp "$shared_db" "${backup_prefix}_shared.vscdb"
        cp "$db" "${backup_prefix}_local.vscdb"
        cp "$db" "$shared_db"
        log "INFO" "[$hash] PUSH OK"
    elif [ "$dir" = "pull" ]; then
        [ -f "$shared_db" ] || { log "WARN" "[$hash] Pas de fichier partagé."; rm -f "$lock_file"; continue; }
        cp "$db" "${backup_prefix}_local.vscdb"
        cp "$shared_db" "$db"
        log "INFO" "[$hash] PULL OK"
    fi

    rm -f "$lock_file"
done

log "INFO" "Sync terminée."
```

**Automatisation avec launchd (macOS) :**

```xml
<!-- ~/Library/LaunchAgents/com.user.copilot-chat-sync.plist -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.copilot-chat-sync</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>/path/to/sync-copilot-chat.sh</string>
        <string>auto</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/copilot-sync.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/copilot-sync-err.log</string>
</dict>
</plist>
```

```bash
# Activer le launchd agent
launchctl load ~/Library/LaunchAgents/com.user.copilot-chat-sync.plist
```

**Automatisation avec systemd (Linux) :**

```ini
# ~/.config/systemd/user/copilot-chat-sync.service
[Unit]
Description=Copilot Chat Session Sync

[Service]
Type=oneshot
ExecStart=/bin/bash /path/to/sync-copilot-chat.sh auto

[Install]
WantedBy=default.target
```

```bash
systemctl --user enable --now copilot-chat-sync.service
```

---

## Licence

Ces scripts sont fournis sous licence MIT. Voir le dépôt principal pour les détails.
