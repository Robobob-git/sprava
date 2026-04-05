# Diagrammes de Séquence - Threading PyQt6

## 📊 Diagramme 1: Requête BLOQUANTE (Problème)

```
┌──────────┐         ┌───────────────┐         ┌──────────┐
│Utilisateur│         │Interface PyQt6│         │Serveur API│
└─────┬────┘         └───────┬───────┘         └─────┬────┘
      │                      │                       │
      │ Clic "Connexion"     │                       │
      │─────────────────────>│                       │
      │                      │                       │
      │                      │ HTTP POST /login      │
      │                      │──────────────────────>│
      │                      │                       │
      │                      │  ⏳ ATTENTE 2s        │
      │  ❌ UI FIGÉE        │  (Requête bloquante)  │
      │  L'utilisateur       │                       │
      │  ne peut rien        │                       │
      │  faire!              │                       │
      │                      │                       │
      │                      │<──────────────────────│
      │                      │ {"api_token": "..."}  │
      │                      │                       │
      │ Interface mise à jour│                       │
      │<─────────────────────│                       │
      │                      │                       │
```

**Problème**: Pendant les 2 secondes de requête HTTP, l'UI est complètement figée.

---

## ✅ Diagramme 2: Requête THREADÉE (Solution)

```
┌──────────┐    ┌───────────────┐    ┌────────┐    ┌──────────┐
│Utilisateur│    │Interface PyQt6│    │QThread │    │Serveur API│
└─────┬────┘    └───────┬───────┘    └────┬───┘    └─────┬────┘
      │                 │                  │              │
      │ Clic "Connexion"│                  │              │
      │────────────────>│                  │              │
      │                 │                  │              │
      │                 │ Créer thread     │              │
      │                 │─────────────────>│              │
      │                 │                  │              │
      │                 │ Démarrer requête │              │
      │                 │─────────────────>│              │
      │                 │                  │              │
      │                 │ RETOUR IMMÉDIAT  │ HTTP POST    │
      │                 │<─────────────────│─────────────>│
      │                 │                  │              │
      │ ✅ UI FLUIDE   │                  │              │
      │ L'utilisateur   │                  │  ⏳ 2s      │
      │ peut bouger     │                  │              │
      │ la fenêtre,     │                  │              │
      │ cliquer, etc.   │                  │              │
      │                 │                  │              │
      │                 │                  │<─────────────│
      │                 │                  │{"api_token":.}│
      │                 │                  │              │
      │                 │ Signal success   │              │
      │                 │<─────────────────│              │
      │                 │                  │              │
      │                 │ Callback success │              │
      │                 │────────┐         │              │
      │                 │        │         │              │
      │                 │<───────┘         │              │
      │                 │                  │              │
      │ Interface MAJ   │                  │              │
      │<────────────────│                  │              │
      │                 │                  │              │
```

**Avantage**: L'interface retourne immédiatement le contrôle à l'utilisateur!

---

## 🔄 Diagramme 3: Requêtes PARALLÈLES

```
┌──────────┐    ┌───────────────┐    ┌────────┐  ┌────────┐  ┌────────┐
│Utilisateur│    │Interface PyQt6│    │Thread 1│  │Thread 2│  │Thread 3│
└─────┬────┘    └───────┬───────┘    └────┬───┘  └────┬───┘  └────┬───┘
      │                 │                  │           │           │
      │ Charger données │                  │           │           │
      │────────────────>│                  │           │           │
      │                 │                  │           │           │
      │                 │ Requête amis     │           │           │
      │                 │─────────────────>│           │           │
      │                 │                  │           │           │
      │                 │ Requête demandes │           │           │
      │                 │─────────────────────────────>│           │
      │                 │                  │           │           │
      │                 │ Requête bloqués  │           │           │
      │                 │───────────────────────────────────────────>│
      │                 │                  │           │           │
      │                 │ RETOUR IMMÉDIAT  │           │           │
      │                 │<─────────────────│           │           │
      │                 │                  │           │           │
      │ ✅ UI FLUIDE   │      ⏳ 1s       │  ⏳ 1s   │  ⏳ 1s   │
      │                 │                  │           │           │
      │                 │      Résultat 1  │           │           │
      │                 │<─────────────────│           │           │
      │                 │                  │           │           │
      │                 │            Résultat 2         │           │
      │                 │<──────────────────────────────│           │
      │                 │                  │           │           │
      │                 │                      Résultat 3           │
      │                 │<──────────────────────────────────────────│
      │                 │                  │           │           │
      │ Tout chargé     │                  │           │           │
      │<────────────────│                  │           │           │
      │                 │                  │           │           │
```

**Gain**: 3 requêtes en parallèle = 1s au lieu de 3s séquentielles!

---

## 📦 Diagramme 4: Architecture Globale

```
┌─────────────────────────────────────────────────────────────┐
│                      Application PyQt6                      │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │InterfaceLogin│  │InterfaceAmis │  │InterfaceMsg  │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                 │                  │               │
│         └─────────────────┴──────────────────┘               │
│                           │                                  │
│         ┌─────────────────▼──────────────────┐               │
│         │   ThreadedRequestManager           │               │
│         │   • execute(method, callbacks)     │               │
│         │   • Gère les QThread               │               │
│         │   • Émet signaux PyQt6             │               │
│         └─────────────────┬──────────────────┘               │
│                           │                                  │
│         ┌─────────────────▼──────────────────┐               │
│         │  gestionnaires_requetes.py         │               │
│         │  (INCHANGÉ)                        │               │
│         │  • GestionConnexions               │               │
│         │  • GestionUtilisateurs             │               │
│         │  • GestionAmis                     │               │
│         │  • GestionConversations            │               │
│         └─────────────────┬──────────────────┘               │
│                           │                                  │
└───────────────────────────┼──────────────────────────────────┘
                            │
                            │ HTTP Requests
                            ▼
                ┌───────────────────────┐
                │   Serveur API         │
                │   api.sprava.top      │
                └───────────────────────┘
```

---

## 🎬 Diagramme 5: Cycle de Vie d'une Requête Threadée

```
1. INITIALISATION
   ┌─────────────────────────────┐
   │ Interface.__init__()        │
   │ self.request_manager =      │
   │   ThreadedRequestManager()  │
   └─────────────────────────────┘
                │
                ▼

2. EXÉCUTION
   ┌─────────────────────────────────────────┐
   │ request_manager.execute(                │
   │   method=lambda: self.gestionnaire...,  │
   │   on_success=callback,                  │
   │   on_error=error_handler                │
   │ )                                       │
   └─────────────────┬───────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
   ┌─────────┐            ┌──────────────┐
   │UI Thread│            │Worker Thread │
   │         │            │              │
   │Continue │            │HTTP Request  │
   │normale  │            │⏳ Attend...  │
   │         │            │              │
   └─────────┘            └──────┬───────┘
                                 │
                                 ▼

3. RÉPONSE
                         ┌──────────────┐
                         │Serveur répond│
                         └──────┬───────┘
                                │
                    ┌───────────┴────────────┐
                    │                        │
                    ▼                        ▼
            ┌──────────────┐        ┌───────────────┐
            │   Succès     │        │    Erreur     │
            │Signal success│        │Signal error   │
            └──────┬───────┘        └───────┬───────┘
                   │                        │
                   └───────────┬────────────┘
                               │
                               ▼

4. CALLBACK (dans UI Thread)
   ┌─────────────────────────────────────┐
   │ _on_success(result) ou              │
   │ _on_error(exception)                │
   │                                     │
   │ Mise à jour de l'interface          │
   └─────────────────────────────────────┘
                   │
                   ▼

5. CLEANUP
   ┌─────────────────────────────────────┐
   │ Signal finished émis                │
   │ Thread.quit()                       │
   │ Thread.wait()                       │
   │ Thread retiré de active_threads     │
   └─────────────────────────────────────┘
```

---

## 🔁 Diagramme 6: Transformation du Code

```
AVANT (Bloquant)
┌────────────────────────────────────────────┐
│ def lancer_connexion(self):                │
│     rep = self.gestionnaire.connexion(...) │ ← BLOQUE ICI
│     if rep:                                │
│         self.token = rep['api_token']      │
│         self.connexion_confirmee()         │
└────────────────────────────────────────────┘

                    │
                    │ TRANSFORMATION
                    ▼

APRÈS (Threadé)
┌────────────────────────────────────────────┐
│ def lancer_connexion(self):                │
│     mail = self.mail_widget.text()         │
│     mdp = self.mdp_widget.text()           │
│                                            │
│     self.request_manager.execute(          │
│         method=lambda:                     │
│           self.gestionnaire.connexion(...),│
│         on_success=self._on_success        │ ← Callback
│     )                                      │
│     # RETOURNE IMMÉDIATEMENT               │
│                                            │
│ def _on_success(self, rep):                │ ← Nouveau
│     if rep:                                │
│         self.token = rep['api_token']      │
│         self.connexion_confirmee()         │
└────────────────────────────────────────────┘
```

---

## 💡 Diagramme 7: Gestion d'Erreur

```
┌──────────────────────────────────────────────────────┐
│                 Requête Threadée                     │
└────────────────────┬─────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
┌───────────────┐         ┌───────────────┐
│   Succès      │         │   Erreur      │
└───────┬───────┘         └───────┬───────┘
        │                         │
        │                         │
        ▼                         ▼
┌───────────────┐         ┌───────────────────────┐
│on_success()   │         │on_error()             │
│appelé avec    │         │appelé avec Exception  │
│le résultat    │         │• Erreur réseau        │
│               │         │• Timeout              │
│• Mise à jour  │         │• Serveur down         │
│  l'UI         │         │                       │
│• Afficher     │         │• Afficher message     │
│  résultat     │         │• Logger l'erreur      │
└───────┬───────┘         └───────┬───────────────┘
        │                         │
        └────────────┬────────────┘
                     │
                     ▼
            ┌────────────────┐
            │on_finished()   │
            │Toujours appelé │
            │                │
            │• Masquer loader│
            │• Réactiver btn │
            │• Cleanup       │
            └────────────────┘
```

---

## 🎯 Diagramme 8: Pattern Complet avec UI

```
┌─────────────────────────────────────────────────────────┐
│                   Interface Utilisateur                 │
│                                                          │
│  ┌──────────┐  ┌────────────┐  ┌─────────────┐         │
│  │ Bouton   │  │ Spinner    │  │ Label Statut│         │
│  │"Connexion│  │ (caché)    │  │             │         │
│  └─────┬────┘  └──────┬─────┘  └──────┬──────┘         │
│        │              │                │                │
└────────┼──────────────┼────────────────┼────────────────┘
         │              │                │
         │ 1. Clic      │                │
         ▼              │                │
    ┌────────────────┐  │                │
    │lancer_connexion│  │                │
    └────────┬───────┘  │                │
             │          │                │
             │ 2. Désactiver bouton      │
             │    Afficher spinner       │
             ▼          │                │
         ┌─────────────┐│                │
         │Bouton OFF   ││                │
         └─────────────┘▼                │
                   ┌─────────┐           │
                   │Spinner  │           │
                   │visible  │           │
                   └─────────┘           │
             │                           │
             │ 3. Lancer requête threadée│
             ▼                           │
    ┌──────────────────┐                 │
    │request_manager   │                 │
    │.execute(...)     │                 │
    └─────────┬────────┘                 │
              │                          │
              │ 4. Requête en cours...   │
              │    ⏳ 2 secondes         │
              │                          │
              │ 5. Réponse reçue         │
              ▼                          │
     ┌─────────────────┐                 │
     │_on_success()    │                 │
     └────────┬────────┘                 │
              │                          │
              │ 6. Masquer spinner       │
              │    Réactiver bouton      │
              │    Mettre à jour statut  │
              ▼                          ▼
         ┌─────────┐              ┌─────────────┐
         │Spinner  │              │Label:       │
         │caché    │              │"Connecté!"  │
         └─────────┘              └─────────────┘
              │                          │
              ▼                          ▼
         ┌─────────────┐                 │
         │Bouton ON    │                 │
         └─────────────┘                 │
```

---

## 📝 Légende

```
┌─────┐
│ Box │  = Composant ou action
└─────┘

   │
   ▼      = Flux / Direction

⏳       = Attente / Temps

✅       = Succès / OK

❌       = Problème / Erreur

┌────┐
│ ON │  = État actif
└────┘

┌────┐
│OFF │  = État inactif
└────┘
```

---

**Ces diagrammes illustrent visuellement le fonctionnement du système de threading.**

Consultez les fichiers de code pour l'implémentation réelle :
- `gestionnaire_threaded.py` - Le module
- `exemple_*.py` - Exemples complets
- `demo_threading.py` - Démo interactive
