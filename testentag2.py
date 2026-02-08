import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout
)
from PyQt6.QtCore import Qt


class Header(QWidget):
    def __init__(self):
        super().__init__()

        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)

        # Titre (page actuelle)
        self.title = QLabel("Amis")
        self.title.setObjectName("pageTitle")

        # Bouton Ajouter
        self.add_button = QPushButton("Ajouter")
        self.add_button.setObjectName("addButton")

        layout.addWidget(self.title)
        layout.addStretch()  # pousse le bouton vers la droite
        layout.addWidget(self.add_button)

        self.setLayout(layout)

        # Connexion du bouton
        self.add_button.clicked.connect(self.on_add_clicked)

        # Style (QSS)
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e2f;
            }

            QLabel#pageTitle {
                color: white;
                font-size: 18px;
                font-weight: bold;
            }

            QPushButton#addButton {
                background-color: #6C63FF;
                color: white;
                border-radius: 10px;
                padding: 6px 15px;
            }

            QPushButton#addButton:hover {
                background-color: #7f78ff;
            }
        """)

    def on_add_clicked(self):
        print("Bouton Ajouter cliqué !")


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Exemple PyQt6")

        layout = QVBoxLayout()
        layout.addWidget(Header())

        self.setLayout(layout)


app = QApplication(sys.argv)
window = MainWindow()
window.resize(400, 200)
window.show()
sys.exit(app.exec())
