from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QVBoxLayout, QWidget, QLineEdit

from amis import WidgetAmi
from autre_fonctions import obtenir_vrai_chemin
from interfaces.interface_graphique import GroupeBoutons, BoutonCustom, ListeElements, TexteEtImage


class InterfaceAmis(QWidget):
    ami_remove = pyqtSignal(int)    # On le crée ici parce que les pyqtSignal sont bizzares
    ami_block = pyqtSignal(int)
    start_conv = pyqtSignal(int)

    def __init__(self, amis:list[int], session):
        super().__init__()

        self.amis = amis

        self.session = session
        self.cache = session.cache

        self.layout = QVBoxLayout()

        self._construire_ui()
        self.setLayout(self.layout)

    def _construire_ui(self):
        self.rechercher_ami = QLineEdit()
        self.rechercher_ami.setPlaceholderText("Rechercher un ami...")
        self.rechercher_ami.textChanged.connect(self.filtrer)
        self.layout.addWidget(self.rechercher_ami)

        self.liste_amis = ListeElements()
        for ami_id in self.cache.amis_ids():
            self.ajouter_ami(ami_id)
        self.liste_amis.itemDoubleClicked.connect(lambda item : self.start_conv.emit(item.data(Qt.ItemDataRole.UserRole)))
        self.layout.addWidget(self.liste_amis)
    
    def filtrer(self, texte:str):
        txt = texte.lower()

        for i in range(self.liste_amis.count()):
            item = self.liste_amis.item(i)
            ami_id = item.data(Qt.ItemDataRole.UserRole)

            ami = self.cache.ami_par_id(ami_id)
            if ami:
                nom_correspond = ami.username.lower().startswith(txt)
                item.setHidden(not nom_correspond)  # Masquer si ne correspond pas

    def ajouter_ami(self, ami_id:int):
        widget_ami = WidgetAmi(ami_id, self.session, True)
        widget_ami.ami_remove.connect(lambda id_: self.ami_remove.emit(id_))    # On renvoie un signal plus haut vers interface_messagerie
        widget_ami.ami_block.connect(lambda id_: self.ami_block.emit(id_))  # la même
        widget_ami.start_conv.connect(lambda id_: self.start_conv.emit(id_))    # la même
        self.liste_amis.ajouter_item(data=ami_id, widget=widget_ami)

    def retirer_ami(self, ami_id:int):
        self.liste_amis.retirer_item(data=ami_id)







