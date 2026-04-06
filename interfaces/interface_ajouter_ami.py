from PyQt6.QtCore import Qt, QSize, QUrl, QEventLoop
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout, QWidget, QPushButton, QLineEdit, QLabel, QMenuBar, QStatusBar, QMenu, QCompleter, QComboBox, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QDoubleSpinBox, QScrollArea, QSpinBox, QSizePolicy, QListWidget, QListWidgetItem
from PyQt6.QtGui import QAction, QPixmap, QIcon, QFont

from interfaces.interface_graphique import BoutonCustom

class InterfaceAjouterAmi(QWidget):
    def __init__(self, session):
        super().__init__()

        self.session = session

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(20, 20, 20, 20)  # Marges autour du contenu
        self.layout.setSpacing(15)  # Espacement entre les widgets
        self.setLayout(self.layout)

        # Titre principal (gros et gras)
        label_ajouter = QLabel("Ajouter")
        font_titre = QFont()
        font_titre.setPointSize(16)
        font_titre.setBold(True)
        label_ajouter.setFont(font_titre)
        label_ajouter.setStyleSheet("color: #ffffff;")

        # Description (plus petit et gris)
        label_description = QLabel("Tu peux ajouter des amis grâce à leur nom.")
        font_description = QFont()
        font_description.setPointSize(10)
        label_description.setFont(font_description)
        label_description.setStyleSheet("color: #b9bbbe; margin-bottom: 10px;")

        # Champ de recherche avec style
        self.recherche_qqn = QLineEdit()
        self.recherche_qqn.setPlaceholderText("Tu peux ajouter des amis grâce à leur nom...")
        self.recherche_qqn.setStyleSheet("""
            QLineEdit {
                background-color: #2f3136;
                color: #ffffff;
                border: 1px solid #202225;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #5865F2;
            }
        """)
        style = """QPushButton {
            background-color: #5865F2;
            color: white;
            border-radius: 8px;
            border: none;
            padding: 12px 20px;
            font-size: 14px;
            font-weight: bold;
        }

        QPushButton:hover {
            background-color: #4752C4;
        }

        QPushButton:focus {
            outline: none;
            border: none;
        }
        """
        bouton_ajouter = BoutonCustom(texte="Envoyer une demande", taille=(200, 45), style=style, custom_command=self.envoyer_demande)

        # Widget contenant le champ + bouton
        widget_recherche = QWidget()
        layout_recherche = QHBoxLayout()
        layout_recherche.setSpacing(10)
        layout_recherche.setContentsMargins(0, 0, 0, 0)
        layout_recherche.addWidget(self.recherche_qqn)
        layout_recherche.addWidget(bouton_ajouter)
        widget_recherche.setLayout(layout_recherche)

        # Ajout des widgets au layout principal
        self.layout.addWidget(label_ajouter)
        self.layout.addWidget(label_description)
        self.layout.addWidget(widget_recherche)

        # Ajouter un stretch pour pousser le contenu vers le haut
        self.layout.addStretch()

    def envoyer_demande(self):
        def succes(rep):
            print('Demande envoyée avec succès')
            son_id = rep.get('receiver_id')
            print(f'rep : {rep}')

        def erreur(e):
            print("Erreur lors de l'envoi de la demande")

        nom = self.recherche_qqn.text()
        self.session.requettes_manager.executer(func=lambda : self.session.gestionnaire_amis.demander_en_ami(nom_ami=nom), func_succes=succes, func_erreur=erreur)

