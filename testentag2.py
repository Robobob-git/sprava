import sys
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PyQt6.QtGui import QPixmap, QPainter, QPainterPath
from PyQt6.QtCore import Qt

from autre_fonctions import obtenir_vrai_chemin

class AvatarCirculaire(QLabel):
    def __init__(self, image_path, taille=80):
        super().__init__()
        self.taille = taille
        self.setFixedSize(taille, taille)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        pixmap = QPixmap(image_path).scaled(
            taille,
            taille,
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation
        )

        self.setPixmap(self._pixmap_circulaire(pixmap))

    def _pixmap_circulaire(self, pixmap):
        masque = QPixmap(self.taille, self.taille)
        masque.fill(Qt.GlobalColor.transparent)

        painter = QPainter(masque)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        path = QPainterPath()
        path.addEllipse(0, 0, self.taille, self.taille)
        painter.setClipPath(path)

        painter.drawPixmap(0, 0, pixmap)
        painter.end()

        return masque

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            print("Avatar cliqué 🟢")

class Fenetre(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Avatar cliquable")

        layout = QVBoxLayout()
        avatar = AvatarCirculaire(obtenir_vrai_chemin('images/accept2.png'), taille=100)

        layout.addWidget(avatar, alignment=Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)

app = QApplication(sys.argv)
fenetre = Fenetre()
fenetre.show()
sys.exit(app.exec())
