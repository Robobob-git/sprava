from PyQt6.QtCore import Qt, QSize, QUrl, QEventLoop, pyqtSignal, QPoint
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout, QWidget, QPushButton, QLineEdit, QLabel, QMenuBar, QStatusBar, QMenu, QCompleter, QComboBox, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QDoubleSpinBox, QScrollArea, QSpinBox, QSizePolicy, QListWidget, QListWidgetItem
from PyQt6.QtGui import QAction, QPixmap, QIcon, QFont, QCursor

from cache import Cache
from interface_graphique import BoutonCustom, BoutonMenu
from autre_fonctions import obtenir_vrai_chemin

"""class Ami:
    def __init__(self, ami_infos:dict):
        self.username = ami_infos.get("username")
        self.id = ami_infos.get("user_id")
        self.mail = ami_infos.get("mail")
        self.phone = ami_infos.get("phone")
        self.date_of_birth = ami_infos.get("date_of_birth")
        self.avatar_id = ami_infos.get("avatar_id")

        '''self.status = "online"'''

    def __eq__(self, autre):    # Permet de comparer deux instances Ami correctement
        if isinstance(autre, Ami):
            return self.id == autre.id
        return False"""

class WidgetAmi(QWidget):
    ami_remove = pyqtSignal(int)    # On le crée ici parce que les pyqtSignal sont bizzares
    ami_block = pyqtSignal(int)

    def __init__(self, ami_id:int, cache:Cache, detaillee:bool=False):
        super().__init__()
        self.cache = cache
        self.detaillee = detaillee

        self.ami = cache.ami_par_id(ami_id)
        if self.ami:
            self.layout = QHBoxLayout()
            self.layout.setContentsMargins(10, 5, 10, 5)
            
            self._construire_widget()

            self.setLayout(self.layout)
        else:
            print(f'{ami_id} introuvable dans {cache.amis_ids()}')
    
    def _construire_widget(self):
        pp = QLabel()
        '''pp.setPixmap(ami.pp)
        avatar_label.setFixedSize(40, 40)'''
        self.layout.addWidget(pp)

        nom = QLabel(self.ami.username)
        self.layout.addWidget(nom)

        '''status = QLabel(self.ami.status)
        couleur = "#43b581" if self.ami.status == "online" else "#747f8d"
        status.setStyleSheet(f"color: {couleur}; font-size: 9pt;")
        info_layout.addWidget(status)'''

        self.layout.addStretch()

        if self.detaillee:
            self.bouton_message = BoutonCustom(taille=(25, 25), chemin_image=obtenir_vrai_chemin("images/speech_bubble1.svg"), custom_command=lambda a=self.ami: self.lancer_conv(a))

            self.action_retirer = QAction("Retirer l'ami")
            self.action_retirer.triggered.connect(lambda checked, ami=self.ami: self.ami_remove.emit(ami))
            self.action_bloquer = QAction("Bloquer l'ami")
            self.action_bloquer.triggered.connect(lambda checked, ami=self.ami : self.ami_block.emit(ami))
            self.menu = QMenu()
            self.menu.addAction(self.action_retirer)
            self.menu.addAction(self.action_bloquer)
            self.menu.setStyleSheet("""
                QMenu {
                    background-color: #2b2b2b;
                    border: 1px solid #3a3a3a;
                    border-radius: 8px;
                    padding: 6px 0px;
                    min-width: 100px;
                }
                QMenu::item {
                    color: #ffffff;
                    font-size: 14px;
                    padding: 10px 20px;
                    background-color: transparent;
                }
                QMenu::item:selected {
                    background-color: #3a3a3a;
                    border-radius: 4px;
                }
                QMenu::separator {
                    height: 1px;
                    background-color: #3a3a3a;
                    margin: 4px 10px;
                }
            """)
            self.bouton_menu = BoutonMenu(menu=self.menu, taille=(25, 25), chemin_image=obtenir_vrai_chemin("images/menu1.svg"))
            self.bouton_menu.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            '''self.bouton_menu = BoutonCustom(taille=(25, 25), chemin_image=obtenir_vrai_chemin("images/menu1.svg"), custom_command=self.afficher_menu)'''



            self.layout.addWidget(self.bouton_message)
            self.layout.addWidget(self.bouton_menu)



    def afficher_menu(self):
        print('dfghjklm')
        bouton_pos = self.bouton_menu.mapToGlobal(QPoint(0, self.bouton_menu.height() + 5))
        print(f"bouton_pos : {bouton_pos}")
        self.menu.popup(bouton_pos)
    
    def lancer_conv(self, ami):
        print(f'bonjour amongus : {ami}')
