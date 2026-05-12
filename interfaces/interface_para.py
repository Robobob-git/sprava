from PyQt6.QtCore import Qt, QSize, QUrl, QEventLoop, pyqtSignal
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout, QWidget, QPushButton, QLineEdit, QLabel, QStatusBar, QCompleter, QComboBox, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QDoubleSpinBox, QScrollArea, QSpinBox, QSizePolicy, QListWidget, QListWidgetItem
from PyQt6.QtGui import QAction, QPixmap, QIcon, QFont
from dataclasses import dataclass

from interfaces.interface_graphique import ListeElements, BoutonCustom
from autre_fonctions import obtenir_vrai_chemin



class InterfacePara(QWidget):
    def __init__(self, session):
        super().__init__()

        self.session = session

        self.layout = QVBoxLayout(self)

        self.faire_ui()

    def faire_ui(self):
        widget_nom = QWidget()
        nom_layout = QGridLayout(widget_nom)
        nom_layout.addWidget(QLabel("Nom d'utilisateur"), 0, 0)
        nom_layout.addWidget(QLabel(self.session.user_info.get("username")), 0, 1)
        nom_layout.addWidget(BoutonCustom(texte="Modifier", taille=(100, 25), custom_command=self.modifier(1)))
        self.layout.addWidget(widget_nom)

        widget_mail = QWidget()
        mail_layout = QGridLayout(widget_mail)
        mail_layout.addWidget(QLabel("E-Mail"), 0, 0)
        mail = QLabel(self.session.user_info.get("mail"))
        if '@' in mail:
            mail = mail.split('@')[1]
            mail = '**********@'+mail
        else:
            mail = '**********'
        mail_layout.addWidget(mail, 0, 1)
        mail_layout.addWidget(BoutonCustom(texte="Modifier", taille=(100, 25), custom_command=self.modifier(2)))
        self.layout.addWidget(widget_mail)

        widget_num = QWidget()
        num_layout = QGridLayout(widget_num)
        num_layout.addWidget(QLabel("Numéro de Téléphone"), 0, 0)
        num = self.censurer(self.session.user_info.get("phone"), 4)
        num_layout.addWidget(QLabel(num), 0, 1)
        num_layout.addWidget(BoutonCustom(texte="Modifier", taille=(100, 25), custom_command=self.modifier(3)))
        self.layout.addWidget(widget_num)

        widget_mdp = QWidget()
        mdp_layout = QGridLayout(widget_mdp)
        mdp_layout.addWidget(QLabel("Mot de passe"), 0, 0)
        mdp_layout.addWidget(QLabel("[caché]"), 0, 1)
        mdp_layout.addWidget(BoutonCustom(texte="Modifier", taille=(100, 25), custom_command=self.modifier(4)))
        self.layout.addWidget(widget_mdp)

    def censurer(mot:str, nb_visibles:int):
        n = len(mot)
        return '*' * max(0, n - nb_visibles) + mot[-nb_visibles:]   # On prend les "nb_visibles" caractères en partant de la fin