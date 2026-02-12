import sys
from dataclasses import dataclass

from PyQt6.QtCore import Qt, QAbstractListModel, QModelIndex, QSize
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QListView,
    QPushButton,
    QStyledItemDelegate,
    QStyle,
)
from PyQt6.QtGui import QPainter


# =========================
# 1️⃣ Donnée
# =========================
@dataclass
class Personne:
    nom: str
    age: int


# =========================
# 2️⃣ Modèle
# =========================
class PersonneModel(QAbstractListModel):
    def __init__(self, personnes=None):
        super().__init__()
        self._personnes = personnes or []

    def rowCount(self, parent=QModelIndex()):
        return len(self._personnes)

    def data(self, index, role):
        if not index.isValid():
            return None

        personne = self._personnes[index.row()]

        if role == Qt.ItemDataRole.DisplayRole:
            return f"{personne.nom} ({personne.age} ans)"

        if role == Qt.ItemDataRole.UserRole:
            return personne

        return None

    def ajouter(self, personne):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self._personnes.append(personne)
        self.endInsertRows()

    def supprimer(self, row):
        if 0 <= row < len(self._personnes):
            self.beginRemoveRows(QModelIndex(), row, row)
            self._personnes.pop(row)
            self.endRemoveRows()


# =========================
# 3️⃣ Delegate (dessin custom)
# =========================
class PersonneDelegate(QStyledItemDelegate):
    def paint(self, painter: QPainter, option, index):
        painter.save()

        rect = option.rect
        texte = index.data(Qt.ItemDataRole.DisplayRole)

        # Fond personnalisé
        if option.state & QStyle.StateFlag.State_Selected:
            painter.fillRect(rect, Qt.GlobalColor.darkGray)

        elif option.state & QStyle.StateFlag.State_MouseOver:
            painter.fillRect(rect, Qt.GlobalColor.gray)

        else:
            painter.fillRect(rect, Qt.GlobalColor.transparent)

        # Texte
        painter.drawText(
            rect.adjusted(10, 0, 0, 0),
            Qt.AlignmentFlag.AlignVCenter,
            texte
        )

        painter.restore()

    def sizeHint(self, option, index):
        return QSize(120, 42)


# =========================
# 4️⃣ Liste custom style
# =========================
class ListeElementsView(QListView):
    def __init__(self, parent=None, horizontal=False, custom_command=None):
        super().__init__(parent)

        self.setSpacing(2)

        if horizontal:
            self.setFlow(QListView.Flow.LeftToRight)
            self.setWrapping(False)
            self.setHorizontalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAsNeeded
            )
            self.setVerticalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAlwaysOff
            )

        self.setStyleSheet("""
            QListView {
                background-color: #1e1f22;
                border: none;
            }
        """)

        self.setMouseTracking(True)

        if custom_command:
            self.clicked.connect(custom_command)


# =========================
# 5️⃣ Fenêtre principale
# =========================
class Fenetre(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ListeElements version MVC - PyQt6")

        layout = QVBoxLayout(self)

        self.model = PersonneModel([
            Personne("Alice", 25),
            Personne("Bob", 30),
        ])

        self.liste = ListeElementsView()
        self.liste.setModel(self.model)
        self.liste.setItemDelegate(PersonneDelegate())

        bouton_ajouter = QPushButton("Ajouter")
        bouton_supprimer = QPushButton("Supprimer sélection")

        bouton_ajouter.clicked.connect(
            lambda: self.model.ajouter(Personne("Nouvelle", 20))
        )

        bouton_supprimer.clicked.connect(self.supprimer)

        layout.addWidget(self.liste)
        layout.addWidget(bouton_ajouter)
        layout.addWidget(bouton_supprimer)

    def supprimer(self):
        index = self.liste.currentIndex()
        if index.isValid():
            self.model.supprimer(index.row())


# =========================
# 6️⃣ Lancement
# =========================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenetre = Fenetre()
    fenetre.resize(300, 300)
    fenetre.show()
    sys.exit(app.exec())
