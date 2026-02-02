from PyQt6.QtCore import Qt, QSize, QUrl, QEventLoop
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout, QWidget, QPushButton, QLineEdit, QLabel, QMenuBar, QStatusBar, QMenu, QCompleter, QComboBox, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QDoubleSpinBox, QScrollArea, QSpinBox, QSizePolicy, QListWidget, QListWidgetItem
from PyQt6.QtGui import QAction, QPixmap, QIcon, QFont

from amis import Ami

class InterfaceAmis:
    def __init__(self, amis:list[Ami]):
        self.layout = QVBoxLayout()

    def construire_ui(self):
        widget_tri_amis = QWidget()
        layout_tri_amis = QHBoxLayout()

        