from PyQt6.QtCore import Qt, QSize, QUrl, QEventLoop, pyqtSignal
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout, QWidget, QPushButton, QLineEdit, QLabel, QMenuBar, QStatusBar, QMenu, QCompleter, QComboBox, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QDoubleSpinBox, QScrollArea, QSpinBox, QSizePolicy, QListWidget, QListWidgetItem
from PyQt6.QtGui import QAction, QPixmap, QIcon, QFont

from amis import WidgetBlocked
from autre_fonctions import obtenir_vrai_chemin
from interface_graphique import GroupeBoutons, BoutonCustom, ListeElements, TexteEtImage

class InterfaceBlocked(QWidget):
    ami_unblock = pyqtSignal(int)

    def __init__(self, session):
        super().__init__()

        self.session = session
        self.cache = session.cache

        self.layout = QVBoxLayout()
        self._construire_ui()
        self.setLayout(self.layout)
    
    def _construire_ui(self):
        self.rechercher_blocked = QLineEdit()
        self.rechercher_blocked.setPlaceholderText("Rechercher un ami...")
        self.rechercher_blocked.textChanged.connect(self.filtrer)
        self.layout.addWidget(self.rechercher_blocked)

        self.liste_blocked = ListeElements()
        for blocked_id in self.cache.blocked_ids():
            widget_blocked = WidgetBlocked(blocked_id, self.cache)
            widget_blocked.ami_unblock.connect(lambda b : self.ami_unblock.emit(b))
            self.liste_blocked.ajouter_item(data=blocked_id, widget=widget_blocked)
        self.layout.addWidget(self.liste_blocked)
    
    def filtrer(self, texte:str):
        txt = texte.lower()

        for i in range(self.liste_amis.count()):
            item = self.liste_amis.item(i)
            ami_id = item.data(Qt.ItemDataRole.UserRole)

            ami = self.cache.ami_par_id(ami_id)
            if ami:
                nom_correspond = ami.username.lower().startswith(txt)
                item.setHidden(not nom_correspond)  # Masquer si ne correspond pas

    def unblock(self, id_):
        self.liste_blocked.retirer_item(data=id_)
    
    def new_blocked(self, id_):
        widget_blocked = WidgetBlocked(id_, self.cache)
        widget_blocked.ami_unblock.connect(lambda b : self.ami_unblock.emit(b))
        self.liste_blocked.ajouter_item(data=id_, widget=widget_blocked)
