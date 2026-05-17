from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QLabel
from PyQt6.QtGui import QPixmap

from interfaces.interface_graphique import ListeElements
from autre_fonctions import obtenir_vrai_chemin
from amis import WidgetAmi

class WidgetExtraBouton(QWidget):
    def __init__(self, texte:str, icone:str = None):
        super().__init__()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(10)

        if icone:
            icon_label = QLabel()
            pixmap = QPixmap(icone).scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            icon_label.setPixmap(pixmap)
            layout.addWidget(icon_label)

        text_label = QLabel(texte)
        text_label.setStyleSheet("color: #dcddde; font-size: 11pt;")
        layout.addWidget(text_label)

        layout.addStretch()

class InterfaceBarreLaterale(QWidget):
    contact_clique_event = pyqtSignal(int)
    extra_bouton_clique_event = pyqtSignal(str)

    def __init__(self, session, liste_amis:list):
        super().__init__()

        self.session = session
        self.liste_amis = liste_amis

        self.layout = QVBoxLayout(self)
        
        self.widget_liste_extra_boutons = ListeElements(custom_command=self.extra_bouton_clique)
        self.widget_colonne_contacts = ListeElements(custom_command=self.contact_clique)

        self._faire_ui()

    def _faire_ui(self):
        self.widget_liste_extra_boutons.ajouter_item(data="bouton_compte", widget=WidgetExtraBouton(texte="Mon Compte", icone=obtenir_vrai_chemin('images/settings_white.svg')))
        self.widget_liste_extra_boutons.ajouter_item(data="bouton_ami", widget=WidgetExtraBouton(texte="Mes Amis", icone=obtenir_vrai_chemin('images/friends_white.svg')))
        self.widget_liste_extra_boutons.ajouter_item(data="bouton_demandes", widget=WidgetExtraBouton(texte="Demandes d'ami", icone=obtenir_vrai_chemin('images/demandes_white.svg')))

        for ami_id in self.liste_amis:
            self.widget_colonne_contacts.ajouter_item(data=ami_id, widget=WidgetAmi(ami_id, self.session))

        self.layout.addWidget(self.widget_liste_extra_boutons)
        self.layout.addWidget(self.widget_colonne_contacts)
        self.layout.setStretch(0, 1)
        self.layout.setStretch(1, 4)


    def ajouter_ami(self, ami_id:int):
        self.widget_colonne_contacts.ajouter_item(data=ami_id, widget=WidgetAmi(ami_id, self.session))

    def retirer_ami(self, ami_id:int):
        self.widget_colonne_contacts.retirer_item(data=ami_id)

    def extra_bouton_clique(self, item):
        data = item.data(Qt.ItemDataRole.UserRole)
        self.extra_bouton_clique_event.emit(data)

    def contact_clique(self, item):
        ami_id = item.data(Qt.ItemDataRole.UserRole)
        self.contact_clique_event.emit(ami_id)


    