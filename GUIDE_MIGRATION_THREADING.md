# Guide de Migration: Ajouter le Threading à votre Application PyQt6

## 📋 Vue d'ensemble

Ce guide explique comment migrer votre application PyQt6 de requêtes HTTP **bloquantes** vers des requêtes **asynchrones** sans modifier le code existant dans `gestionnaires_requetes.py`.

## 🎯 Le Problème

```python
# Code actuel (BLOQUANT)
def lancer_connexion(self):
    rep = self.gestionnaire_connexions.connexion(mail=..., mdp=...)  # ❌ UI FIGÉE pendant 1-3s
    if rep:
        self.token = rep.pop('api_token')
        # ...
```

**Résultat**: L'interface se fige, l'utilisateur ne peut rien faire.

## ✅ La Solution

```python
# Code threadé (FLUIDE)
def lancer_connexion(self):
    self.request_manager.execute(
        method=lambda: self.gestionnaire_connexions.connexion(mail=..., mdp=...),
        on_success=self._on_connexion_success  # ✅ UI RESTE FLUIDE
    )

def _on_connexion_success(self, rep):
    if rep:
        self.token = rep.pop('api_token')
        # ... même code qu'avant
```

**Résultat**: L'interface reste réactive, meilleure expérience utilisateur.

---

## 📦 Fichiers Créés

| Fichier | Description |
|---------|-------------|
| `gestionnaire_threaded.py` | Module principal avec `RequestWorker` et `ThreadedRequestManager` |
| `exemple_interface_login_threaded.py` | Exemple complet pour `InterfaceLogin` |
| `exemple_interface_messagerie_threaded.py` | Exemple complet pour `InterfaceMessagerie` |
| `demo_threading.py` | Application de démo interactive |
| `GUIDE_MIGRATION_THREADING.md` | Ce guide |

---

## 🚀 Démarrage Rapide

### 1️⃣ Tester la Démo

Lancez la démo pour voir la différence :

```bash
python demo_threading.py
```

**Essayez**:
- Cliquez sur "Faire une requête BLOQUANTE" → l'UI se fige ❌
- Cliquez sur "Requête THREADÉE" → l'UI reste fluide ✅

### 2️⃣ Migrer votre Première Interface

#### Étape A: Ajouter le manager

Dans `__init__` de votre interface:

```python
from gestionnaire_threaded import ThreadedRequestManager

class InterfaceLogin(QWidget):
    def __init__(self, fenetre_principale):
        super().__init__()
        # ... code existant ...
        
        # AJOUTER CETTE LIGNE
        self.request_manager = ThreadedRequestManager()
```

#### Étape B: Transformer une méthode

**AVANT** (code actuel):
```python
def lancer_connexion(self):
    if self.mail_widget_connexion.text() != "" and self.mdp_widget_connexion.text() != "":
        rep = self.gestionnaire_connexions.connexion(
            mail=self.mail_widget_connexion.text(), 
            mdp=self.mdp_widget_connexion.text()
        )
        if rep:
            self.token = rep.pop('api_token')
            rep.pop('status_code')
            self.user_info = rep
            self.connexion_confirmee()
```

**APRÈS** (threadé):
```python
def lancer_connexion(self):
    if self.mail_widget_connexion.text() != "" and self.mdp_widget_connexion.text() != "":
        # Capturer les valeurs dans des variables locales
        mail = self.mail_widget_connexion.text()
        mdp = self.mdp_widget_connexion.text()
        
        # Exécution asynchrone
        self.request_manager.execute(
            method=lambda: self.gestionnaire_connexions.connexion(mail=mail, mdp=mdp),
            on_success=self._on_connexion_success,
            on_error=self._on_connexion_error
        )

def _on_connexion_success(self, rep):
    """Callback appelé quand la connexion réussit."""
    if rep:
        self.token = rep.pop('api_token')
        rep.pop('status_code')
        self.user_info = rep
        self.connexion_confirmee()
    else:
        print("Connexion échouée")

def _on_connexion_error(self, error):
    """Callback appelé en cas d'erreur réseau."""
    print(f"Erreur lors de la connexion: {error}")
```

#### Étape C: Cleanup à la fermeture

Ajoutez cette méthode à votre interface:

```python
def closeEvent(self, event):
    """Nettoyer les threads quand la fenêtre se ferme."""
    self.request_manager.cleanup_all()
    super().closeEvent(event)
```

---

## 🎓 Exemples Détaillés

### Exemple 1: Connexion Simple

```python
# Dans votre interface
def lancer_connexion(self):
    mail = self.mail_widget.text()
    mdp = self.mdp_widget.text()
    
    self.request_manager.execute(
        method=lambda: self.gestionnaire.connexion(mail=mail, mdp=mdp),
        on_success=lambda rep: self.traiter_connexion(rep),
        on_error=lambda e: print(f"Erreur: {e}")
    )

def traiter_connexion(self, rep):
    if rep:
        self.token = rep.pop('api_token')
        print("Connecté!")
```

### Exemple 2: Supprimer un Ami

```python
def supprimer_ami(self, ami_id):
    self.request_manager.execute(
        method=lambda: self.gestionnaire_amis.enlever_ami(ami_id=ami_id),
        on_success=lambda rep: self._on_ami_supprime(rep, ami_id)
    )

def _on_ami_supprime(self, rep, ami_id):
    if rep.get("status_code") == 200:
        self.liste_amis.remove(ami_id)
        print(f"Ami {ami_id} supprimé")
```

### Exemple 3: Charger les Amis au Démarrage

```python
def charger_amis(self):
    # Afficher un indicateur de chargement
    self.loading_label.show()
    
    self.request_manager.execute(
        method=lambda: self.gestionnaire_amis.obtenir_amis(toutes_infos=True),
        on_success=self._on_amis_charges,
        on_finished=lambda: self.loading_label.hide()  # Masquer le loader
    )

def _on_amis_charges(self, amis):
    for ami in amis:
        self.ajouter_ami_ui(ami)
```

### Exemple 4: Requêtes Séquentielles

Quand une requête dépend d'une autre:

```python
def ajouter_ami_par_nom(self, nom):
    # Étape 1: Obtenir l'ID
    self.request_manager.execute(
        method=lambda: self.gestionnaire_utilisateurs.obtenir_id(nom=nom),
        on_success=lambda user_id: self._envoyer_demande(user_id)
    )

def _envoyer_demande(self, user_id):
    # Étape 2: Envoyer la demande
    self.request_manager.execute(
        method=lambda: self.gestionnaire_amis.demander_en_ami(ami_id=user_id),
        on_success=lambda rep: print("Demande envoyée!")
    )
```

### Exemple 5: Requêtes Parallèles

Charger plusieurs choses en même temps:

```python
def charger_donnees(self):
    # Les 3 requêtes s'exécutent EN PARALLÈLE
    
    self.request_manager.execute(
        method=lambda: self.gestionnaire_amis.obtenir_amis(toutes_infos=True),
        on_success=self._on_amis_charges
    )
    
    self.request_manager.execute(
        method=lambda: self.gestionnaire_amis.obtenir_demandes_amis_recues(),
        on_success=self._on_demandes_chargees
    )
    
    self.request_manager.execute(
        method=lambda: self.gestionnaire_amis.obtenir_blocked_ids(),
        on_success=self._on_bloques_charges
    )
```

---

## 🔍 Patterns Avancés

### Pattern 1: Désactiver un Bouton Pendant la Requête

```python
def envoyer_message(self):
    bouton = self.bouton_envoyer
    bouton.setEnabled(False)  # Désactiver
    
    message = self.champ_texte.text()
    
    self.request_manager.execute(
        method=lambda: self.gestionnaire_conv.envoyer_msg(conv_id=1, msg=message),
        on_success=lambda rep: self.message_envoye(rep),
        on_finished=lambda: bouton.setEnabled(True)  # Réactiver dans tous les cas
    )
```

### Pattern 2: Indicateur de Chargement (Spinner)

```python
def charger_conversations(self):
    self.spinner.show()
    self.liste_conv.hide()
    
    self.request_manager.execute(
        method=lambda: self.gestionnaire_conv.obtenir_convs(),
        on_success=self._afficher_conversations,
        on_finished=lambda: (self.spinner.hide(), self.liste_conv.show())
    )
```

### Pattern 3: Gestion d'Erreur avec Message Utilisateur

```python
def connexion(self):
    self.request_manager.execute(
        method=lambda: self.gestionnaire.connexion(mail=..., mdp=...),
        on_success=self._connexion_ok,
        on_error=self._afficher_erreur
    )

def _afficher_erreur(self, error):
    from PyQt6.QtWidgets import QMessageBox
    QMessageBox.warning(
        self, 
        "Erreur de connexion",
        f"Impossible de se connecter:\n{error}"
    )
```

### Pattern 4: Progression avec Plusieurs Étapes

```python
def inscription_complete(self):
    # Étape 1
    self.statut_label.setText("Création du compte...")
    self.request_manager.execute(
        method=lambda: self.gestionnaire.inscription(...),
        on_success=self._etape2_connexion
    )

def _etape2_connexion(self, rep):
    self.token = rep['api_token']
    self.statut_label.setText("Chargement du profil...")
    
    self.request_manager.execute(
        method=lambda: self.gestionnaire_utilisateurs.obtenir_infos(id=rep['user_id']),
        on_success=self._etape3_finalisation
    )

def _etape3_finalisation(self, infos):
    self.statut_label.setText("Finalisation...")
    self.profil_charge(infos)
```

---

## 📝 Checklist de Migration

Pour chaque interface à migrer:

- [ ] ✅ Ajouter `self.request_manager = ThreadedRequestManager()` dans `__init__`
- [ ] ✅ Identifier toutes les méthodes qui font des requêtes HTTP
- [ ] ✅ Pour chaque méthode:
  - [ ] Capturer les paramètres dans des variables locales
  - [ ] Remplacer l'appel direct par `request_manager.execute()`
  - [ ] Créer les callbacks `_on_*_success` et `_on_*_error`
  - [ ] Déplacer le code de traitement dans les callbacks
- [ ] ✅ Ajouter `closeEvent()` pour le cleanup
- [ ] ✅ (Optionnel) Ajouter des indicateurs visuels (loaders, désactivation de boutons)
- [ ] ✅ Tester que l'UI reste réactive

---

## ⚠️ Pièges à Éviter

### 1. Capture de Variables dans les Lambdas

❌ **MAUVAIS**:
```python
def supprimer_ami(self, ami_id):
    # ami_id pourrait changer avant l'exécution!
    self.request_manager.execute(
        method=lambda: self.gestionnaire.enlever_ami(ami_id=ami_id)  # ❌ Référence
    )
```

✅ **BON**:
```python
def supprimer_ami(self, ami_id):
    # Capturer la valeur maintenant
    id_a_supprimer = ami_id
    self.request_manager.execute(
        method=lambda: self.gestionnaire.enlever_ami(ami_id=id_a_supprimer)  # ✅
    )
```

### 2. Accès aux Widgets dans les Callbacks

❌ **MAUVAIS**:
```python
def charger_amis(self):
    self.request_manager.execute(
        method=lambda: self.gestionnaire.obtenir_amis(),
        on_success=lambda amis: self.widget_liste.setText(str(amis))  # ❌ Widget peut être détruit
    )
```

✅ **BON**:
```python
def charger_amis(self):
    self.request_manager.execute(
        method=lambda: self.gestionnaire.obtenir_amis(),
        on_success=self._afficher_amis  # ✅ Méthode qui vérifie l'existence
    )

def _afficher_amis(self, amis):
    if hasattr(self, 'widget_liste'):  # Vérifier que le widget existe
        self.widget_liste.setText(str(amis))
```

### 3. Oublier le Cleanup

❌ **MAUVAIS**:
```python
class MonInterface(QWidget):
    def __init__(self):
        self.request_manager = ThreadedRequestManager()
        # ... pas de closeEvent()
```

✅ **BON**:
```python
class MonInterface(QWidget):
    def __init__(self):
        self.request_manager = ThreadedRequestManager()
    
    def closeEvent(self, event):
        self.request_manager.cleanup_all()  # ✅ Nettoyer les threads
        super().closeEvent(event)
```

---

## 🧪 Tester votre Migration

### Test 1: UI Réactive

1. Lancez votre application
2. Cliquez sur un bouton qui fait une requête
3. **Essayez immédiatement** de bouger la fenêtre ou cliquer ailleurs
4. ✅ Si vous pouvez interagir → Migration réussie
5. ❌ Si l'UI se fige → Il reste des requêtes bloquantes

### Test 2: Vérifier les Threads

Ajoutez ce code temporaire:

```python
def lancer_requete(self):
    print(f"Threads actifs avant: {len(self.request_manager.active_threads)}")
    
    self.request_manager.execute(
        method=lambda: self.gestionnaire.connexion(...),
        on_success=lambda rep: print(f"Threads actifs après: {len(self.request_manager.active_threads)}")
    )
```

Les threads doivent se nettoyer automatiquement.

### Test 3: Gestion d'Erreur

1. Coupez votre connexion internet
2. Essayez de faire une requête
3. ✅ Le callback `on_error` devrait être appelé
4. ✅ L'application ne devrait pas crasher

---

## 🎨 Améliorer l'Expérience Utilisateur

### Indicateur de Chargement Simple

```python
class MonInterface(QWidget):
    def __init__(self):
        super().__init__()
        self.loading_label = QLabel("Chargement...")
        self.loading_label.hide()
        # ... ajouter au layout ...
    
    def charger_donnees(self):
        self.loading_label.show()
        
        self.request_manager.execute(
            method=lambda: self.gestionnaire.obtenir_amis(),
            on_success=self._donnees_chargees,
            on_finished=lambda: self.loading_label.hide()
        )
```

### Spinner Animé (QProgressBar)

```python
from PyQt6.QtWidgets import QProgressBar

class MonInterface(QWidget):
    def __init__(self):
        super().__init__()
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # Mode "indéterminé"
        self.progress.hide()
    
    def charger_donnees(self):
        self.progress.show()
        
        self.request_manager.execute(
            method=lambda: self.gestionnaire.obtenir_amis(),
            on_success=self._donnees_chargees,
            on_finished=lambda: self.progress.hide()
        )
```

---

## 📚 Ressources Supplémentaires

### Fichiers à Consulter

1. **`gestionnaire_threaded.py`**: Le module principal
2. **`exemple_interface_login_threaded.py`**: Migration complète de InterfaceLogin
3. **`exemple_interface_messagerie_threaded.py`**: Migration complète de InterfaceMessagerie
4. **`demo_threading.py`**: Démo interactive

### Documentation PyQt6

- [QThread](https://doc.qt.io/qt-6/qthread.html)
- [Signals & Slots](https://doc.qt.io/qt-6/signalsandslots.html)

---

## 🆘 Besoin d'Aide?

### Problème: L'UI se fige toujours

**Solution**: Vérifiez que vous utilisez bien `request_manager.execute()` et pas un appel direct.

### Problème: "RuntimeError: wrapped C/C++ object has been deleted"

**Solution**: Le widget a été détruit avant le callback. Vérifiez l'existence:

```python
def callback(self, result):
    if hasattr(self, 'mon_widget') and self.mon_widget:
        self.mon_widget.setText(str(result))
```

### Problème: Les threads ne se terminent pas

**Solution**: Vérifiez que vous appelez `cleanup_all()` dans `closeEvent()`.

---

## 🎉 Conclusion

Vous avez maintenant tous les outils pour migrer votre application vers des requêtes asynchrones !

**Prochaines étapes**:

1. ✅ Tester la démo: `python demo_threading.py`
2. ✅ Migrer `interface_login.py` en premier
3. ✅ Migrer `interface_messagerie.py` ensuite
4. ✅ Migrer les autres interfaces progressivement

**Avantages obtenus**:

- ✅ UI fluide et réactive
- ✅ Meilleure expérience utilisateur
- ✅ Code original préservé (`gestionnaires_requetes.py` inchangé)
- ✅ Migration progressive possible

Bonne migration ! 🚀
