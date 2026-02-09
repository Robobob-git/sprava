from PyQt6.QtCore import Qt, QSize, QUrl, QEventLoop
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout, QWidget, QPushButton, QLineEdit, QLabel, QStatusBar, QCompleter, QComboBox, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QDoubleSpinBox, QScrollArea, QSpinBox, QSizePolicy, QListWidget, QListWidgetItem
from PyQt6.QtGui import QAction, QPixmap, QIcon, QFont

from interface_graphique import ListeElements

class InterfaceDemandes(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()

        self.demandes_recues = []
        self.demandes_envoyees = []

    def _faire_ui_recues(self):
        widget_recues = ListeElements()
        for d in self.demandes_recues:
            l = QHBoxLayout()
            label = QLabel(d.nom)

            widget_recues.ajouter_item(data=d.nom, widget=label)
            

    def changer_type(self):
        pass

        