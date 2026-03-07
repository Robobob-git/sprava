import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QScrollArea, QLabel, QToolButton, QHBoxLayout, QMenu
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt

class WidgetAmi(QWidget):
    def __init__(self, nom):
        super().__init__()
        layout = QHBoxLayout(self)

        layout.addWidget(QLabel(nom))
        layout.addStretch()

        menu = QMenu()
        menu.addAction(QAction("Retirer l'ami", menu))
        menu.addAction(QAction("Bloquer", menu))

        bouton = QToolButton()
        bouton.setText("⋮")
        bouton.setFixedSize(30, 30)
        bouton.setMenu(menu)
        bouton.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        bouton.setStyleSheet("""
            QToolButton {
                background-color: #3a3c43;
                color: white;
                border-radius: 15px;
                border: none;
                font-size: 16px;
            }
            QToolButton::menu-indicator { image: none; }
        """)
        layout.addWidget(bouton)

app = QApplication(sys.argv)

fenetre = QWidget()
fenetre.setStyleSheet("background-color: #2b2d31;")
fenetre.resize(400, 300)

# ScrollArea qui contient un widget avec un VBoxLayout
scroll = QScrollArea()
scroll.setWidgetResizable(True)
scroll.setFrameShape(QScrollArea.Shape.NoFrame)

contenu = QWidget()
liste_layout = QVBoxLayout(contenu)
liste_layout.setSpacing(2)
liste_layout.addStretch()  # pousse les items vers le haut

# Ajout des items
for nom in ["Alice", "Bob", "Charlie"]:
    w = WidgetAmi(nom)
    liste_layout.insertWidget(liste_layout.count() - 1, w)  # insère avant le stretch

scroll.setWidget(contenu)

layout_principal = QVBoxLayout(fenetre)
layout_principal.addWidget(scroll)

fenetre.show()
sys.exit(app.exec())