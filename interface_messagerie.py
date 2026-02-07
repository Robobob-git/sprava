from PyQt6.QtCore import Qt, QSize, QUrl, QEventLoop
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout, QWidget, QPushButton, QLineEdit, QLabel, QMenuBar, QStatusBar, QMenu, QCompleter, QComboBox, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QDoubleSpinBox, QScrollArea, QSpinBox, QSizePolicy, QListWidget, QListWidgetItem
from PyQt6.QtGui import QAction, QPixmap, QIcon, QFont

from autre_fonctions import obtenir_vrai_chemin

from interface_graphique import BoutonCustom, ListeElements
from gestionnaires_requetes import GestionAmis
from amis import Ami, WidgetAmi

class WidgetExtraBouton(QWidget):
    def __init__(self, texte: str, icone: str | None=None):
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





'''class ColonneContacts(QWidget):
    def __init__(self, amis:list[Ami]):
        super().__init__()

        self.amis = amis

        self.layout = QVBoxLayout()
        self.liste_contacts = QListWidget()
        self.liste_contacts.setStyleSheet("""
            QListWidget {
                background-color: #1e1f22;
                border: none;
                outline: none;
            }
            QListWidget::item {
                border-bottom: 1px solid #2b2d31;
                outline: none;
            }
            QListWidget::item:hover {
                background-color: #292b2f;
            }
            QListWidget::item:selected {
                background-color: #2f3136;
            }
        """)

        if len(self.amis) != 0:
            for ami in self.amis:
                item = QListWidgetItem(self.liste_contacts)
                item.setSizeHint(QSize(280, 60))
                item.setData(Qt.ItemDataRole.UserRole, ami)

                widget_ami = WidgetAmi(ami)
                self.liste_contacts.setItemWidget(item, widget_ami)

            self.liste_contacts.itemClicked.connect(self.contact_clique)

        self.layout.addWidget(self.liste_contacts)
        self.setLayout(self.layout)

        
        def contact_clique(self, item):
            ami = item.data(Qt.ItemDataRole.UserRole)
            print(f"Ami cliqué : {ami.username}")'''




class InterfaceMessagerie(QWidget):
    def __init__(self, user_info:dict, token:str):
        super().__init__()
        self.user_info = user_info
        self.token = token

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.gestionnaire_amis = GestionAmis(user_id=self.user_info.get('user_id'), token=self.token)
        amis_infos = self.gestionnaire_amis.obtenir_amis(toutes_infos=True)
        self.liste_amis = []
        if amis_infos:
            self.liste_amis = [Ami(a) for a in amis_infos]

        self.faire_interface()
        

    def faire_interface(self):
        self.faire_barre_laterale()
        

        #self.bouton1 = BoutonCustom(texte="1", layout_parent=self.layout, ligne=0, colonne=1, nouvelle_page=False)
        #self.bouton2 = BoutonCustom(texte="2", layout_parent=self.layout, ligne=0, colonne=2, nouvelle_page=False)

        self.champ_de_texte = QLineEdit("Ecrire un message...")
        self.layout.addWidget(self.champ_de_texte, 0, 1)

    def faire_barre_laterale(self):
        widget_barre_laterale = QWidget()
        layout_barre_laterale = QVBoxLayout(widget_barre_laterale)


        widget_colonne_contacts = ListeElements()
        for ami in self.liste_amis:
            widget_colonne_contacts.ajouter_item(data=ami, widget=WidgetAmi(ami))
        widget_colonne_contacts.itemClicked.connect(self.contact_clique)


        widget_logo = QLabel()


        
        widget_liste_extra_boutons = ListeElements()
        widget_liste_extra_boutons.ajouter_item(data="bouton_ami", widget=WidgetExtraBouton(texte="Mes Amis", icone=obtenir_vrai_chemin('images/friends')))
        widget_liste_extra_boutons.itemClicked.connect(self.extra_bouton_clique)
        #widget_bouton_ami = BoutonCustom(texte="Mes Amis", taille=(200, 50), chemin_image=obtenir_vrai_chemin('images/friends.png'), layout_horizontal=True)

        

        layout_barre_laterale.addWidget(widget_liste_extra_boutons)
        layout_barre_laterale.addWidget(widget_colonne_contacts)

        self.layout.addWidget(widget_barre_laterale, 0, 0)
    
    def extra_bouton_clique(self, item):
        data = item.data(Qt.ItemDataRole.UserRole)
        print(f"Extra bouton cliqué : {data}")

        if data == "bouton_ami":
            menu_ami("")

    def contact_clique(self, item):
        ami = item.data(Qt.ItemDataRole.UserRole)
        print(f"Ami cliqué : {ami.username}")