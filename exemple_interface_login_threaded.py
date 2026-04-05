"""
EXEMPLE d'utilisation de ThreadedRequestManager avec InterfaceLogin.

Ce fichier montre comment migrer InterfaceLogin vers des requêtes asynchrones
SANS MODIFIER le code original.

Pour l'utiliser:
1. Copiez les méthodes modifiées dans votre InterfaceLogin
2. Ajoutez self.request_manager = ThreadedRequestManager() dans __init__
3. Remplacez les anciennes méthodes par les nouvelles versions
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QMessageBox
from gestionnaire_threaded import ThreadedRequestManager
from gestionnaires_requetes import GestionConnexions


class InterfaceLoginThreaded(QWidget):
    """
    Version threadée de InterfaceLogin - EXEMPLE UNIQUEMENT.
    
    Les changements par rapport à l'original:
    - Ajout de self.request_manager dans __init__
    - Modification de lancer_connexion() pour utiliser les threads
    - Modification de lancer_inscription() pour utiliser les threads
    - Ajout de méthodes de callback (_on_connexion_success, etc.)
    """
    
    def __init__(self, fenetre_principale):
        super().__init__()
        self.fenetre_principale = fenetre_principale
        
        # NOUVEAU: Manager de requêtes threadées
        self.request_manager = ThreadedRequestManager()
        
        # Garde le gestionnaire de connexions original (inchangé)
        self.gestionnaire_connexions = GestionConnexions()
        
        # ... le reste de __init__ reste identique ...
    
    def lancer_connexion(self):
        """
        Version threadée de lancer_connexion.
        
        AVANT (bloquant):
            rep = self.gestionnaire_connexions.connexion(mail=..., mdp=...)
            if rep:
                # traiter résultat
        
        APRÈS (non-bloquant):
            self.request_manager.execute(
                method=lambda: self.gestionnaire_connexions.connexion(...),
                on_success=self._on_connexion_success,
                on_error=self._on_connexion_error
            )
        """
        mail = getattr(self, 'mail_widget_connexion', None)
        mdp = getattr(self, 'mdp_widget_connexion', None)
        
        if not mail or not mdp:
            print("Widgets non initialisés")
            return
        
        if mail.text() != "" and mdp.text() != "":
            # Capturer les valeurs dans la closure
            mail_value = mail.text()
            mdp_value = mdp.text()
            
            # Exécution asynchrone
            self.request_manager.execute(
                method=lambda: self.gestionnaire_connexions.connexion(
                    mail=mail_value, 
                    mdp=mdp_value
                ),
                on_success=self._on_connexion_success,
                on_error=self._on_connexion_error
            )
            
            # Optionnel: désactiver le bouton pendant la requête
            # self.bouton_connexion.setEnabled(False)
        else:
            print('Veuillez renseigner le mail et le mot de passe')
    
    def _on_connexion_success(self, rep):
        """Callback appelé quand la connexion réussit."""
        # Réactiver le bouton si vous l'aviez désactivé
        # self.bouton_connexion.setEnabled(True)
        
        if rep:
            self.token = rep.pop('api_token')
            rep.pop('status_code')
            self.user_info = rep
            self.connexion_confirmee()
        else:
            print("Connexion échouée")
    
    def _on_connexion_error(self, error):
        """Callback appelé en cas d'erreur réseau."""
        # self.bouton_connexion.setEnabled(True)
        print(f"Erreur lors de la connexion: {error}")
        # Optionnel: afficher un message à l'utilisateur
        # QMessageBox.warning(self, "Erreur", f"Connexion impossible: {error}")
    
    def lancer_inscription(self):
        """Version threadée de lancer_inscription."""
        # Récupérer les valeurs des widgets
        pseudo_widget = getattr(self, 'pseudo_widget', None)
        mail_widget = getattr(self, 'mail_widget_inscription', None)
        mdp_widget = getattr(self, 'mdp_widget_inscription', None)
        confirmer_mdp = getattr(self, 'confirmer_mdp', None)
        date_widget = getattr(self, 'date_naiss_widget', None)
        
        if not all([pseudo_widget, mail_widget, mdp_widget, confirmer_mdp, date_widget]):
            print("Widgets non initialisés")
            return
        
        # Vérifications
        if pseudo_widget.text() != "" and mail_widget.text() != "" and \
           mdp_widget.text() != "" and confirmer_mdp.text() != "" and \
           date_widget.date().toString("yyyy-MM-dd") != "":
            
            if mdp_widget.text() == confirmer_mdp.text():
                # Capturer les valeurs
                pseudo = pseudo_widget.text()
                mail = mail_widget.text()
                mdp = mdp_widget.text()
                date_naiss = date_widget.date().toString("yyyy-MM-dd")
                
                # Exécution asynchrone
                self.request_manager.execute(
                    method=lambda: self.gestionnaire_connexions.inscription(
                        pseudo=pseudo,
                        mail=mail,
                        mdp=mdp,
                        date_naissance=date_naiss
                    ),
                    on_success=self._on_inscription_success,
                    on_error=self._on_inscription_error
                )
            else:
                print("Les mots de passe ne correspondent pas")
        else:
            print('Veuillez renseigner correctement tous les champs')
    
    def _on_inscription_success(self, rep):
        """Callback appelé quand l'inscription réussit."""
        if rep:
            self.token = rep.pop('api_token')
            rep.pop('status_code')
            self.user_info = rep
            self.inscription_confirmee()
        else:
            print("Inscription échouée")
    
    def _on_inscription_error(self, error):
        """Callback appelé en cas d'erreur d'inscription."""
        print(f"Erreur lors de l'inscription: {error}")
    
    # Les méthodes connexion_confirmee() et inscription_confirmee()
    # restent IDENTIQUES à l'original
    
    def connexion_confirmee(self):
        """Identique à l'original - pas de changement."""
        print(f"token : {self.token}")
        print("Connecté avec succès")
        # ... reste du code original ...
    
    def inscription_confirmee(self):
        """Identique à l'original - pas de changement."""
        print(f"token : {self.token}")
        # self.changer_moyen_connexion()
        # QMessageBox.information(self, "INFO", "Compte créé avec succès")
    
    def closeEvent(self, event):
        """Nettoyer les threads quand la fenêtre se ferme."""
        self.request_manager.cleanup_all()
        super().closeEvent(event)


# ============================================================
# MIGRATION PROGRESSIVE: Comment adapter votre code existant
# ============================================================

"""
ÉTAPE 1: Ajouter le manager dans __init__
    def __init__(self, fenetre_principale):
        super().__init__()
        # ... code existant ...
        self.request_manager = ThreadedRequestManager()  # <-- AJOUTER

ÉTAPE 2: Transformer une méthode bloquante
    AVANT:
        def lancer_connexion(self):
            rep = self.gestionnaire.connexion(mail=..., mdp=...)
            if rep:
                self.token = rep.pop('api_token')
                # ...
    
    APRÈS:
        def lancer_connexion(self):
            mail = self.mail_widget.text()
            mdp = self.mdp_widget.text()
            
            self.request_manager.execute(
                method=lambda: self.gestionnaire.connexion(mail=mail, mdp=mdp),
                on_success=self._on_connexion_success
            )
        
        def _on_connexion_success(self, rep):
            if rep:
                self.token = rep.pop('api_token')
                # ... reste du code original ...

ÉTAPE 3: Cleanup à la fermeture
    def closeEvent(self, event):
        self.request_manager.cleanup_all()
        super().closeEvent(event)
"""
