from PyQt6.QtCore import Qt, QSize, QUrl, QEventLoop
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout, QWidget, QPushButton, QLineEdit, QLabel, QMenuBar, QStatusBar, QMenu, QCompleter, QComboBox, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QDoubleSpinBox, QScrollArea, QSpinBox, QSizePolicy, QDateEdit, QCalendarWidget
from PyQt6.QtGui import QAction, QPixmap, QIcon, QFont

from interfaces.interface_graphique import BoutonCustom
from gestionnaire_threaded import RequettesManager
from gestionnaires_requetes import GestionConnexions
from interfaces.interface_messagerie import InterfaceMessagerie
from session import Session

class InterfaceLogin(QWidget):
    def __init__(self, fenetre_principale:QMainWindow):
        super().__init__()

        self.token = None
        self.user_id = None

        self.fenetre_principale = fenetre_principale

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.requettes_manager = RequettesManager()
        self.gestionnaire_connexions = GestionConnexions()

        self.moyen_connexion_actuel = "Connexion"

        self.faire_interface()

    def faire_interface(self):
        def ajouter_au_layout_avec_titre(titre:str, widget_perso:QWidget, layout):
            w = QWidget()
            l = QVBoxLayout()

            l.addWidget(QLabel(titre))
            l.addWidget(widget_perso)

            w.setLayout(l)
            w.show()

            layout.addWidget(w)


        
        def texte_cliquable(texte_avant:str, texte_a_cliquer:str, action) -> QLabel:
            '''On crée un texte cliquable qui redirigerait normalement vers un lien mais on le fait rediriger vers rien, et on capte l'action de clic'''

            label = QLabel(f'{texte_avant} <a href="signup">{texte_a_cliquer}</a>')
            label.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
            label.setOpenExternalLinks(False)
            label.linkActivated.connect(action)
            return label

        self.mail_widget_connexion = QLineEdit()
        self.mdp_widget_connexion = QLineEdit()
        self.mdp_widget_connexion.setEchoMode(QLineEdit.EchoMode.Password)
        bouton_connexion = BoutonCustom(texte="Connexion", taille=(400, 40), custom_command=self.lancer_connexion)
        switch_vers_inscription = texte_cliquable(texte_avant="Pas de compte ?", texte_a_cliquer="S'inscrire", action=self.changer_moyen_connexion)

        self.pseudo_widget = QLineEdit()
        self.mail_widget_inscription = QLineEdit()
        self.confirmer_mdp = QLineEdit()
        self.mdp_widget_inscription = QLineEdit()
        self.confirmer_mdp.setEchoMode(QLineEdit.EchoMode.Password)
        self.mdp_widget_inscription.setEchoMode(QLineEdit.EchoMode.Password)
        self.date_naiss_widget = QDateEdit()
        self.date_naiss_widget.setCalendarPopup(True)
        calendar = QCalendarWidget()
        calendar.setStyleSheet("background:#202020; color:white;")
        self.date_naiss_widget.setCalendarWidget(calendar)

        bouton_inscription = BoutonCustom(texte="Inscription", taille=(400, 40), custom_command=self.lancer_inscription)
        switch_vers_connexion = texte_cliquable(texte_avant="Déjà un compte ?", texte_a_cliquer="Se connecter", action=self.changer_moyen_connexion)


        self.connexion_widget = QWidget()
        connexion_layout = QVBoxLayout()
        ajouter_au_layout_avec_titre("E-mail", self.mail_widget_connexion, connexion_layout)
        ajouter_au_layout_avec_titre("Mot de passe", self.mdp_widget_connexion, connexion_layout)
        connexion_layout.addWidget(bouton_connexion, alignment=Qt.AlignmentFlag.AlignCenter)
        connexion_layout.addWidget(switch_vers_inscription)
        self.connexion_widget.setLayout(connexion_layout)

        self.inscription_widget = QWidget()
        inscription_layout = QVBoxLayout()
        ajouter_au_layout_avec_titre("Pseudonyme", self.pseudo_widget, inscription_layout)
        ajouter_au_layout_avec_titre("E-mail", self.mail_widget_inscription, inscription_layout)
        ajouter_au_layout_avec_titre("Mot de passe", self.mdp_widget_inscription, inscription_layout)
        ajouter_au_layout_avec_titre("Confirmer mot de passe", self.confirmer_mdp, inscription_layout)
        ajouter_au_layout_avec_titre("Date de naissance", self.date_naiss_widget, inscription_layout)
        inscription_layout.addWidget(bouton_inscription, alignment=Qt.AlignmentFlag.AlignCenter)
        inscription_layout.addWidget(switch_vers_connexion)
        self.inscription_widget.setLayout(inscription_layout)

        self.central = QWidget()
        self.central.setMaximumWidth(450)
        self.central_layout = QVBoxLayout()
        self.central.setLayout(self.central_layout)

        self.central_layout.addWidget(self.connexion_widget)
        self.central_layout.addWidget(self.inscription_widget)
        self.layout.addWidget(self.central, 0, 0, Qt.AlignmentFlag.AlignCenter)

        self.connexion_widget.show()
        self.inscription_widget.hide()
    
    def changer_moyen_connexion(self):
        if self.moyen_connexion_actuel == "Connexion":
            self.connexion_widget.hide()
            self.inscription_widget.show()
            self.moyen_connexion_actuel = "Inscription"
        
        elif self.moyen_connexion_actuel == "Inscription":
            self.inscription_widget.hide()
            self.connexion_widget.show()
            self.moyen_connexion_actuel = "Connexion"

    def lancer_connexion(self):
        def succes(rep):
            print("AAAAAAAAAAAAAAAAAA")
            if rep:
                print(f'rep : {rep}')
                self.token = rep.pop('api_token')
                rep.pop('status_code')
                self.user_info = rep
                self.connexion_confirmee()
            else:
                print(f"Connexion échouée")
        def erreur(e):
            print(f"Erreur lors de la connexion: {e}")


        if self.mail_widget_connexion.text() != "" and self.mdp_widget_connexion.text() != "":
            if self.mail_widget_connexion.text() == "test" and self.mdp_widget_connexion.text() == "test":
                self.connexion_confirmee_test()
                return
            
            mail=self.mail_widget_connexion.text()
            mdp=self.mdp_widget_connexion.text()
            self.requettes_manager.executer(func=lambda : self.gestionnaire_connexions.connexion(mail, mdp), func_succes=succes, func_erreur=erreur)
        else:
            print(f'Veuillez renseigner le mail et le mot de passe')

    
    def lancer_inscription(self):
        def succes(rep):
            if rep:
                self.token = rep.pop('api_token')
                rep.pop('status_code')
                self.user_info = rep
                self.inscription_confirmee()
            else:
                print(f"Inscription échouée")
        def erreur(e):
            print(f"Erreur lors de la connexion: {e}")


        if self.pseudo_widget.text() != "" and self.mail_widget_inscription.text() != "" and self.mdp_widget_inscription.text() != "" and self.confirmer_mdp.text() != "" and self.date_naiss_widget.date().toString("yyyy-MM-dd") != "":
            if self.mdp_widget_inscription.text() == self.confirmer_mdp.text():
                pseudo = self.pseudo_widget.text()
                mail = self.mail_widget_inscription.text()
                mdp = self.mdp_widget_inscription.text()
                date_naissance = self.date_naiss_widget.date().toString("yyyy-MM-dd")
                self.requettes_manager.executer(func=lambda : self.gestionnaire_connexions.inscription(pseudo, mail, mdp, date_naissance), func_succes=succes, func_erreur=erreur) 
            
            else:
                print("Les mots de passe ne correspondent pas")
        else:
            print(f'Veuillez renseigner correctement tous les champs')

    
    def connexion_confirmee(self):
        print(f"token : {self.token}")
        print("Connecté avec succès")
        self.session = Session(user_info=self.user_info, token=self.token, requettes_manager=self.requettes_manager)
        interface_messagerie = InterfaceMessagerie(fenetre_principale=self.fenetre_principale, session=self.session)
        self.fenetre_principale.ajouter_interface(interface=interface_messagerie, ligne=1, col=0)
        self.fenetre_principale.changer_interface(interface_messagerie)

    def connexion_confirmee_test(self):
        print("MODE TEST")
        user_info = {'user_id':999, 'username':'test', 'mail':'test@mail.com', 'phone':None, 'date_of_birth':'2000-01-01'}
        self.session = Session(user_info=user_info, token="", requettes_manager="", test=True)
        interface_messagerie = InterfaceMessagerie(fenetre_principale=self.fenetre_principale, session=self.session, test=True)
        self.fenetre_principale.ajouter_interface(interface=interface_messagerie, ligne=1, col=0)
        self.fenetre_principale.changer_interface(interface_messagerie)

    def inscription_confirmee(self):
        print(f"token : {self.token}")
        self.changer_moyen_connexion()
        QMessageBox.information(self, "INFO", "Compte crée avec succès")
