from PyQt6.QtCore import Qt, QSize, QUrl, QEventLoop, pyqtSignal
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout, QWidget, QPushButton, QLineEdit, QLabel, QStatusBar, QCompleter, QComboBox, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QDoubleSpinBox, QScrollArea, QSpinBox, QSizePolicy, QListWidget, QListWidgetItem
from PyQt6.QtGui import QAction, QPixmap, QIcon, QFont
from dataclasses import dataclass

from interfaces.interface_graphique import ListeElements, BoutonCustom
from autre_fonctions import obtenir_vrai_chemin

@dataclass
class Demande:
    nom: str
    identifiant: int

class InterfaceDemandesRecues(QWidget):
    ami_accept = pyqtSignal(int)    # On le crée ici parce que les pyqtSignal sont bizzares

    def __init__(self, session, test):
        super().__init__()

        self.session = session
        self.test = test
        if not self.test:
            self.requettes_manager = session.requettes_manager

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.widget_recues = ListeElements()
        self.layout.addWidget(self.widget_recues)

        self.demandes:list[int] = []
        if not self.test:
            self._trouver_demandes_recues()

        self._faire_ui()

    def _trouver_demandes_recues(self):
        def succes(rep):
            if rep.get('friend_requests_ids') == []:
                self.demandes = []
                return
            self.demandes = [fr.get('sender_id') for fr in rep.get('friend_requests_ids')]
            self._faire_ui()


        self.requettes_manager.executer(func=self.session.gestionnaire_amis.obtenir_demandes_amis_recues, func_succes=succes)
        # La réponse est de la forme : {'status_code': 200, 'friend_requests_ids': [{'sender_id': 17, 'created_at': '2026-02-11T09:58:13'}]}

    def _faire_ui(self):
        def succes(rep):    # Ici on a direct une liste de noms en str
            for id_, nom in zip(self.demandes, rep):
                self.ajouter_demande(ami_id=id_, ami_nom=nom)
        
        self.requettes_manager.executer(func=lambda : self.session.gestionnaire_utilisateurs.obtenir_noms(ids=self.demandes), func_succes=succes)

    def accepter_demande(self, ami_id:int, ami_nom:str):
        if self.test:
            return
        
        def succes(rep):
            self.ami_accept.emit(rep.get('new_friend_id'))
            self.retirer_demande(ami_id=ami_id)
        def erreur(e):
            print(f"erreur lors de l'acceptation de l'ami {ami_nom} : {e}")

        self.requettes_manager.executer(func=lambda : self.session.gestionnaire_amis.accepter_demande_ami(nom_ami=ami_nom, ami_id=ami_id), func_succes=succes, func_erreur=erreur)

    def refuser_demande(self, ami_id:int):
        if self.test:
            return
        
        def succes(rep):
            self.retirer_demande(ami_id=ami_id)
        def erreur(e):
            print(f"erreur lors de la rejection de la demande de l'ami avec l'id : {ami_id} : {e}")
        
        self.requettes_manager.executer(func=lambda : self.session.gestionnaire_amis.refuser_demande_ami(ami_id=ami_id), func_succes=succes, func_erreur=erreur)

    def ajouter_demande(self, ami_id:int, ami_nom:str=None):
        if not ami_nom:
            ami_nom = self.session.cache.ami_par_id(ami_id).username

        w = QWidget()
        l = QHBoxLayout()
        w.setLayout(l)
        label = QLabel(ami_nom)
        bouton_acc = BoutonCustom(taille=(25, 25), chemin_image=obtenir_vrai_chemin("images/accept.svg"), custom_command=lambda ami_id=ami_id, ami_nom=ami_nom: self.accepter_demande(ami_id, ami_nom))
        bouton_ref = BoutonCustom(taille=(25, 25), chemin_image=obtenir_vrai_chemin("images/deny.svg"), custom_command=lambda ami_id=ami_id, ami_nom=ami_nom: self.refuser_demande(ami_id, ami_nom))
        
        l.addWidget(label)
        l.addWidget(bouton_acc)
        l.addWidget(bouton_ref)
        self.widget_recues.ajouter_item(data=ami_id, widget=w)
    
    def retirer_demande(self, ami_id:int):
        self.widget_recues.retirer_item(data=ami_id)

class InterfaceDemandesEnvoyees(QWidget):
    def __init__(self, session, test):
        super().__init__()

        self.session = session
        self.test = test

        if not self.test:
            self.requettes_manager = session.requettes_manager

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.widget_envoyees = ListeElements()
        self.layout.addWidget(self.widget_envoyees)

        self.demandes:list[int] = []
        if not self.test:
            self._trouver_demandes_envoyees()

        self._faire_ui()
    
    def _trouver_demandes_envoyees(self):
        def succes(rep):
            if rep.get('sent_friend_requests_ids') == []:
                self.demandes = []
                return
            self.demandes = [fr.get('receiver_id') for fr in rep.get('sent_friend_requests_ids')]
            self._faire_ui()

        self.requettes_manager.executer(func=self.session.gestionnaire_amis.obtenir_demandes_amis_envoyees, func_succes=succes)

    def _faire_ui(self):
        def succes(rep):    # Ici on a direct une liste de noms en str
            for id_, nom in zip(self.demandes, rep):
                self.ajouter_demande(ami_id=id_, ami_nom=nom)
        
        self.requettes_manager.executer(func=lambda : self.session.gestionnaire_utilisateurs.obtenir_noms(ids=self.demandes), func_succes=succes)
 
    def annuler_demande(self, ami_id:int):
        if self.test:
            return
        
        def succes(rep):
            self.retirer_demande(ami_id=ami_id)
        def erreur(e):
            print(f"erreur lors de l'annulation de la demande pour l'ami avec l'id {ami_id} : {e}")

        self.requettes_manager.executer(func=lambda : self.session.gestionnaire_amis.annuler_demande_ami(ami_id=ami_id), func_succes=succes, func_erreur=erreur)

    def ajouter_demande(self, ami_id:int, ami_nom:str):
        w = QWidget()
        l = QHBoxLayout()
        w.setLayout(l)
        label = QLabel(ami_nom)
        bouton_annuler = BoutonCustom(taille=(25, 25), chemin_image=obtenir_vrai_chemin("images/deny.svg"), custom_command=lambda ami_id=ami_id: self.annuler_demande(ami_id))
        
        l.addWidget(label)
        l.addWidget(bouton_annuler)
        self.widget_envoyees.ajouter_item(data=ami_id, widget=w)
    
    def retirer_demande(self, ami_id:int):
        self.widget_envoyees.retirer_item(data=ami_id)

        