import sys
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QSizePolicy, QToolButton
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize

from autre_fonctions import obtenir_vrai_chemin


class BoutonCustom():
    def __init__(self, texte:str, taille=(200, 200), marge:int = 0, style:str=None, chemin_image:str = None, custom_command = None, nouvelle_page:bool = False, layout_horizontal:bool=False):
        super().__init__()
        self.custom_custom_command = custom_command
        self.nouvelle_page = nouvelle_page
        
        if not layout_horizontal:
            bouton = QPushButton()
        else:
            bouton = QToolButton()

        bouton.setText(texte)
        bouton.setFixedSize(*taille)

        
        if chemin_image:
            bouton.setIcon(QIcon(chemin_image))
            bouton.setIconSize(taille)

            if not layout_horizontal:
                bouton.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        
        bouton.setStyleSheet(f"""
        QPushButton {{
            background-color: #5865F2;
            border-radius: 8px;
            color: white;
            padding: {marge}px;   /* espace entre bord et contenu */
        }}
        QPushButton:hover {{
            background-color: #4752C4;
        }}
        """)

        if style:
            bouton.setStyleSheet(style)
            
        # Ajoute un évènement quand on clique sur le bouton
        bouton.clicked.connect(self.on_bouton_clicked)

        return bouton

    def on_bouton_clicked(self):
        if self.custom_custom_command:
            self.custom_custom_command()