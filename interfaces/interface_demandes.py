from PyQt6.QtCore import Qt, QSize, QUrl, QEventLoop, pyqtSignal
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout, QWidget, QPushButton, QLineEdit, QLabel, QStatusBar, QCompleter, QComboBox, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QDoubleSpinBox, QScrollArea, QSpinBox, QSizePolicy, QListWidget, QListWidgetItem
from PyQt6.QtGui import QAction, QPixmap, QIcon, QFont
from dataclasses import dataclass

from gestionnaires_requetes import GestionAmis
from interfaces.interface_graphique import ListeElements, BoutonCustom
from autre_fonctions import obtenir_vrai_chemin

@dataclass
class Demande:
    nom: str
    identifiant: int

class InterfaceDemandesRecues(QWidget):
    ami_accept = pyqtSignal(int)    # On le crée ici parce que les pyqtSignal sont bizzares

    def __init__(self, session):
        super().__init__()

        self.session = session
        self.requettes_manager = session.requettes_manager

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.demandes:list[Demande] = []
        self._trouver_demandes_recues()

        self.ui = self._faire_ui()

    def _trouver_demandes_recues(self):
        def succes(rep):
            if rep.get('friend_requests_ids') == []:
                self.demandes = []
                self.ui = self._faire_ui()
                return
            liste_ids = [fr.get('sender_id') for fr in rep.get('friend_requests_ids')]
            liste_noms = self.session.gestionnaire_utilisateurs.obtenir_noms(ids=liste_ids)

            self.demandes = [Demande(nom, id_) for nom, id_ in zip(liste_noms, liste_ids)]
            self.ui = self._faire_ui()
            return
        
        self.requettes_manager.executer(func=self.session.gestionnaire_amis.obtenir_demandes_amis_recues, func_succes=succes)
        # La réponse est de la forme : {'status_code': 200, 'friend_requests_ids': [{'sender_id': 17, 'created_at': '2026-02-11T09:58:13'}]}

    def _faire_ui(self):
        widget_recues = ListeElements()
        for d in self.demandes:
            w = QWidget()
            l = QHBoxLayout()
            w.setLayout(l)
            label = QLabel(d.nom)
            bouton_acc = BoutonCustom(taille=(25, 25), chemin_image=obtenir_vrai_chemin("images/accept.svg"), custom_command=lambda d=d: self.accepter_demande(d))
            bouton_ref = BoutonCustom(taille=(25, 25), chemin_image=obtenir_vrai_chemin("images/deny.svg"), custom_command=lambda d=d: self.refuser_demande(d))

            l.addWidget(label)
            l.addWidget(bouton_acc)
            l.addWidget(bouton_ref)
            widget_recues.ajouter_item(data="", widget=w)
        self.layout.addWidget(widget_recues)
        return widget_recues

    def accepter_demande(self, demande):
        def succes(rep):
            self.demandes.remove(demande)
            self.ami_accept.emit(rep.get('new_friend_id'))

            self.update_ui()
        def erreur(e):
            print(f"erreur lors de l'accpetation de {demande.nom} : {e}")

        self.requettes_manager.executer(func=lambda : self.session.gestionnaire_amis.accepter_demande_ami(nom_ami=demande.nom, ami_id=demande.identifiant), func_succes=succes, func_erreur=erreur)

    def refuser_demande(self, demande):
        def succes(rep):
            self.demandes.remove(demande)
            self.update_ui()
        def erreur(e):
            print(f"erreur lors de la rejection de la demande de {demande.nom} : {e}")
        
        self.requettes_manager.executer(func=lambda : self.session.gestionnaire_amis.refuser_demande_ami(ami_id=demande.identifiant), func_succes=succes, func_erreur=erreur)

    def update_ui(self):
        '''On supprime le widget pour le raffraichir'''
        self.layout.removeWidget(self.ui)
        self.ui.setParent(None)
        self.ui.deleteLater()

        self.ui = self._faire_ui()

class InterfaceDemandesEnvoyees(QWidget):
    def __init__(self, session):
        super().__init__()

        self.session = session
        self.requettes_manager = session.requettes_manager

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.demandes = []
        self._trouver_demandes_envoyees()

        self.ui = self._faire_ui()
    
    def _trouver_demandes_envoyees(self):
        def succes(rep):
            if rep.get('sent_friend_requests_ids') == []:
                self.demandes = []
                self.ui = self._faire_ui()
                return
            liste_ids = [fr.get('receiver_id') for fr in rep.get('sent_friend_requests_ids')]
            liste_noms = self.session.gestionnaire_utilisateurs.obtenir_noms(ids=liste_ids)
            
            self.demandes = [Demande(nom, id_) for nom, id_ in zip(liste_noms, liste_ids)]
            self.ui = self._faire_ui()
            return
        
        self.requettes_manager.executer(func=self.session.gestionnaire_amis.obtenir_demandes_amis_envoyees, func_succes=succes)


    def _faire_ui(self):
        widget_envoyees = ListeElements()
        for d in self.demandes:
            w = QWidget()
            l = QHBoxLayout()
            w.setLayout(l)
            label = QLabel(d.nom)
            bouton_annuler = BoutonCustom(taille=(25, 25), chemin_image=obtenir_vrai_chemin("images/deny.svg"), custom_command=lambda d=d: self.annuler_demande(d))

            l.addWidget(label)
            l.addWidget(bouton_annuler)
            widget_envoyees.ajouter_item(data="", widget=w)
        self.layout.addWidget(widget_envoyees)
        return widget_envoyees
    
    def annuler_demande(self, demande):
        def succes(rep):
            self.demandes.remove(demande)
            self.update_ui()

            self.update_ui()
        def erreur(e):
            print(f"erreur lors de l'annulation de la demande pour {demande.nom} : {e}")

        self.requettes_manager.executer(func=lambda : self.session.gestionnaire_amis.annuler_demande_ami(nom_ami=demande.nom), func_succes=succes, func_erreur=erreur)

    def update_ui(self):
        '''On supprime le widget pour le raffraichir'''
        self.layout.removeWidget(self.ui)
        self.ui.setParent(None)
        self.ui.deleteLater()

        self.ui = self._faire_ui()
        

        