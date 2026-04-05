"""
EXEMPLE d'utilisation de ThreadedRequestManager avec InterfaceMessagerie.

Ce fichier montre comment migrer les opérations sur les amis vers des requêtes asynchrones.
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QMessageBox
from gestionnaire_threaded import ThreadedRequestManager


class InterfaceMessagerieThreaded(QWidget):
    """
    Version threadée de InterfaceMessagerie - EXEMPLE UNIQUEMENT.
    
    Montre comment rendre asynchrones les opérations:
    - Ajout/suppression d'amis
    - Blocage/déblocage
    - Acceptation de demandes
    """
    
    def __init__(self, fenetre_principale, session):
        super().__init__()
        self.fenetre_principale = fenetre_principale
        self.session = session
        
        # NOUVEAU: Manager de requêtes threadées
        self.request_manager = ThreadedRequestManager()
        
        # ... le reste de __init__ reste identique ...
    
    # ===== EXEMPLE 1: Suppression d'ami =====
    
    def remove_friend(self, friend_id: int, visuellement: bool = False):
        """
        Version threadée de remove_friend.
        
        L'UI reste réactive pendant que la requête HTTP est en cours.
        """
        if not visuellement and friend_id not in self.liste_amis:
            print(f"Impossible de retirer l'ami {friend_id}")
            return
        
        if not visuellement:
            # AVANT (bloquant):
            # rep = self.session.gestionnaire_amis.enlever_ami(ami_id=friend_id)
            # if rep.get("status_code") != 200:
            #     return
            
            # APRÈS (non-bloquant):
            self.request_manager.execute(
                method=lambda: self.session.gestionnaire_amis.enlever_ami(ami_id=friend_id),
                on_success=lambda rep: self._on_remove_friend_success(rep, friend_id),
                on_error=lambda e: self._on_remove_friend_error(e, friend_id)
            )
        else:
            # Suppression visuelle immédiate (pas de requête)
            self._effectuer_suppression_visuelle(friend_id)
    
    def _on_remove_friend_success(self, rep, friend_id):
        """Callback quand la suppression réussit."""
        if rep and rep.get("status_code") == 200:
            self._effectuer_suppression_visuelle(friend_id)
        else:
            print(f"Erreur serveur lors de la suppression de {friend_id}")
    
    def _on_remove_friend_error(self, error, friend_id):
        """Callback en cas d'erreur réseau."""
        print(f"Erreur réseau lors de la suppression de {friend_id}: {error}")
    
    def _effectuer_suppression_visuelle(self, friend_id):
        """Code de mise à jour de l'UI (extrait de l'original)."""
        self.session.cache.invalider_ami(friend_id)
        # self.interface_amis.retirer_ami(friend_id)
        self.liste_amis.remove(friend_id)
        # self.widget_colonne_contacts.retirer_item(data=friend_id)
    
    # ===== EXEMPLE 2: Blocage d'ami =====
    
    def block_friend(self, friend_id: int):
        """Version threadée de block_friend."""
        print(f"block_friend appelé avec {friend_id}")
        
        self.request_manager.execute(
            method=lambda: self.session.gestionnaire_amis.bloquer_ami(ami_id=friend_id),
            on_success=lambda rep: self._on_block_success(rep, friend_id),
            on_error=lambda e: self._on_block_error(e, friend_id)
        )
    
    def _on_block_success(self, rep, friend_id):
        """Callback quand le blocage réussit."""
        if not rep or rep.get("status_code") != 200:
            print(f"Erreur serveur lors du bloquage de {friend_id}")
            return
        
        print("Blocage réussi")
        self.session.cache.block(friend_id)
        # self.interface_blocked.new_blocked(friend_id)
        self.remove_friend(friend_id, visuellement=True)
    
    def _on_block_error(self, error, friend_id):
        """Callback en cas d'erreur de blocage."""
        print(f"Erreur réseau lors du blocage de {friend_id}: {error}")
    
    # ===== EXEMPLE 3: Déblocage d'ami =====
    
    def unblock_friend(self, friend_id: int):
        """Version threadée de unblock_friend."""
        self.request_manager.execute(
            method=lambda: self.session.gestionnaire_amis.debloquer_ami(friend_id),
            on_success=lambda rep: self._on_unblock_success(rep, friend_id),
            on_error=lambda e: self._on_unblock_error(e, friend_id)
        )
    
    def _on_unblock_success(self, rep, friend_id):
        """Callback quand le déblocage réussit."""
        if rep.get("status_code") != 200:
            print(f"Erreur serveur lors du débloquage de {friend_id}")
            return
        
        self.session.cache.unblock(friend_id)
        # self.interface_blocked.unblock(friend_id)
    
    def _on_unblock_error(self, error, friend_id):
        """Callback en cas d'erreur de déblocage."""
        print(f"Erreur réseau lors du déblocage de {friend_id}: {error}")
    
    # ===== EXEMPLE 4: Acceptation de demande d'ami =====
    
    def new_friend(self, friend_id: int):
        """
        Version threadée de new_friend.
        
        Exemple avec DEUX requêtes séquentielles:
        1. Obtenir les infos du nouvel ami
        2. Mettre à jour le cache et l'UI
        """
        self.request_manager.execute(
            method=lambda: self.session.gestionnaire_utilisateurs.obtenir_infos(id_=friend_id),
            on_success=lambda infos: self._on_new_friend_info_received(infos, friend_id),
            on_error=lambda e: print(f"Erreur lors de la récupération des infos: {e}")
        )
    
    def _on_new_friend_info_received(self, infos, friend_id):
        """Callback quand les infos du nouvel ami sont reçues."""
        # Importer Ami uniquement si nécessaire
        try:
            from cache import Ami
            ami = Ami.depuis_dict(infos)
            self.session.cache.upsert_ami(ami)
            
            self.liste_amis.append(friend_id)
            # self.interface_amis.ajouter_ami(friend_id)
            # self.widget_colonne_contacts.ajouter_item(...)
        except Exception as e:
            print(f"Erreur lors de l'ajout du nouvel ami: {e}")
    
    # ===== EXEMPLE 5: Version simplifiée avec SimpleThreadedRequestManager =====
    
    def remove_friend_simple(self, friend_id: int):
        """
        Variante avec SimpleThreadedRequestManager pour encore moins de code.
        """
        from gestionnaire_threaded import SimpleThreadedRequestManager
        
        if not hasattr(self, 'simple_manager'):
            self.simple_manager = SimpleThreadedRequestManager()
        
        self.simple_manager.execute_simple(
            request_func=lambda: self.session.gestionnaire_amis.enlever_ami(ami_id=friend_id),
            success_callback=lambda rep: self._effectuer_suppression_visuelle(friend_id) 
                if rep.get("status_code") == 200 else None,
            error_message=f"Erreur lors de la suppression de l'ami {friend_id}"
        )
    
    def closeEvent(self, event):
        """Nettoyer les threads quand la fenêtre se ferme."""
        self.request_manager.cleanup_all()
        if hasattr(self, 'simple_manager'):
            self.simple_manager.cleanup_all()
        super().closeEvent(event)


# ============================================================
# PATTERNS AVANCÉS
# ============================================================

class ExemplesAvances:
    """Exemples de patterns plus complexes."""
    
    @staticmethod
    def exemple_chargement_avec_indicateur(self):
        """
        Pattern: Afficher un indicateur de chargement pendant la requête.
        """
        # Afficher le loader
        # self.loading_widget.show()
        
        self.request_manager.execute(
            method=lambda: self.session.gestionnaire_amis.obtenir_amis(toutes_infos=True),
            on_success=lambda result: self._on_amis_loaded(result),
            on_error=lambda e: print(f"Erreur: {e}"),
            on_finished=lambda: None  # self.loading_widget.hide()
        )
    
    @staticmethod
    def exemple_desactivation_bouton(self):
        """
        Pattern: Désactiver un bouton pendant la requête.
        """
        # bouton = self.bouton_ajouter_ami
        # bouton.setEnabled(False)
        
        self.request_manager.execute(
            method=lambda: self.session.gestionnaire_amis.demander_en_ami(nom_ami="Bob"),
            on_success=lambda rep: print("Demande envoyée!"),
            on_finished=lambda: None  # bouton.setEnabled(True)
        )
    
    @staticmethod
    def exemple_multiples_requetes_paralleles(self):
        """
        Pattern: Lancer plusieurs requêtes en parallèle.
        
        Attention: les callbacks peuvent arriver dans n'importe quel ordre!
        """
        manager = ThreadedRequestManager()
        
        # Requête 1: Charger les amis
        manager.execute(
            method=lambda: self.session.gestionnaire_amis.obtenir_amis(toutes_infos=True),
            on_success=lambda amis: print(f"Amis chargés: {len(amis)}")
        )
        
        # Requête 2: Charger les demandes (en parallèle!)
        manager.execute(
            method=lambda: self.session.gestionnaire_amis.obtenir_demandes_amis_recues(),
            on_success=lambda demandes: print(f"Demandes chargées: {demandes}")
        )
        
        # Requête 3: Charger les bloqués (en parallèle!)
        manager.execute(
            method=lambda: self.session.gestionnaire_amis.obtenir_blocked_ids(),
            on_success=lambda blocked: print(f"Bloqués: {len(blocked) if blocked else 0}")
        )
    
    @staticmethod
    def exemple_requetes_sequentielles(self):
        """
        Pattern: Exécuter des requêtes l'une après l'autre.
        
        Utile quand la requête 2 dépend du résultat de la requête 1.
        """
        manager = ThreadedRequestManager()
        
        # Étape 1: Obtenir l'ID de l'utilisateur
        manager.execute(
            method=lambda: self.session.gestionnaire_utilisateurs.obtenir_id(nom="Alice"),
            on_success=lambda user_id: self._envoyer_demande_ami(user_id, manager)
        )
    
    def _envoyer_demande_ami(self, user_id, manager):
        """Étape 2: Envoyer la demande d'ami."""
        manager.execute(
            method=lambda: self.session.gestionnaire_amis.demander_en_ami(ami_id=user_id),
            on_success=lambda rep: print(f"Demande envoyée à {user_id}")
        )


# ============================================================
# CHECKLIST DE MIGRATION
# ============================================================

"""
Pour migrer une interface existante:

☐ 1. Ajouter le manager dans __init__:
      self.request_manager = ThreadedRequestManager()

☐ 2. Identifier les méthodes avec requêtes bloquantes:
      - Chercher les appels à self.gestionnaire_*.méthode()
      - Chercher les endroits où l'UI pourrait se figer

☐ 3. Pour chaque méthode bloquante:
      a) Capturer les paramètres dans des variables locales
      b) Appeler request_manager.execute() avec un lambda
      c) Créer les callbacks _on_*_success et _on_*_error
      d) Déplacer le code de traitement dans les callbacks

☐ 4. Ajouter closeEvent pour cleanup:
      def closeEvent(self, event):
          self.request_manager.cleanup_all()
          super().closeEvent(event)

☐ 5. (Optionnel) Ajouter des indicateurs visuels:
      - Désactiver les boutons pendant les requêtes
      - Afficher des spinners/loaders
      - Afficher des messages de confirmation

☐ 6. Tester:
      - Vérifier que l'UI reste réactive
      - Vérifier que les erreurs sont gérées
      - Vérifier que les threads se terminent proprement
"""
