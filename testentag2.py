import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout,
    QPushButton, QButtonGroup, QVBoxLayout, QLabel
)
from PyQt6.QtCore import Qt


class BarreFiltres(QWidget):
    def __init__(self):
        super().__init__()

        layout = QHBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)

        self.group = QButtonGroup(self)
        self.group.setExclusive(True)

        # --- Boutons filtres ---
        self.btn_amis = self.creer_bouton("Amis", checked=True)
        self.btn_en_ligne = self.creer_bouton("En ligne")
        self.btn_tous = self.creer_bouton("Tous")

        for btn in (self.btn_amis, self.btn_en_ligne, self.btn_tous):
            layout.addWidget(btn)
            self.group.addButton(btn)

        # --- Bouton Ajouter (action) ---
        self.btn_ajouter = QPushButton("Ajouter")
        self.btn_ajouter.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_ajouter.setObjectName("ajouter")
        layout.addWidget(self.btn_ajouter)

        self.setStyleSheet(self.style())

        # Signal
        self.group.buttonClicked.connect(self.on_filtre_change)
        self.btn_ajouter.clicked.connect(self.on_ajouter)

    def creer_bouton(self, texte, checked=False):
        btn = QPushButton(texte)
        btn.setCheckable(True)
        btn.setChecked(checked)
        #btn.setCursor(Qt.CursorShape.PointingHandCursor)
        return btn

    def on_filtre_change(self, bouton):
        print("Filtre actif :", bouton.text())

    def on_ajouter(self):
        print("Action : ajouter un ami")

    def style(self):
        return """
        QPushButton {
            background-color: #2b2d31;
            color: white;
            border-radius: 12px;
            padding: 6px 14px;
            border: none;
            font-size: 13px;
        }

        QPushButton:hover {
            background-color: #3a3c43;
        }

        QPushButton:checked {
            background-color: #404249;
        }

        QPushButton#ajouter {
            background-color: #5865F2;
            padding: 6px 16px;
        }

        QPushButton#ajouter:hover {
            background-color: #4752C4;
        }
        """

class Fenetre(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Exemple barre filtres")

        layout = QVBoxLayout(self)
        layout.addWidget(BarreFiltres())
        layout.addStretch()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    fenetre = Fenetre()
    fenetre.resize(400, 120)
    fenetre.show()

    sys.exit(app.exec())
