from PyQt6.QtCore import Qt, QSize, QUrl, QEventLoop, pyqtSignal
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout, QWidget, QPushButton, QLineEdit, QLabel, QStatusBar, QCompleter, QComboBox, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QDoubleSpinBox, QScrollArea, QSpinBox, QSizePolicy, QListWidget, QListWidgetItem
from PyQt6.QtGui import QAction, QPixmap, QIcon, QFont
from dataclasses import dataclass

from interfaces.interface_graphique import ListeElements, BoutonCustom

class InterfaceDebug(QWidget):
    receive_request = pyqtSignal(int)

    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.btn_recevoir_demande = BoutonCustom(texte='Recevoir Demande', taille=(100, 50), custom_command=self.recevoir_demande)
        self.layout.addWidget(self.btn_recevoir_demande)


    def recevoir_demande(self):
        self.receive_request.emit(998)