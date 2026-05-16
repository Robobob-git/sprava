from PyQt6.QtCore import Qt, QSize, QUrl, QEventLoop, pyqtSignal
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout, QWidget, QPushButton, QLineEdit, QLabel, QStatusBar, QCompleter, QComboBox, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QDoubleSpinBox, QScrollArea, QSpinBox, QSizePolicy, QListWidget, QListWidgetItem, QStackedWidget
from PyQt6.QtGui import QAction, QPixmap, QIcon, QFont
from dataclasses import dataclass

from interfaces.interface_graphique import ListeElements, BoutonCustom
from autre_fonctions import obtenir_vrai_chemin

class LignePara(QWidget):
    save = pyqtSignal()

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

        self.bouton_modifier = BoutonCustom(texte="Modifier", taille=(100, 25), custom_command=self.mode_modif)
        self.bouton_sauvegarder = BoutonCustom(texte="Sauvegarder", taille=(100, 25), custom_command=self.save.emit)
        self.bouton_annuler = BoutonCustom(texte="Annuler", taille=(100, 25), custom_command=self.mode_base)
        self.boutons_edit = QWidget()
        edit_layout = QHBoxLayout(self.boutons_edit)
        edit_layout.addWidget(self.bouton_sauvegarder)
        edit_layout.addWidget(self.bouton_annuler)

        self.boutons = QStackedWidget()
        self.boutons.addWidget(self.bouton_modifier)
        self.boutons.addWidget(self.boutons_edit)
        self.boutons.setCurrentWidget(self.bouton_modifier)
        self.layout.addWidget(self.boutons, 0, 1, 2, 1)
    
    def mode_modif(self):
        self.entrees.setCurrentWidget(self.edit)
        self.boutons.setCurrentWidget(self.boutons_edit)

    def mode_base(self):
        self.entrees.setCurrentWidget(self.label)
        self.boutons.setCurrentWidget(self.bouton_modifier)

class InterfacePara(QWidget):
    nouv_nom = pyqtSignal(str)

    def __init__(self, session):
        super().__init__()

        self.session = session
        self.requettes_manager = self.session.requettes_manager

        self.layout = QVBoxLayout(self)

        self.faire_ui()

    def faire_ui(self):
        nom = self.session.user_info.get("username")
        self.nom_label = QLabel(nom)
        self.nom_edit = QLineEdit(nom)
        self.nom_ligne = LignePara(titre=QLabel("Nom d'utilisateur"), label=self.nom_label, edit=self.nom_edit)
        self.nom_ligne.save.connect(self.changer_nom)
        self.layout.addWidget(self.nom_ligne)

        mail = self.session.user_info.get("mail")
        if '@' in mail:
            mail = mail.split('@')[1]
            mail = '**********@'+mail
        else:
            mail = '**********'
        self.mail_label = QLabel(mail)
        self.mail_edit = QLineEdit()
        self.mail_ligne = LignePara(titre=QLabel("E-mail"), label=self.mail_label, edit=self.mail_edit)
        self.mail_ligne.save.connect(self.changer_mail)
        self.layout.addWidget(self.mail_ligne)

        mdp = "[caché]"
        self.mdp_label = QLabel(mdp)
        self.mdp_edit = QLineEdit()
        self.mdp_ligne = LignePara(titre=QLabel("Mot de passe"), label=self.mdp_label, edit=self.mdp_edit)
        self.mdp_ligne.save.connect(self.changer_mdp)
        self.layout.addWidget(self.mdp_ligne)
    
    def changer_nom(self):
        nom = self.nom_edit.text()

        def succes(rep):
            print('Nom changé')
            self.nouv_nom.emit(nom)

            self.nom_label.setText(nom)
            self.nom_edit.setText(nom)
            self.session.user_info["username"] = nom
            self.nom_ligne.mode_base()
        def erreur(e):
            print(f"Erreur lors du changement de nom")
        
        self.requettes_manager.executer(func=lambda : self.session.gestionnaire_utilisateurs.changer_nom(nom), func_succes=succes, func_erreur=erreur)
    
    def changer_mail(self):
        mail = self.mail_edit.text()

        def succes(rep):
            print('Mail changé')

            if '@' in mail:
                mail = mail.split('@')[1]
                mail = '**********@'+mail
            else:
                mail = '**********'

            self.mail_label.setText(mail)
            self.mail_edit.setText("")
            self.session.user_info["mail"] = mail
            self.mail_ligne.mode_base()
        def erreur(e):
            print(f"Erreur lors du changement de mail")

        self.requettes_manager.executer(func=lambda : self.session.gestionnaire_utilisateurs.changer_mail(mail), func_succes=succes, func_erreur=erreur)
    
    def changer_mdp(self):
        mdp = self.mdp_edit.text()

        def succes(rep):
            print('Mdp changé')
            
            self.mdp_edit.setText("")
            print(f'user info : {self.session.user_info}')
            self.session.user_info["password"] = mdp
            self.mdp_ligne.mode_base()
        def erreur(e):
            print(f"Erreur lors du changement de mdp")

        self.requettes_manager.executer(func=lambda : self.session.gestionnaire_utilisateurs.changer_mdp(mdp), func_succes=succes, func_erreur=erreur)