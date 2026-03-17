from PyQt6.QtCore import Qt, QSize, QUrl, QEventLoop, pyqtSignal
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout, QWidget, QPushButton, QLineEdit, QLabel, QMenuBar, QStatusBar, QMenu, QCompleter, QComboBox, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QDoubleSpinBox, QScrollArea, QSpinBox, QSizePolicy, QListWidget, QListWidgetItem
from PyQt6.QtGui import QAction, QPixmap, QIcon, QFont

from amis import WidgetAmi
from autre_fonctions import obtenir_vrai_chemin
from interface_graphique import GroupeBoutons, BoutonCustom, ListeElements, TexteEtImage

class InterfaceBlocked(QWidget):
    ami_unblock = pyqtSignal(int)

    def __init__(self, session):
        super().__init__()

        self.session = session

        self.layout = QVBoxLayout()
        self._construire_ui()
        self.setLayout(self.layout)
    
    def _construire_ui(self):
        rechercher_blocked = QLineEdit()
        rechercher_blocked.setPlaceholderText("Rechercher un ami...")
        self.layout.addWidget(rechercher_blocked)

        self.liste_blocked = ListeElements()
        for blocked in self.session.cache.blocked_ids():
            pass
