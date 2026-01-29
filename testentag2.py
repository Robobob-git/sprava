import sys
from dataclasses import dataclass

from PyQt6.QtCore import Qt, QRect, QSize, QAbstractListModel, QModelIndex
from PyQt6.QtGui import QPainter, QColor, QPixmap, QFont
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QListView,
    QVBoxLayout,
    QStyledItemDelegate,
    QStyle
)


# ----------------------------
# DATA
# ----------------------------
@dataclass
class Ami:
    user_id: int
    username: str
    status: str   # "online" / "offline"
    avatar_path: str | None = None


# ----------------------------
# MODEL
# ----------------------------
class ModeleAmis(QAbstractListModel):
    def __init__(self, amis):
        super().__init__()
        self.amis = amis

    def rowCount(self, parent=QModelIndex()):
        return len(self.amis)

    def data(self, index, role):
        if not index.isValid():
            return None

        ami = self.amis[index.row()]

        if role == Qt.ItemDataRole.UserRole:
            return ami

        return None


# ----------------------------
# DELEGATE
# ----------------------------
class DelegueAmi(QStyledItemDelegate):

    def paint(self, painter: QPainter, option, index):
        ami: Ami = index.data(Qt.ItemDataRole.UserRole)
        rect = option.rect

        # --- fond ---
        if option.state & QStyle.StateFlag.State_Selected:
            painter.fillRect(rect, QColor("#2f3136"))
        elif option.state & QStyle.StateFlag.State_MouseOver:
            painter.fillRect(rect, QColor("#292b2f"))
        else:
            painter.fillRect(rect, QColor("#1e1f22"))

        margin = 10
        avatar_size = 40

        # --- avatar ---
        avatar_rect = QRect(
            rect.left() + margin,
            rect.top() + (rect.height() - avatar_size) // 2,
            avatar_size,
            avatar_size
        )

        avatar = self._charger_avatar(ami, avatar_size)
        painter.drawPixmap(avatar_rect, avatar)

        # --- pseudo ---
        painter.setPen(QColor("white"))
        painter.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        painter.drawText(
            rect.left() + avatar_size + 2 * margin,
            rect.top() + 25,
            ami.username
        )

        # --- statut ---
        couleur_statut = QColor("#43b581") if ami.status == "online" else QColor("#747f8d")
        painter.setPen(couleur_statut)
        painter.setFont(QFont("Arial", 9))
        painter.drawText(
            rect.left() + avatar_size + 2 * margin,
            rect.top() + 45,
            ami.status
        )

    def sizeHint(self, option, index):
        return QSize(250, 60)

    def _charger_avatar(self, ami, size):
        if ami.avatar_path:
            pix = QPixmap(ami.avatar_path)
            if not pix.isNull():
                return pix.scaled(
                    size,
                    size,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )

        # Avatar par défaut (cercle coloré)
        pix = QPixmap(size, size)
        pix.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pix)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor("#5865f2"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(0, 0, size, size)
        painter.end()

        return pix


# ----------------------------
# UI
# ----------------------------
class FenetreTest(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test liste d'amis - PyQt6")
        self.resize(300, 400)

        amis = [
            Ami(1, "Alice", "online"),
            Ami(2, "Bob", "offline"),
            Ami(3, "Charlie", "online"),
            Ami(4, "Diana", "offline"),
            Ami(5, "Eve", "online"),
        ]

        modele = ModeleAmis(amis)

        vue = QListView()
        vue.setModel(modele)
        vue.setItemDelegate(DelegueAmi())
        vue.setMouseTracking(True)
        vue.setStyleSheet("QListView { border: none; }")

        vue.clicked.connect(self.ami_clique)

        layout = QVBoxLayout()
        layout.addWidget(vue)
        self.setLayout(layout)

    def ami_clique(self, index):
        ami = index.data(Qt.ItemDataRole.UserRole)
        print(f"Ami cliqué : {ami.username}")


# ----------------------------
# MAIN
# ----------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenetre = FenetreTest()
    fenetre.show()
    sys.exit(app.exec())
