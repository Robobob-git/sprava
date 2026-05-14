from PyQt6.QtCore import Qt, QSize, QUrl, QEventLoop, pyqtSignal
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout, QWidget, QPushButton, QLineEdit, QLabel, QStatusBar, QCompleter, QComboBox, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QDoubleSpinBox, QScrollArea, QSpinBox, QSizePolicy, QListWidget, QListWidgetItem, QStackedWidget
from PyQt6.QtGui import QAction, QPixmap, QIcon, QFont
from dataclasses import dataclass

from interfaces.interface_graphique import ListeElements, BoutonCustom
from autre_fonctions import obtenir_vrai_chemin

class LignePara(QWidget):
    def __init__(self, titre:QLabel, label:QLabel, edit:QLineEdit):
        super().__init__()

        self.label = label
        self.edit = edit

        self.layout = QGridLayout(self)
        self.layout.addWidget(titre, 0, 0)

        self.entrees = QStackedWidget()
        self.entrees.addWidget(self.label)
        self.entrees.addWidget(self.edit)
        self.entrees.setCurrentWidget(self.label)
        self.layout.addWidget(self.entrees, 1, 0)

        self.bouton_modifier = BoutonCustom(texte="Modifier", taille=(100, 25), custom_command=self.modifier)
        self.bouton_sauvegarder = BoutonCustom(texte="Sauvegarder", taille=(100, 25), custom_command=self.sauvegarder)
        self.bouton_annuler = BoutonCustom(texte="Annuler", taille=(100, 25), custom_command=self.annuler)
        self.boutons_edit = QWidget()
        edit_layout = QHBoxLayout(self.boutons_edit)
        edit_layout.addWidget(self.bouton_sauvegarder)
        edit_layout.addWidget(self.bouton_annuler)

        self.boutons = QStackedWidget()
        self.boutons.addWidget(self.bouton_modifier)
        self.boutons.addWidget(self.boutons_edit)
        self.boutons.setCurrentWidget(self.bouton_modifier)
        self.layout.addWidget(self.boutons, 0, 1, 2, 1)
    
    def modifier(self):
        self.entrees.setCurrentWidget(self.edit)
        self.boutons.setCurrentWidget(self.boutons_edit)

    def annuler(self):
        self.entrees.setCurrentWidget(self.label)
        self.boutons.setCurrentWidget(self.bouton_modifier)

    def sauvegarder(self):
        print("save")
        pass

class InterfacePara(QWidget):
    def __init__(self, session):
        super().__init__()

        self.session = session

        self.layout = QVBoxLayout(self)

        self.faire_ui()

    def faire_ui(self):
        nom = self.session.user_info.get("username")
        nom_edit = QLineEdit(nom)
        nom_ligne = LignePara(titre=QLabel("Nom d'utilisateur"), label=QLabel(nom), edit=nom_edit)
        self.layout.addWidget(nom_ligne)

        mail = self.session.user_info.get("mail")
        if '@' in mail:
            mail = mail.split('@')[1]
            mail = '**********@'+mail
        else:
            mail = '**********'
        mail_edit = QLineEdit(mail)
        mail_ligne = LignePara(titre=QLabel("E-mail"), label=QLabel(mail), edit=mail_edit)
        self.layout.addWidget(mail_ligne)

        num = self.session.user_info.get("phone")
        if num:
            num = self.censurer(num, 4)
        else:
            num = ''
        num_edit = QLineEdit(num)
        num_ligne = LignePara(titre=QLabel("Numéro de téléphone"), label=QLabel(num), edit=num_edit)
        self.layout.addWidget(num_ligne)

        mdp = "[caché]"
        mdp_edit = QLineEdit()
        mdp_ligne = LignePara(titre=QLabel("Mot de passe"), label=QLabel(mdp), edit=mdp_edit)
        self.layout.addWidget(mdp_ligne)

    def censurer(self, mot:str, nb_visibles:int):
        n = len(mot)
        return '*' * max(0, n - nb_visibles) + mot[-nb_visibles:]   # On prend les "nb_visibles" caractères en partant de la fin
    
