import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QMenu, QLabel, QToolButton
from PyQt6.QtCore import Qt, QPoint, QSize
from PyQt6.QtGui import QAction, QCursor, QIcon

class TestWidget(QWidget):
    def __init__(self, titre, mode):  # mode = "exec", "delayed", "instant"
        super().__init__()
        self.mode = mode
        layout = QVBoxLayout()

        # Titre
        title_label = QLabel(titre)
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #ffffff;")
        layout.addWidget(title_label)

        # Bouton menu
        if mode == "exec":
            self.button = QPushButton("⋮")
            self.button.clicked.connect(self.show_menu_exec)
        else:
            self.button = QToolButton()
            self.button.setText("⋮")
            if mode == "delayed":
                self.button.setPopupMode(QToolButton.ToolButtonPopupMode.DelayedPopup)
            else:  # instant
                self.button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

        self.button.setFixedSize(36, 36)
        self.button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.button.setStyleSheet("""
            background-color: #2b2b2b;
            color: #ffffff;
            border-radius: 6px;
            font-size: 18px;
        """)

        # Menu
        self.menu = QMenu(self)
        self.menu.setStyleSheet("""
            QMenu {
                background-color: #2b2b2b;
                border: 1px solid #3a3a3a;
                border-radius: 8px;
                padding: 6px 0px;
                min-width: 180px;
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
        """)

        # Actions
        action_bloquer = QAction("Bloquer l'ami", self)
        action_bloquer.triggered.connect(lambda: self.on_action("Bloquer l'ami"))
        self.menu.addAction(action_bloquer)

        action_retirer = QAction("Retirer l'ami", self)
        action_retirer.triggered.connect(lambda: self.on_action("Retirer l'ami"))
        self.menu.addAction(action_retirer)

        if mode != "exec":
            self.button.setMenu(self.menu)

        layout.addWidget(self.button, alignment=Qt.AlignmentFlag.AlignCenter)

        # Label résultat
        self.result_label = QLabel("Résultat : aucun")
        self.result_label.setStyleSheet("color: #dcddde; margin-top: 20px;")
        self.result_label.setWordWrap(True)
        layout.addWidget(self.result_label)

        layout.addStretch()
        self.setLayout(layout)

    def show_menu_exec(self):
        button_pos = self.button.mapToGlobal(QPoint(0, self.button.height() + 5))
        self.menu.exec(button_pos)

    def on_action(self, action_name):
        self.result_label.setText(f"✅ Action: {action_name}")
        self.result_label.setStyleSheet("color: #57f287; margin-top: 20px;")
        print(f"[{self.mode}] Action déclenchée : {action_name}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test Menu Options - PyQt6")
        self.setFixedSize(900, 400)
        self.setStyleSheet("background-color: #1e1e1e;")

        # Widget central avec layout horizontal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Ajouter les 3 widgets de test
        widget1 = TestWidget("Option 1:\nQPushButton + exec()", "exec")
        widget2 = TestWidget("Option 2:\nQToolButton + DelayedPopup", "delayed")
        widget3 = TestWidget("Option 3:\nQToolButton + InstantPopup", "instant")

        main_layout.addWidget(widget1)
        main_layout.addWidget(widget2)
        main_layout.addWidget(widget3)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
