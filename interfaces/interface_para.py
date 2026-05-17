from PyQt6.QtCore import Qt, QSize, QUrl, QEventLoop, pyqtSignal, QFileInfo, QRect
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout, QWidget, QPushButton, QLineEdit, QLabel, QStatusBar, QCompleter, QComboBox, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QDoubleSpinBox, QScrollArea, QSpinBox, QSizePolicy, QListWidget, QListWidgetItem, QStackedWidget, QFileDialog, QFrame
from PyQt6.QtGui import QAction, QPixmap, QIcon, QFont, QImageReader, QImage, QPainter, QPainterPath
from dataclasses import dataclass
from pathlib import Path

from interfaces.interface_graphique import ListeElements, BoutonCustom
from autre_fonctions import obtenir_vrai_chemin, obtenir_user_chemin, obtenir_pp_chemin, changer_pp

def cercler(path_in: str, path_out: str, size: int = 256):
    img = QImage(path_in)
    if img.isNull():
        return False

    # crop carré centré
    cote = min(img.width(), img.height())
    x = (img.width() - cote) // 2
    y = (img.height() - cote) // 2
    square = img.copy(QRect(x, y, cote, cote)).scaled(size, size)

    # masque circulaire
    output = QImage(size, size, QImage.Format.Format_ARGB32)
    output.fill(0)
    painter = QPainter(output)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    path = QPainterPath()
    path.addEllipse(0, 0, size, size)
    painter.setClipPath(path)
    painter.drawImage(0, 0, square)
    painter.end()

    return output.save(path_out, "PNG")

class LignePara(QWidget):
    save = pyqtSignal()
    preview = pyqtSignal()
    annuler_preview = pyqtSignal()

    def __init__(self, titre:QLabel, label:QLabel=None, edit:QLineEdit=None, pp:bool=False, session=None):
        super().__init__()

        self.titre = titre
        self.label = label
        self.edit = edit
        self.pp = pp
        self.session = session

        self.pp_path = ""

        self.layout = QGridLayout(self)
        self.layout.addWidget(self.titre, 0, 0)


        if not self.pp:
            self.entrees = QStackedWidget()
            self.entrees.addWidget(self.label)
            self.entrees.addWidget(self.edit)
            self.entrees.setCurrentWidget(self.label)
            self.layout.addWidget(self.entrees, 1, 0)
        else:
            self.layout.addWidget(self.label, 1, 0)

        self.bouton_modifier = BoutonCustom(texte="Modifier", taille=(100, 25), custom_command=self.mode_modif)
        self.bouton_sauvegarder = BoutonCustom(texte="Sauvegarder", taille=(100, 25), custom_command=self.save.emit)
        self.bouton_annuler = BoutonCustom(texte="Annuler", taille=(100, 25), custom_command=self.mode_base)
        self.boutons_edit = QWidget()

        edit_layout = QHBoxLayout(self.boutons_edit)
        edit_layout.setContentsMargins(0, 0, 0, 0)
        edit_layout.setSpacing(8)
        edit_layout.addWidget(self.bouton_sauvegarder)
        edit_layout.addWidget(self.bouton_annuler)

        self.boutons = QStackedWidget()
        self.boutons.setFixedSize(220, 30)
        self.boutons.addWidget(self.bouton_modifier)
        self.boutons.addWidget(self.boutons_edit)
        self.boutons.setCurrentWidget(self.bouton_modifier)
        self.layout.addWidget(self.boutons, 0, 1, 2, 1, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignHCenter)
    
    def mode_modif(self):
        if self.pp:
            self.choisir_pp()
            self.preview.emit()
        else:
            self.entrees.setCurrentWidget(self.edit)

        self.boutons.setCurrentWidget(self.boutons_edit)

    def mode_base(self):
        if self.pp:
            self.annuler_preview.emit()
        else:
            self.entrees.setCurrentWidget(self.label)

        self.boutons.setCurrentWidget(self.bouton_modifier)

    def choisir_pp(self):
        # 1) Ouvrir le dialogue
        path, _ = QFileDialog.getOpenFileName(self,"Choisir une photo de profil", "", "Images (*.png *.jpg *.jpeg *.webp *.bmp *.gif)") # On fait "path, _ =" parce que QFileDialog renvoie un tuple (fichier, filtre_selectioné) donc on prend que le fichier direct
        if not path:
            return

        # 2) Vérifier taille (5MB)
        talle_bit = QFileInfo(path).size()
        if talle_bit > 5 * 1024 * 1024:
            QMessageBox.warning(self, "Fichier trop grand", "Image > 5MB.")
            return

        # 3) Vérifier que c'est bien une image lisible
        if not QImageReader(path).canRead():
            QMessageBox.warning(self, "Format invalide", "Fichier image non lisible.")
            return

        path_temp = obtenir_user_chemin(user_id=self.session.user_id, fichier="pp_rognee.png")
        if not cercler(path, path_temp, size=256):
            QMessageBox.warning(self, "Erreur", "Recadrage échoué.")
            return
        self.pp_path = path_temp


class InterfacePara(QWidget):
    nouv_nom = pyqtSignal(str)
    nouv_pp = pyqtSignal(str)

    def __init__(self, session):
        super().__init__()

        self.session = session
        self.requettes_manager = self.session.requettes_manager

        self.user_info = self.session.user_info

        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        self.faire_ui()

    def faire_ui(self):
        def _ajouter_sep():
            sep = QFrame()
            sep.setFrameShape(QFrame.Shape.HLine)
            sep.setFrameShadow(QFrame.Shadow.Sunken)
            sep.setStyleSheet("color: #2b2d31;")
            self.layout.addWidget(sep)

        _ajouter_sep()
        self.pp = QLabel()
        pp_path = obtenir_pp_chemin(self.session.user_id, self.user_info['avatar_id'])
        if pp_path == '':
            changer_pp(tailles=50, labels=self.pp, default=True)
        else:
            changer_pp(tailles=50, labels=self.pp, path=pp_path)
        self.pp_ligne = LignePara(titre=QLabel("Photo de profil"), label=self.pp, pp=True, session=self.session)
        self.pp_ligne.preview.connect(lambda : self.modifier_pp(preview=True))
        self.pp_ligne.annuler_preview.connect(self.pp_de_base)
        self.pp_ligne.save.connect(lambda : self.modifier_pp(warning=True))
        self.layout.addWidget(self.pp_ligne)
        _ajouter_sep()
        
        

        nom = self.user_info.get("username")
        self.nom_label = QLabel(nom)
        self.nom_edit = QLineEdit(nom)
        self.nom_ligne = LignePara(titre=QLabel("Nom d'utilisateur"), label=self.nom_label, edit=self.nom_edit, session=self.session)
        self.nom_ligne.save.connect(self.changer_nom)
        self.layout.addWidget(self.nom_ligne)
        _ajouter_sep()

        mail = self.user_info.get("mail")
        if '@' in mail:
            mail = mail.split('@')[1]
            mail = '**********@'+mail
        else:
            mail = '**********'
        self.mail_label = QLabel(mail)
        self.mail_edit = QLineEdit()
        self.mail_ligne = LignePara(titre=QLabel("E-mail"), label=self.mail_label, edit=self.mail_edit, session=self.session)
        self.mail_ligne.save.connect(self.changer_mail)
        self.layout.addWidget(self.mail_ligne)
        _ajouter_sep()

        mdp = "[caché]"
        self.mdp_label = QLabel(mdp)
        self.mdp_edit = QLineEdit()
        self.mdp_ligne = LignePara(titre=QLabel("Mot de passe"), label=self.mdp_label, edit=self.mdp_edit, session=self.session)
        self.mdp_ligne.save.connect(self.changer_mdp)
        self.layout.addWidget(self.mdp_ligne)
        _ajouter_sep()

        self.pp_ligne.setFixedSize(450, 100)
        self.nom_ligne.setFixedSize(400, 80)
        self.mail_ligne.setFixedSize(400, 80)
        self.mdp_ligne.setFixedSize(400, 80)

    def modifier_pp(self, warning:bool=False, preview:bool=False):
        pp_path = self.pp_ligne.pp_path
        
        if pp_path == '':
            if warning:
                QMessageBox.warning(self, "Erreur", "Photo de Profil inchangée")

            self.pp_de_base(pp_path)
            return
        else:
            changer_pp(tailles=50, labels=self.pp, path=pp_path)
        
        if preview:
            return
        
        def succes(rep):
            QMessageBox.information(self, "INFO", "Photo de profil changée avec succès")
            self.nouv_pp.emit(rep['avatar_id'])
            self.pp_ligne.mode_base()

            path_temp = Path(self.pp_ligne.pp_path)
            if path_temp.is_file():
                path_temp.unlink()
        def erreur(rep):
            print('Erreur lors du changement de pp')
            changer_pp(tailles=50, labels=self.pp, default=True)

        self.requettes_manager.executer(func=lambda : self.session.gestionnaire_utilisateurs.changer_pp(pp_path), func_succes=succes, func_erreur=erreur)

    def pp_de_base(self):
        pp_path = obtenir_pp_chemin(self.session.user_id, self.user_info['avatar_id'])
        if pp_path == '':
            changer_pp(tailles=50, labels=self.pp, default=True)
        else:
            changer_pp(tailles=50, labels=self.pp, path=pp_path)

    def changer_nom(self):
        nom = self.nom_edit.text()

        def succes(rep):
            QMessageBox.information(self, "INFO", "Nom de profil changé avec succès")
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
            QMessageBox.information(self, "INFO", "Mail changé avec succès")

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
            QMessageBox.information(self, "INFO", "Mot de passe changée avec succès")
            
            self.mdp_edit.setText("")
            print(f'user info : {self.user_info}')
            self.session.user_info["password"] = mdp
            self.mdp_ligne.mode_base()
        def erreur(e):
            print(f"Erreur lors du changement de mdp")

        self.requettes_manager.executer(func=lambda : self.session.gestionnaire_utilisateurs.changer_mdp(mdp), func_succes=succes, func_erreur=erreur)