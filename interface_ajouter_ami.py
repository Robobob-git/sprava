from PyQt6.QtCore import Qt, QSize, QUrl, QEventLoop
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout, QWidget, QPushButton, QLineEdit, QLabel, QMenuBar, QStatusBar, QMenu, QCompleter, QComboBox, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QDoubleSpinBox, QScrollArea, QSpinBox, QSizePolicy, QListWidget, QListWidgetItem
from PyQt6.QtGui import QAction, QPixmap, QIcon, QFont

from interface_graphique import BoutonCustom

class InterfaceAjouterAmi(QWidget):
    def __init__(self, session):
        super().__init__()

        self.session = session

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        label_ajouter = QLabel("Ajouter")
        label_description = QLabel("Tu peux ajouter des amis grâce à leur nom")

        self.recherche_qqn = QLineEdit()
        self.recherche_qqn.setPlaceholderText("Tu peux ajouter des amis grâce à leur nom...")
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
        bouton_ajouter = BoutonCustom(texte="Envoyer demande", taille=(150, 30), style=style, custom_command=self.envoyer_demande)
        widget_recherche = QWidget()
        l = QHBoxLayout()
        l.addWidget(self.recherche_qqn)
        l.addWidget(bouton_ajouter)
        widget_recherche.setLayout(l)

        self.layout.addWidget(label_ajouter)
        self.layout.addWidget(label_description)
        self.layout.addWidget(widget_recherche)

    def envoyer_demande(self):
        nom = self.recherche_qqn.text()
        rep = self.session.gestionnaire_amis.demander_en_ami(nom_ami=nom)

        if rep.get('status_code') == 404:
            print("utilisateur introuvable")
            return

        elif rep.get('status_code') == 200:
            print('Demande envoyée avec succès')
            son_id = rep.get('receiver_id')

