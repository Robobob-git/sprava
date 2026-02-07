from PyQt6.QtCore import Qt, QSize, QUrl, QEventLoop
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout, QWidget, QPushButton, QLineEdit, QLabel, QMenuBar, QStatusBar, QMenu, QCompleter, QComboBox, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QDoubleSpinBox, QScrollArea, QSpinBox, QSizePolicy, QListWidget, QListWidgetItem
from PyQt6.QtGui import QAction, QPixmap, QIcon, QFont

from amis import Ami
from interface_graphique import GroupeBoutons, BoutonCustom, ListeElements


class InterfaceAmis(QWidget):
    def __init__(self, amis:list[Ami]):
        super().__init__()

        self.amis = amis

        self.layout = QVBoxLayout()

    def construire_ui(self):
        bouton_amis = BoutonCustom(texte="Amis")
        bouton_demandes = BoutonCustom(texte="Demandes")

        boutons_gestion_amis = GroupeBoutons(boutons=[bouton_amis, bouton_demandes])
        bouton_amis.setChecked(True)

        self.layout.addWidget(boutons_gestion_amis)


        widget_recherche_ami = QWidget()
        layout_recherche_ami = QHBoxLayout(widget_recherche_ami)

        rechercher_ami = QLineEdit("Rechercher un ami...")
        bouton_ajouter = BoutonCustom(texte="Ajouter", custom_command=self.ajouter_ami)
        layout_recherche_ami.addWidget(rechercher_ami)
        layout_recherche_ami.addWidget(bouton_ajouter)
        self.layout.addWidget(widget_recherche_ami)


        liste_amis = ListeElements()
        for ami in amisliste_amis.ajouter_item()


    
    def ajouter_ami(self):
        pass






