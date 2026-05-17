from PyQt6.QtCore import Qt, QSize, QUrl, QEventLoop, pyqtSignal, QObject
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout, QWidget, QPushButton, QLineEdit, QLabel, QStatusBar, QCompleter, QComboBox, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QDoubleSpinBox, QScrollArea, QSpinBox, QSizePolicy, QListWidget, QListWidgetItem, QStackedWidget
from PyQt6.QtGui import QAction, QPixmap, QIcon, QFont
from datetime import datetime, timedelta, timezone

from autre_fonctions import obtenir_pp_chemin, download_pp, changer_pp

from interfaces.interface_graphique import BoutonCustom, TexteEtImage

class HeaderMP(QWidget):
    def __init__(self, ami_id:int, session): 
        super().__init__()

        self.session = session

        self.layout = QHBoxLayout(self)
        self.setFixedHeight(50)

        self.ami = self.session.cache.ami_par_id(ami_id)

        self._faire_ui()
    
    def _faire_ui(self):
        self.pp = QLabel()
        self.pp.setFixedSize(40, 40)
        self.modifier_pp(self.ami.pp_id)

        self.nom = QLabel(self.ami.username)

        self.layout.addWidget(self.pp)
        self.layout.addWidget(self.nom)
        self.layout.addStretch()

    def modifier_pp(self, pp_id:str):
        if pp_id is None:
            changer_pp(tailles=40, labels=self.pp, default=True)
            return
        
        pp_path = obtenir_pp_chemin(self.session.user_id, pp_id)
        changer_pp(tailles=40, labels=self.pp, path=pp_path)
    
    def modifier_nom(self, nom:str):
        self.nom.setText(nom)

class MpManager(QObject):
    envoi_msg = pyqtSignal(int, str)

    def __init__(self, session):
        super().__init__()

        self.session = session

        self.headers = {}
        self.mps = {}
        
        self.widget_header = QStackedWidget()
        self.widget_conv = QStackedWidget()


    def ajouter_conv(self, ami_id:int):
        header = HeaderMP(ami_id, self.session)
        self.headers[ami_id] = header
        self.widget_header.addWidget(header)

        conv_id = self.session.cache.conv_id_par_ami_id(ami_id)
        mp = InterfaceMP(conv_id, ami_id, self.session)
        mp.envoi_msg.connect(lambda ami_id, msg : self.envoi_msg.emit(ami_id, msg))
        self.mps[ami_id] = mp
        self.widget_conv.addWidget(mp)

    def supprimer_conv(self, ami_id:int):
        if ami_id not in self.mps.keys():
            print(f"Il n'y a pas de conv avec l'ami d'id : {ami_id}")
            return
        
        widget = self.headers[ami_id]
        self.widget_header.removeWidget(widget)
        widget.deleteLater()
        del self.headers[ami_id]

        widget = self.mps[ami_id]
        self.widget_conv.removeWidget(widget)
        widget.deleteLater()
        del self.mps[ami_id]

    def choisir_conv(self, ami_id:int):
        if ami_id not in self.mps.keys():
            self.ajouter_conv(ami_id)

        self.widget_header.setCurrentWidget(self.headers[ami_id])
        self.widget_conv.setCurrentWidget(self.mps[ami_id])
        self.mps[ami_id].scroll_en_bas()

    def ajouter_msg(self, msg_id:int, ami_id:int, sender_id:int, message:str, pp_id:str, heure=None, avec_cache=False):
        self.mps.get(ami_id).ajouter_msg(msg_id, sender_id, message, pp_id, heure, avec_cache)

class MessageWidget(QWidget):
    def __init__(self, auteur:str, message:str, heure:str = None, pp_path:str=None, montrer_header:bool=True):
        super().__init__()
        self.auteur = auteur
        self.message = message
        
        self.heure = heure
        if self.heure is None:
            self.heure = str(datetime.now().strftime("%H:%M"))
        else:
            heure = datetime.fromisoformat(self.heure)
            heure = heure.replace(tzinfo=timezone.utc).astimezone()  # On adapte avec la timezone car le timestamp renvoyé par le serveur est en UTC sans marqueur de timezone
            if datetime.now().astimezone() - heure >= timedelta(hours=24):  # converit aussi la date actuelle en format voulu pour la comparaison
                self.heure = str(heure.strftime("%Y-%m-%d %H:%M"))  # Affiche la date et l'heure si le msg est plus vieux d'un jour
            else:
                self.heure = str(heure.strftime("%H:%M"))   # Sinon affiche uniquement l'heure

        self.montrer_header = montrer_header
        #self.montrer_header=False
        self.pp_path = pp_path
        
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        
        self._faire_ui()
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
            self.layout.addSpacing(50)
            self.pp = QLabel()
            changer_pp(tailles=30, labels=self.pp, path=self.pp_path, default=True if self.pp_path =='' else False)
            self.layout.addWidget(self.pp, alignment=Qt.AlignmentFlag.AlignTop)
        else:
            # Espace pour aligner avec les messages qui ont un pp_id
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
        self.layout.addStretch()

class InterfaceMP(QWidget):
    envoi_msg = pyqtSignal(int, str)

    def __init__(self, conv_id:int, ami_id:int, session):
        super().__init__()
        
        self.conv_id = conv_id
        self.ami_id = ami_id
        self.session = session

        self.cache = session.cache
        self.user_id = self.session.user_id
        self.user_username = self.session.user_info['username']
        self.ami = self.cache.ami_par_id(ami_id)
        self.messages = []
        self.requettes_manager = self.session.requettes_manager

        self.offset = 0
        self.charge = False

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self._faire_ui()
        self.charger_cache()
    
    def _faire_ui(self):
        self.bouton_charger_plus = QPushButton("Charger plus")
        self.bouton_charger_plus.clicked.connect(self.charger_plus)

        self.zone_scroll = QScrollArea()
        self.zone_scroll.setWidgetResizable(True)

        self.conv = QWidget()
        self.conv_layout = QVBoxLayout(self.conv)
        self.charger_plus_container = QWidget()
        charger_plus_layout = QHBoxLayout(self.charger_plus_container)
        charger_plus_layout.addStretch()
        charger_plus_layout.addWidget(self.bouton_charger_plus)
        charger_plus_layout.addStretch()
        self.conv_layout.addWidget(self.charger_plus_container)

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

        self.layout.addWidget(self.zone_scroll)
        self.layout.addWidget(self.ecrire_widget)
    
    def charger_cache(self):
        messages = self.cache.lire_msgs(self.conv_id)
        self.offset = len(messages)
        self.ajouter_messages(messages, True, False)
        self.comparer_serv(messages)

    def charger_plus(self):
        if self.charge:
            return
        self.charge = True

        def succes(rep):
            msgs = rep.get("messages")
            if not msgs:
                self.charge = False
                return

            msgs = msgs[::-1]  # du plus vieux au plus recent

            sb = self.zone_scroll.verticalScrollBar()
            old_value = sb.value()

            for msg in msgs:
                sender_id = msg["sender_id"]
                if sender_id == self.user_id:
                    pp_id = self.session.user_info["avatar_id"]
                    auteur = self.user_username
                else:
                    pp_id = self.ami.pp_id
                    auteur = self.ami.username

                w = MessageWidget(auteur, msg["content"], msg["created_at"], obtenir_pp_chemin(self.user_id, pp_id), True)
                self.conv_layout.insertWidget(1, w)
                self.messages.insert(0, w)

            sb.setValue(old_value + 1)

            self.offset += len(msgs)
            self.charge = False

        def erreur(e):
            self.charge = False

        self.requettes_manager.executer(func=lambda: self.session.gestionnaire_conv.obtenir_msgs(self.conv_id, limite=50, offset=self.offset), func_succes=succes, func_erreur=erreur)

    def comparer_serv(self, cache_messages:list[dict]):
        def succes(rep):
            print(f'\nMSGS SERVEUR : {rep.get("messages")}')
            serv_messages = rep.get("messages")[::-1]   # Inverse pour avoir du plus vieux au plus récent
            serv_messages_ids = [msg["id"] for msg in serv_messages]
            
            cache_messages_ids = []
            if cache_messages != []:
                cache_messages_ids = [msg["msg_id"] for msg in cache_messages]

            if serv_messages_ids != cache_messages_ids:
                self.cache.nettoyer_conv(self.conv_id)
                self.clear_messages()
                print('AGAGAGGAGAGGAGAGGAGAGAG')
                self.ajouter_messages(serv_messages, False, True)
        def erreur(rep):
            print('Erreur lors de la comparaison avec les messages serveur')

        self.requettes_manager.executer(func=lambda : self.session.gestionnaire_conv.obtenir_msgs(self.conv_id), func_succes=succes, func_erreur=erreur)
    
    def ajouter_msg(self, msg_id:int, sender_id:int, message:str, pp_id:str, heure=None, avec_cache=False):
        if sender_id == self.user_id:
            auteur = self.user_username
        else:
            auteur = self.ami.username
        
        if avec_cache:
            self.cache.add_msg(conv_id=self.conv_id, msg_id=msg_id, sender_id=sender_id, msg=message)

        message_widget = MessageWidget(auteur=auteur, message=message, heure=heure, pp_path=obtenir_pp_chemin(self.user_id, pp_id), montrer_header=True)
        self.conv_layout.insertWidget(1, message_widget)
        '''self.zone_scroll.ensureWidgetVisible(message_widget)    # "Attend" que la taille du widget sois calculée poru bien scroll au plus bas '''
        self.messages.append(message_widget)
        
        self.scroll_en_bas()
    
    def ajouter_messages(self, messages:list[dict], du_cache:bool=False, avec_cache:bool = False):
        for msg in messages:
            sender_id = msg['sender_id']
            if sender_id == self.user_id:
                pp_id = self.session.user_info['avatar_id']
            else:
                pp_id = self.ami.pp_id


            if du_cache:
                self.ajouter_msg(msg_id=msg['msg_id'], sender_id=msg['sender_id'], message=msg['contenu'], pp_id=pp_id, heure=msg['timestamp'])
            else:
                self.ajouter_msg(msg_id=msg['id'], sender_id=msg['sender_id'], message=msg['content'], pp_id=pp_id, heure=msg['created_at'])
           
            if avec_cache:
                if du_cache:
                    self.cache.add_msg(self.conv_id, msg["msg_id"], msg['sender_id'], msg['contenu'], msg['timestamp'])
                else:
                    self.cache.add_msg(self.conv_id, msg["id"], msg['sender_id'], msg['content'], msg['created_at'])

    def clear_messages(self):
        while self.conv_layout.count():
            item = self.conv_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

    def scroll_en_bas(self):
        scrollbar = self.zone_scroll.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def envoyer_message(self):
        texte = self.ecrire_msg.text().strip()
        if texte:
            self.envoi_msg.emit(self.ami_id, texte)
            self.ecrire_msg.clear() # Met vide la zone où on écrit le message à envoyer


