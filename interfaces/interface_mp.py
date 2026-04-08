from PyQt6.QtCore import Qt, QSize, QUrl, QEventLoop, pyqtSignal
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout, QWidget, QPushButton, QLineEdit, QLabel, QStatusBar, QCompleter, QComboBox, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QDoubleSpinBox, QScrollArea, QSpinBox, QSizePolicy, QListWidget, QListWidgetItem, QStackedWidget
from PyQt6.QtGui import QAction, QPixmap, QIcon, QFont
from datetime import datetime

from interfaces.interface_graphique import BoutonCustom, TexteEtImage

class HeaderMP(QWidget):
    def __init__(self): 
        super().__init__()

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.header = None
    
    def changer_header(self, ami_id, cache):
        ami = cache.ami_par_id(ami_id)
        self.header = None

class MpManager:
    def __init__(self, session):
        self.session = session

        self.mps = {}
        self.widget_conv = QStackedWidget()

    def choisir_conv(self, ami_id) -> None:
        if ami_id not in self.mps.keys():
            mp = InterfaceMP(ami_id, self.session)
            self.mps[ami_id] = mp
            self.widget_conv.addWidget(mp)
        self.widget_conv.setCurrentWidget(self.mps[ami_id])

class MessageWidget(QWidget):
    def __init__(self, auteur:str, heure:str, message:str, avatar=None, montrer_header=True):
        super().__init__()
        self.auteur = auteur
        self.heure = heure
        self.message = message
        self.montrer_header = montrer_header
        montrer_header=False
        self.avatar = avatar
        
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        
        self.init_ui()
        self.setStyleSheet("""
            MessageWidget {
                background-color: transparent;
                padding: 2px;
            }
            MessageWidget:hover {
                background-color: rgba(255, 255, 255, 0.05);
            }
        """)
    
    def _faire_ui(self):
        '''self.layout.setContentsMargins(10, 4, 10, 4)
        self.layout.setSpacing(10)'''
        if self.montrer_header:
            self.layout.addWidget(self.avatar, alignment=Qt.AlignmentFlag.AlignTop)
        else:
            # Espace pour aligner avec les messages qui ont un avatar
            self.layout.addSpacing(50)

        msg_layout = QVBoxLayout()
        """msg_layout.setSpacing(2)"""
        if self.montrer_header:
            header_layout = QHBoxLayout()
            msg_layout.addLayout(header_layout)

            nom_label = QLabel(self.auteur)
            nom_label.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")

            heure_label = QLabel(self.heure)
            heure_label.setStyleSheet("color: #888; font-size: 11px;")

            header_layout.addWidget(nom_label)
            header_layout.addWidget(heure_label)
        
        msg_label = QLabel(self.message)
        '''msg_label.setStyleSheet("color: #dcddde; font-size: 13px; line-height: 1.4;")'''
        msg_layout.addWidget(msg_label)

        self.layout.addLayout(msg_layout)
        self.layout.addStrech()

class InterfaceMP(QWidget):
    envoi_msg = pyqtSignal(str)

    def __init__(self, ami_id, session):
        super().__init__()
        
        self.ami_id = ami_id
        self.session = session

        self.cache = session.cache
        self.ami = self.cache.ami_par_id(ami_id)
        self.messages = []


        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self._faire_ui()
    
    def _faire_ui(self):
        '''self.windget_total.setContentsMargins(0, 0, 0, 0)
        self.windget_total.setSpacing(0)'''


        self.zone_scroll = QScrollArea()
        '''self.zone_scroll.setWidgetResizable(True)
        self.zone_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.zone_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #36393f;
            }
            QScrollBar:vertical {
                background-color: #2f3136;
                width: 12px;
            }
            QScrollBar::handle:vertical {
                background-color: #202225;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #18191c;
            }
        """)'''

        self.conv = QWidget()
        '''self.conv.setStyleSheet("background-color: #36393f;")'''
        self.conv_layout = QVBoxLayout()
        self.conv.setLayout(self.conv_layout)
        '''self.conv_layout.setContentsMargins(0, 10, 0, 10)
        self.conv_layout.setSpacing(0)
        self.conv_layout.addStretch()'''

        self.zone_scroll.setWidget(self.conv)


        self.ecrire_widget = QWidget()
        self.ecrire_layout = QHBoxLayout()
        self.ecrire_widget.setLayout(self.ecrire_layout)

        self.ecrire_msg = QLineEdit()
        self.ecrire_msg.setPlaceholderText(f'Envoyer un message à {self.ami.username}')
        self.ecrire_msg.returnPressed.connect(self.envoyer_message) # Envoie le message si on appuie sur entrée

        style = """
            QPushButton {
                background-color: #5865f2;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton QLabel {
            font-size: 13px;
            }
            QPushButton:hover {
                background-color: #4752c4;
            }
            QPushButton:focus {
            outline: none;
            border: none;
            }
        """
        self.bouton_envoyer = BoutonCustom(texte="Envoyer", taille=(100, 30), style=style, custom_command=self.envoyer_message)

        self.ecrire_layout.addWidget(self.ecrire_msg)
        self.ecrire_layout.addWidget(self.bouton_envoyer)

        self.layout.addWidget(self.conv)
        self.layout.addWidget(self.ecrire_widget)
    
    def ajouter_message(self, auteur:str, message:str, heure=None, avatar=None):
        if heure is None:
            heure = datetime.now()
        pass

        message_widget = MessageWidget(auteur, heure, message, avatar, montrer_header=True)

        self.conv_layout.insertWidget(self.conv_layout.count() - 1, message_widget)
        self.messages.append(message_widget)
        
        self.scroll_en_bas()

    def scroll_en_bas(self):
        scrollbar = self.scroll_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def envoyer_message(self):
        texte = self.ecrire_msg.text().strip()
        if texte:
            self.envoi_msg.emit(texte)


