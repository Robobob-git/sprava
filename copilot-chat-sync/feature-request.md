---
name: "Feature Request: Cloud synchronization of Copilot Chat sessions via GitHub account"
about: Allow Copilot Chat conversation history to be synchronized across machines using the authenticated GitHub account
labels: enhancement, feature-request, sync
---

# Feature Request: Cloud Sync of Copilot Chat Sessions (Cross-Machine)

## Summary

Add an option for GitHub Copilot Chat to synchronize conversation history across
multiple machines using the user's authenticated GitHub account (or a chosen cloud
storage), similar to how VS Code Settings Sync works for extensions and preferences.

---

## Problem

Copilot Chat conversations (sessions) are stored **locally** in a SQLite database
(`state.vscdb`) located in:

```
%APPDATA%\Code\User\workspaceStorage\<workspace-hash>\state.vscdb   (Windows)
~/.config/Code/User/workspaceStorage/<workspace-hash>/state.vscdb   (Linux)
~/Library/Application Support/Code/User/workspaceStorage/<workspace-hash>/state.vscdb  (macOS)
```

**VS Code Settings Sync** synchronizes extensions, keybindings, snippets, and
settings — but **not** `workspaceStorage` content. This means:

- A conversation started on Machine A is **invisible** on Machine B.
- Each machine has a different `<workspace-hash>`, so even a manual copy requires
  knowing which folder to map.
- Users who work on multiple machines (laptop + desktop, work + home) lose
  continuity in their Copilot Chat workflows.

### Technical root cause

1. The `workspaceStorage` hash is computed from the workspace folder path, which
   differs between machines (e.g., `C:\Users\Alice\project` vs. `D:\work\project`).
2. `state.vscdb` is never included in VS Code's built-in sync mechanism.
3. There is no export/import UI or API in the current extension.

---

## Proposed Solution

Implement **Copilot Chat Session Sync** as an opt-in feature, leveraging the user's
existing GitHub authentication:

### Option A — GitHub-hosted sync (preferred)

Store session data (encrypted) in a GitHub Gist or in a dedicated Copilot Cloud
endpoint, tied to the authenticated `github.copilot` account.

**Flow:**
1. User enables "Sync Chat Sessions" in Copilot Chat settings.
2. On session start: extension pulls the latest sessions from GitHub.
3. On session end / periodically: extension pushes new/updated sessions to GitHub.
4. Conflict resolution: last-write-wins with a per-session timestamp, or
   user-prompted merge UI.

### Option B — VS Code Settings Sync integration

Include relevant `ItemTable` keys from `state.vscdb` in the VS Code Settings Sync
payload (via the `vscode.ExtensionContext.globalState` sync mechanism, which already
supports `setKeysForSync`).

**Implementation hint:**
```typescript
// In extension activation
context.globalState.setKeysForSync([
  'copilot.chat.conversations',
  'copilot.chat.sessions',
  // ... other relevant keys
]);
```

This would automatically include the data in the user's existing Settings Sync
without requiring a separate infrastructure.

---

## User Impact

- **Affected users:** All Copilot Chat users who work on more than one machine
  (estimated to be a large fraction of developers).
- **Severity:** Medium — conversations are not lost, but inaccessible on other
  machines, breaking workflow continuity.
- **Workaround exists:** Manual file copy or third-party sync scripts (see
  [community scripts](https://github.com/Robobob-git/sprava/tree/main/copilot-chat-sync)),
  but this is error-prone and not user-friendly.

---

## Security and Privacy Considerations

- Sync should be **opt-in** (disabled by default).
- Data should be **end-to-end encrypted** or at minimum encrypted at rest, given
  that conversations may contain sensitive code.
- Users should be able to **delete synced data** from the cloud at any time.
- No conversation content should be used for model training without explicit consent.

---

## Acceptance Criteria

- [ ] User can enable/disable chat session sync in the Copilot Chat settings panel.
- [ ] Conversations started on Machine A appear on Machine B after sync.
- [ ] Sync respects the same GitHub account authentication already used by the extension.
- [ ] Conflict resolution strategy is documented and predictable.
- [ ] Data is encrypted in transit and at rest.
- [ ] User can clear/reset synced sessions.
- [ ] Feature works on Windows, macOS, and Linux.

---

## Additional Context

**Environment where the issue was observed:**
- VS Code: 1.111.0 (Windows)
- Extension: `github.copilot-chat@0.39.1`
- Affected DB path: `%APPDATA%\Code\User\workspaceStorage\ddd164513de1ba86adf453b26384f03d\state.vscdb`

**Related VS Code APIs:**
- [`ExtensionContext.globalState.setKeysForSync`](https://code.visualstudio.com/api/references/vscode-api#ExtensionContext)
- [Settings Sync documentation](https://code.visualstudio.com/docs/editor/settings-sync)

**Community workaround scripts:**
A community-maintained set of PowerShell scripts for manual/semi-automatic
synchronization is available at:
`copilot-chat-sync/` in this repository — see `README.md` for full documentation.
