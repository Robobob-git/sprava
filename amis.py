from PyQt6.QtCore import Qt, QSize, QUrl, QEventLoop, pyqtSignal
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout, QWidget, QPushButton, QLineEdit, QLabel, QMenuBar, QStatusBar, QMenu, QCompleter, QComboBox, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QDoubleSpinBox, QScrollArea, QSpinBox, QSizePolicy, QListWidget, QListWidgetItem
from PyQt6.QtGui import QAction, QPixmap, QIcon, QFont, QCursor

from interface_graphique import BoutonCustom, MenuDeroulable
from autre_fonctions import obtenir_vrai_chemin

class Ami:
    def __init__(self, ami_infos:dict):
        self.username = ami_infos.get("username")
        self.id = ami_infos.get("user_id")
        self.mail = ami_infos.get("mail")
        self.phone = ami_infos.get("phone")
        self.date_of_birth = ami_infos.get("date_of_birth")
        self.avatar_id = ami_infos.get("avatar_id")

        '''self.status = "online"'''

class WidgetAmi(QWidget):
    ami_remove = pyqtSignal(Ami)
    ami_block = pyqtSignal(Ami) # On le crée ici parce que les pyqtSignal sont bizzares

    def __init__(self, ami:Ami, detaillee:bool=False):
        super().__init__()
        self.ami = ami
        self.detaillee = detaillee

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(10, 5, 10, 5)
        
        self._construire_widget()

        self.setLayout(self.layout)
    
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


            action_lancer_conv = QAction("Lancer une conversation")
            action_lancer_conv.triggered.connect(lambda : self.lancer_conv)
            action_retirer = QAction("Retirer l'ami")
            action_retirer.triggered.connect(lambda : self.retirer_ami)
            action_bloquer = QAction("Bloquer l'ami")
            action_bloquer.triggered.connect(lambda : self.bloquer_ami)
            self.menu = MenuDeroulable(actions=[action_lancer_conv, action_retirer, action_bloquer], pos_separateurs=[1])

            self.bouton_menu = BoutonCustom(taille=(25, 25), chemin_image=obtenir_vrai_chemin("images/menu1.svg"))
            self.bouton_menu.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            self.layout.addWidget(self.bouton_message)
            self.layout.addWidget(self.bouton_menu)



    
    def lancer_conv(self, ami):
        print(f'bonjour amongus : {ami}')


    def afficher_menu(self):
        bouton_pos = self.bouton_menu.mapToGlobal(QPoint(0, self.bouton_menu.height() + 5))
        self.menu.exec(bouton_pos)

    def retirer_ami(self, ami):
        print(f'retirer amongus : {ami}')
        pass

    def bloquer_ami(self, ami):
        print(f'bloquer amongus : {ami}')
        pass
