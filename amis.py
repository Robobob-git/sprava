from PyQt6.QtCore import Qt, QSize, QUrl, QEventLoop
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout, QWidget, QPushButton, QLineEdit, QLabel, QMenuBar, QStatusBar, QMenu, QCompleter, QComboBox, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QDoubleSpinBox, QScrollArea, QSpinBox, QSizePolicy, QListWidget, QListWidgetItem
from PyQt6.QtGui import QAction, QPixmap, QIcon, QFont

class Ami:
    def __init__(self, ami_infos:dict):
        self.username = ami_infos.get("username")
        self.id = ami_infos.get("user_id")
        self.mail = ami_infos.get("mail")
        self.phone = ami_infos.get("phone")
        self.date_of_birth = ami_infos.get("date_of_birth")
        self.avatar_id = ami_infos.get("avatar_id")

        '''self.status = "online"'''

class WidgetAmi(QWidget):
    def __init__(self, ami:Ami, detaillee:bool=False):
        super().__init__()
        self.ami = ami

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(10, 5, 10, 5)
        
        self._construire_widget()

        self.setLayout(self.layout)
    
    def _construire_widget(self):
        pp = QLabel()
        '''pp.setPixmap(ami.pp)
        avatar_label.setFixedSize(40, 40)'''

        # Infos (nom + statut)
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        nom = QLabel(self.ami.username)
        info_layout.addWidget(nom)

        '''status = QLabel(self.ami.status)
        couleur = "#43b581" if self.ami.status == "online" else "#747f8d"
        status.setStyleSheet(f"color: {couleur}; font-size: 9pt;")
        info_layout.addWidget(status)'''



        self.layout.addWidget(pp)
        self.layout.addLayout(info_layout)
        self.layout.addStretch()