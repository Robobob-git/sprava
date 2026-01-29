from PyQt6.QtCore import Qt, QSize, QUrl, QEventLoop
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout, QWidget, QPushButton, QLineEdit, QLabel, QMenuBar, QStatusBar, QMenu, QCompleter, QComboBox, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QDoubleSpinBox, QScrollArea, QSpinBox, QSizePolicy, QListWidget, QListWidgetItem
from PyQt6.QtGui import QAction, QPixmap, QIcon, QFont

from interface_graphique import BoutonCustom
from gestionnaires_requetes import GestionAmis
from amis import Ami

class WidgetAmi(QWidget):
    def __init__(self, ami:Ami):
        super().__init__()
        self.ami = ami

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(10, 5, 10, 5)

        pp = QLabel()
        '''pp.setPixmap(...)
        avatar_label.setFixedSize(40, 40)'''

        # Infos (nom + statut)
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        status = QLabel(ami.status)
        couleur = "#43b581" if ami.status == "online" else "#747f8d"
        status.setStyleSheet(f"color: {couleur}; font-size: 9pt;")

        self.layout.addWidget(pp)
        self.layout.addLayout(info_layout)
        #self.layout.addStretch()

        self.setLayout(self.layout)



class ColonneContacts(QWidget):
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
            print(f"Ami cliqué : {ami.username}")




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
        widget_colonne_contacts = ColonneContacts(amis=self.liste_amis)
        widget_logo = QLabel()
        widget_bouton_ami = BoutonCustom(texte="Mes Amis", )


        self.layout.addWidget(widget_colonne_contacts, 0, 1)

        #self.bouton1 = BoutonCustom(texte="1", layout_parent=self.layout, ligne=0, colonne=1, nouvelle_page=False)
        #self.bouton2 = BoutonCustom(texte="2", layout_parent=self.layout, ligne=0, colonne=2, nouvelle_page=False)

        self.champ_de_texte = QLineEdit("Ecrire un message...")
        self.layout.addWidget(self.champ_de_texte, 1, 2)