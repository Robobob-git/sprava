import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QToolButton, QVBoxLayout, QMenu
)
from PyQt6.QtGui import QAction

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Menu propre")
        self.resize(300, 200)

        layout = QVBoxLayout(self)

        self.button = QToolButton()
        self.button.setText("⋯")

        menu = QMenu(self)

        menu.addAction("Démarrer un appel vidéo")
        menu.addAction("Démarrer un appel vocal")
        menu.addSeparator()
        menu.addAction("Retirer l'ami")

        self.button.setMenu(menu)
        self.button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

        layout.addWidget(self.button)

app = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(app.exec())
