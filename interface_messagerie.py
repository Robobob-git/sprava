from PyQt6.QtCore import Qt, QSize, QUrl, QEventLoop, pyqtSignal
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout, QWidget, QPushButton, QLineEdit, QLabel, QStatusBar, QCompleter, QComboBox, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QDoubleSpinBox, QScrollArea, QSpinBox, QSizePolicy, QListWidget, QListWidgetItem, QStackedWidget
from PyQt6.QtGui import QAction, QPixmap, QIcon, QFont

from autre_fonctions import obtenir_vrai_chemin

from interface_graphique import BoutonCustom, ListeElements, TexteEtImage, LigneCategorie, GroupeBoutons
from interface_amis import InterfaceAmis
from interface_ajouter_ami import InterfaceAjouterAmi
from interface_demandes import InterfaceDemandesRecues, InterfaceDemandesEnvoyees

from gestionnaires_requetes import GestionAmis, GestionUtilisateurs
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

class InterfaceMessagerie(QWidget):
    def __init__(self, fenetre_principale:QMainWindow, user_info:dict, token:str):
        super().__init__()
        self.fenetre_principale = fenetre_principale
        self.user_info = user_info
        self.token = token

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.gestionnaire_utilisateurs = GestionUtilisateurs(token=self.token)
        self.gestionnaire_amis = GestionAmis(token=self.token)
        amis_infos = self.gestionnaire_amis.obtenir_amis(toutes_infos=True)
        self.liste_amis = []
        if amis_infos:
            self.liste_amis = [Ami(a) for a in amis_infos]

        self._faire_ui()
        

    def _faire_ui(self):
        self._faire_barre_laterale()
        self._faire_interfaces()
        self._faire_ligne_categorie()


        
        

        #self.bouton1 = BoutonCustom(texte="1", layout_parent=self.layout, ligne=0, colonne=1, nouvelle_page=False)
        #self.bouton2 = BoutonCustom(texte="2", layout_parent=self.layout, ligne=0, colonne=2, nouvelle_page=False)

        #self.champ_de_texte = QLineEdit("Ecrire un message...")
        #self.layout.addWidget(self.champ_de_texte, 0, 1)

    def _faire_barre_laterale(self):
        widget_barre_laterale = QWidget()
        layout_barre_laterale = QVBoxLayout(widget_barre_laterale)


        widget_colonne_contacts = ListeElements(custom_command=self.contact_clique)
        for ami in self.liste_amis:
            widget_colonne_contacts.ajouter_item(data=ami, widget=WidgetAmi(ami))


        widget_logo = QLabel()


        
        widget_liste_extra_boutons = ListeElements(custom_command=self.extra_bouton_clique)

        widget_liste_extra_boutons.ajouter_item(data="bouton_ami", widget=WidgetExtraBouton(texte="Mes Amis", icone=obtenir_vrai_chemin('images/friends.png')))
        widget_liste_extra_boutons.ajouter_item(data="bouton_demandes", widget=WidgetExtraBouton(texte="Demandes d'ami", icone=obtenir_vrai_chemin('images/demandes.svg')))


        

        layout_barre_laterale.addWidget(widget_liste_extra_boutons)
        layout_barre_laterale.addWidget(widget_colonne_contacts)

        self.layout.addWidget(widget_barre_laterale, 0, 0, 2, 1)
    
    def _faire_interfaces(self):
        self.interface = QStackedWidget()
        self.layout.addWidget(self.interface, 1, 1)

        self.interface_amis = InterfaceAmis(amis=self.liste_amis)
        self.interface_ajouter_amis = InterfaceAjouterAmi(gestionnaire_amis=self.gestionnaire_amis)
        self.interface_demandes_recues = InterfaceDemandesRecues(gestionnaire_utilisateurs=self.gestionnaire_utilisateurs, gestionnaire_amis=self.gestionnaire_amis)
        self.interface_demandes_envoyees = InterfaceDemandesEnvoyees(gestionnaire_utilisateurs=self.gestionnaire_utilisateurs, gestionnaire_amis=self.gestionnaire_amis)

        self.interface.addWidget(self.interface_amis)
        self.interface.addWidget(self.interface_ajouter_amis)

        self.interface.addWidget(self.interface_demandes_recues)
        self.interface.addWidget(self.interface_demandes_envoyees)
        self.interface_demandes_recues.ami_accept.connect(self.new_friend)

        self.interface.setCurrentWidget(self.interface_amis)

    def new_friend(self, friend:Ami):
        self.liste_amis.append(friend)


    def changer_interface(self, interface):
        if interface == self.interface:
            return

        self.interface.setCurrentWidget(interface)

    def _faire_ligne_categorie(self):
        self.ligne_categorie = QStackedWidget()


        layout_amis = QHBoxLayout()
        label_logo_amis = TexteEtImage(texte="Amis", chemin_image=obtenir_vrai_chemin("images/friends.png"))
        bouton_tous = BoutonCustom(texte="Tous", taille=(75, 30), custom_command=lambda : self.changer_interface(self.interface_amis))
        style = """QPushButton {
            background-color: #5865F2;
            color: white;
            border-radius: 12px;
            border: none;
        }

        QPushButton QLabel {
            font-size: 13px;
        }

        QPushButton:hover {
            background-color: #4752C4;
        }

        QPushButton:focus {
            outline: none;
            border: none;
        }
        """
        bouton_ajouter = BoutonCustom(texte="Ajouter", taille=(75, 30), style=style, custom_command=lambda : self.changer_interface(self.interface_ajouter_amis))
        groupe_bouton_amis = GroupeBoutons([bouton_tous, bouton_ajouter])
        bouton_tous.setChecked(True)

        layout_amis.addWidget(label_logo_amis)
        layout_amis.addWidget(groupe_bouton_amis)
        self.categorie_amis = QWidget()
        self.categorie_amis.setLayout(layout_amis)



        layout_demandes = QHBoxLayout()
        label_logo_demandes = TexteEtImage(texte="Demandes", chemin_image=obtenir_vrai_chemin("images/demandes.svg"))
        bouton_recues = BoutonCustom(texte="Reçues", taille=(75, 30), custom_command=lambda : self.changer_interface(self.interface_demandes_recues))
        bouton_envoyees = BoutonCustom(texte="Envoyées", taille=(75, 30), custom_command=lambda : self.changer_interface(self.interface_demandes_envoyees))
        groupe_boutons_demandes = GroupeBoutons([bouton_recues, bouton_envoyees])
        bouton_recues.setChecked(True)

        layout_demandes.addWidget(label_logo_demandes)
        layout_demandes.addWidget(groupe_boutons_demandes)
        self.categorie_demandes = QWidget()
        self.categorie_demandes.setLayout(layout_demandes)



        self.ligne_categorie.addWidget(self.categorie_amis)
        self.ligne_categorie.addWidget(self.categorie_demandes)
        self.ligne_categorie.setCurrentWidget(self.categorie_amis)

        self.layout.addWidget(self.ligne_categorie, 0, 1)

    def extra_bouton_clique(self, item):
        data = item.data(Qt.ItemDataRole.UserRole)
        print(f"Extra bouton cliqué : {data}")

        if data == "bouton_ami":
            self.ligne_categorie.setCurrentWidget(self.categorie_amis)
            self.changer_interface(self.interface_amis)
        elif data == "bouton_demandes":
            self.ligne_categorie.setCurrentWidget(self.categorie_demandes)
            self.changer_interface(self.interface_demandes_recues)

    def contact_clique(self, item):
        ami = item.data(Qt.ItemDataRole.UserRole)
        print(f"Ami cliqué : {ami.username}")