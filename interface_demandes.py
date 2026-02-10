from PyQt6.QtCore import Qt, QSize, QUrl, QEventLoop
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout, QWidget, QPushButton, QLineEdit, QLabel, QStatusBar, QCompleter, QComboBox, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QDoubleSpinBox, QScrollArea, QSpinBox, QSizePolicy, QListWidget, QListWidgetItem
from PyQt6.QtGui import QAction, QPixmap, QIcon, QFont

from gestionnaires_requetes import GestionAmis
from interface_graphique import ListeElements, BoutonCustom
from autre_fonctions import obtenir_vrai_chemin

class InterfaceDemandes(QWidget):
    def __init__(self, gestionnaire_amis):
        super().__init__()

        self.gestionnaire_amis = gestionnaire_amis

        self.layout = QVBoxLayout()

        self.demandes_recues = []
        self.demandes_envoyees = []

    def _faire_ui_recues(self):
        widget_recues = ListeElements()
        for d in self.demandes_recues:
            l = QHBoxLayout()
            label = QLabel(d.nom)
            bouton_acc = BoutonCustom(taille=(50, 50), chemin_image=obtenir_vrai_chemin("images/accept.svg"), custom_command=self.accepter_demande(d))
            bouton_ref = BoutonCustom(taille=(50, 50), chemin_image=obtenir_vrai_chemin("images/deny.svg"), custom_command=self.refuser_demande(d))


            widget_recues.ajouter_item(data=d.nom, widget=label)
            
    def accepter_demande(self, demande):
        rep = self.gestionnaire_amis.accepter_demande_ami(nom_ami=demande.nom, id_ami=demande.id)
        print(rep)
    def refuser_demande(self, demande):
        pass

    def changer_type(self):
        pass

        