from PyQt6.QtCore import Qt, QSize, QUrl, QEventLoop, pyqtSignal
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout, QWidget, QPushButton, QLineEdit, QLabel, QMenuBar, QStatusBar, QMenu, QCompleter, QComboBox, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QDoubleSpinBox, QScrollArea, QSpinBox, QSizePolicy, QListWidget, QListWidgetItem
from PyQt6.QtGui import QAction, QPixmap, QIcon, QFont

from amis import Ami, WidgetAmi
from autre_fonctions import obtenir_vrai_chemin
from interface_graphique import GroupeBoutons, BoutonCustom, ListeElements, TexteEtImage


class InterfaceAmis(QWidget):
    ami_remove = pyqtSignal(Ami)    # On le crée ici parce que les pyqtSignal sont bizzares
    ami_block = pyqtSignal(Ami)

    def __init__(self, amis:list[Ami]):
        super().__init__()

        self.amis = amis

        self.layout = QVBoxLayout()

        self._construire_ui()
        self.setLayout(self.layout)

    def _construire_ui(self):
        rechercher_ami = QLineEdit()
        rechercher_ami.setPlaceholderText("Rechercher un ami...")
        self.layout.addWidget(rechercher_ami)


        '''self.liste_amis = QScrollArea()
        contenu_liste = QWidget()
        self.liste_amis.setWidgetResizable(True)
        self.liste_amis.setFrameShape(QScrollArea.Shape.NoFrame)
        layout_contenu = QVBoxLayout(contenu_liste)
        for ami in self.amis:
            layout_contenu.addWidget(WidgetAmi(ami=ami, detaillee=True))

        self.liste_amis.setWidget(contenu_liste)
        self.layout.addWidget(self.liste_amis)'''

        self.liste_amis = ListeElements()
        for ami in self.amis:
            widget_ami = WidgetAmi(ami, True)
            widget_ami.ami_remove.connect(lambda ami : self.ami_remove.emit(ami))    # On renvoie un signal plus haut vers interface_messagerie
            widget_ami.ami_block.connect(lambda ami : self.ami_block.emit(ami))      # la même
            self.liste_amis.ajouter_item(data=ami, widget=widget_ami)
        self.liste_amis.itemClicked.connect(self.ami_clique)
        self.layout.addWidget(self.liste_amis)
        
    def ami_clique(self, item):
        data = item.data(Qt.ItemDataRole.UserRole)
        print(f"ami cliqué : {data}")

    def ajouter_ami(self, id_ami:int):
        self.amis.append(ami)
        self.liste_amis.ajouter_item(data=ami, widget=WidgetAmi(ami, True))

    def retirer_ami(self, id_ami:int):
        print(f"truc à retirer : {ami}\nself.liste_amis : {self.amis}")
        self.amis.remove(ami)
        self.liste_amis.retirer_item(data=ami)







