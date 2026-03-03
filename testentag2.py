import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QPushButton, QMenu, QLabel
)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QAction, QCursor


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Menu déroulant - Test PyQt6")
        self.setFixedSize(400, 300)
        self.setStyleSheet("background-color: #1e1e1e;")

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Label d'info
        self.label = QLabel("Cliquez sur le bouton ⋮")
        self.label.setStyleSheet("color: #aaaaaa; font-size: 14px; margin-bottom: 20px;")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)

        # Bouton "trois points" comme dans l'image
        self.menu_button = QPushButton("⋮")
        self.menu_button.setFixedSize(36, 36)
        self.menu_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        self.menu_button.setStyleSheet("""
            QPushButton {
                background-color: #2b2b2b;
                color: #ffffff;
                border: none;
                border-radius: 18px;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
            }
            QPushButton:pressed {
                background-color: #444444;
            }
        """)
        self.menu_button.clicked.connect(self.show_menu)
        layout.addWidget(self.menu_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # Création du menu déroulant
        self.dropdown_menu = QMenu(self)
        self.dropdown_menu.setStyleSheet("""
            QMenu {
                background-color: #2b2b2b;
                border: 1px solid #3a3a3a;
                border-radius: 8px;
                padding: 6px 0px;
                min-width: 220px;
            }
            QMenu::item {
                color: #ffffff;
                font-size: 14px;
                padding: 10px 20px;
                background-color: transparent;
            }
            QMenu::item:selected {
                background-color: #3a3a3a;
                border-radius: 4px;
            }
            QMenu::separator {
                height: 1px;
                background-color: #3a3a3a;
                margin: 4px 10px;
            }
        """)

        # --- Actions du menu ---

        # Action 1 : Démarrer un appel vidéo
        action_video = QAction("Bloquer l'ami", self)
        action_video.triggered.connect(lambda: self.on_action("Ami bloqué"))
        self.dropdown_menu.addAction(action_video)

        # Séparateur
        self.dropdown_menu.addSeparator()

        # Action 2 : Retirer l'ami (en rouge)
        action_retirer = QAction("Retirer l'ami", self)
        action_retirer.triggered.connect(lambda: self.on_action("Ami retiré !"))
        self.dropdown_menu.addAction(action_retirer)

    def show_menu(self):
        """Affiche le menu sous le bouton."""
        button_pos = self.menu_button.mapToGlobal(
            QPoint(0, self.menu_button.height() + 5)
        )
        self.dropdown_menu.exec(button_pos)

    def on_action(self, message):
        """Callback générique pour les actions."""
        self.label.setText(f"✅ Action : {message}")
        self.label.setStyleSheet("color: #57f287; font-size: 14px; margin-bottom: 20px;")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())