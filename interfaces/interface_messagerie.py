from PyQt6.QtCore import Qt, QSize, QUrl, QEventLoop, pyqtSignal
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout, QWidget, QPushButton, QLineEdit, QLabel, QStatusBar, QCompleter, QComboBox, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QDoubleSpinBox, QScrollArea, QSpinBox, QSizePolicy, QListWidget, QListWidgetItem, QStackedWidget
from PyQt6.QtGui import QAction, QPixmap, QIcon, QFont

from autre_fonctions import obtenir_vrai_chemin

from interfaces.interface_graphique import BoutonCustom, ListeElements, TexteEtImage, LigneCategorie, GroupeBoutons
from interfaces.interface_amis import InterfaceAmis
from interfaces.interface_blocked import InterfaceBlocked
from interfaces.interface_ajouter_ami import InterfaceAjouterAmi
from interfaces.interface_demandes import InterfaceDemandesRecues, InterfaceDemandesEnvoyees
from interfaces.interface_debug import InterfaceDebug
from interfaces.interface_mp import MpManager

from gestionnaires_requetes import GestionAmis, GestionUtilisateurs
from cache import Cache, Ami
from amis import WidgetAmi

class WidgetExtraBouton(QWidget):
    def __init__(self, texte:str, icone:str = None):
        super().__init__()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(10)

        if icone:
            icon_label = QLabel()
            pixmap = QPixmap(icone).scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            icon_label.setPixmap(pixmap)
            layout.addWidget(icon_label)

        text_label = QLabel(texte)
        text_label.setStyleSheet("color: #dcddde; font-size: 11pt;")
        layout.addWidget(text_label)

        layout.addStretch()

class InterfaceMessagerie(QWidget):
    def __init__(self, fenetre_principale:QMainWindow, session, test:bool=False):
        super().__init__()
        self.fenetre_principale = fenetre_principale
        self.session = session
        self.test = test

        if not self.test:
            self.requettes_manager = session.requettes_manager
        self.cache = session.cache

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        '''self.gestionnaire_utilisateurs = GestionUtilisateurs(token=self.token)
        self.gestionnaire_amis = GestionAmis(token=self.token)'''

        self.liste_amis = self.cache.amis_ids()
        if not self.test:
            self.trouver_amis()
            self.trouver_blocked()


        self._connecter_signaux()
        self._faire_ui()

    def _connecter_signaux(self):
        wsb = self.session.ws_bridge

        wsb.new_message_received.connect(self.new_msg)

    def _faire_ui(self):
        self._faire_barre_laterale()
        self._faire_interfaces()
        self._faire_ligne_categorie()

    def _faire_barre_laterale(self):
        widget_barre_laterale = QWidget()
        layout_barre_laterale = QVBoxLayout(widget_barre_laterale)

        self.widget_colonne_contacts = ListeElements(custom_command=self.contact_clique)
        for ami_id in self.liste_amis:
            self.widget_colonne_contacts.ajouter_item(data=ami_id, widget=WidgetAmi(ami_id, self.cache))


        widget_logo = QLabel()


        
        widget_liste_extra_boutons = ListeElements(custom_command=self.extra_bouton_clique)

        widget_liste_extra_boutons.ajouter_item(data="bouton_ami", widget=WidgetExtraBouton(texte="Mes Amis", icone=obtenir_vrai_chemin('images/friends_white.svg')))
        widget_liste_extra_boutons.ajouter_item(data="bouton_demandes", widget=WidgetExtraBouton(texte="Demandes d'ami", icone=obtenir_vrai_chemin('images/demandes.svg')))


        

        layout_barre_laterale.addWidget(widget_liste_extra_boutons)
        layout_barre_laterale.addWidget(self.widget_colonne_contacts)

        self.layout.addWidget(widget_barre_laterale, 0, 0, 2, 1)
    
    def _faire_interfaces(self):
        self.interface = QStackedWidget()
        self.layout.addWidget(self.interface, 1, 1)

        self.interface_amis = InterfaceAmis(amis=self.liste_amis, session=self.session)
        self.interface_blocked = InterfaceBlocked(session = self.session)
        self.interface_ajouter_amis = InterfaceAjouterAmi(session=self.session, test=self.test)
        self.interface_demandes_recues = InterfaceDemandesRecues(session=self.session, test=self.test)
        self.interface_demandes_envoyees = InterfaceDemandesEnvoyees(session=self.session, test=self.test)

        self.mp_manager = MpManager(session=self.session)
        self.interface_mp = self.mp_manager.widget_conv

        self.interface.addWidget(self.interface_amis)
        self.interface_amis.ami_remove.connect(self.remove_friend)
        self.interface_amis.ami_block.connect(self.block_friend)
        self.interface_amis.start_conv.connect(lambda ami_id : self.contact_clique(ami_id=ami_id))
        self.interface.addWidget(self.interface_blocked)
        self.interface_blocked.ami_unblock.connect(self.unblock_friend)
        self.interface.addWidget(self.interface_ajouter_amis)
        self.interface_ajouter_amis.nouv_demande.connect(lambda ami_id, ami_nom: self.interface_demandes_envoyees.ajouter_demande(ami_id=ami_id, ami_nom=ami_nom))
        
        self.interface.addWidget(self.interface_demandes_recues)
        self.interface.addWidget(self.interface_demandes_envoyees)
        self.interface_demandes_recues.ami_accept.connect(self.new_friend)

        self.interface.addWidget(self.interface_mp)
        self.mp_manager.envoi_msg.connect(lambda ami_id, msg : self.send_msg(ami_id, msg))

        self.interface.setCurrentWidget(self.interface_amis)

        if self.test:
            def recevoir_demande():
                pass
            self.interface_debug = InterfaceDebug()

            self.interface.addWidget(self.interface_debug)

    def changer_interface(self, interface):
        if interface == self.interface:
            return

        self.interface.setCurrentWidget(interface)

    def _faire_ligne_categorie(self):
        self.ligne_categorie = QStackedWidget()


        layout_amis = QHBoxLayout()
        label_logo_amis = TexteEtImage(texte="Amis", chemin_image=obtenir_vrai_chemin("images/friends_white.svg"))
        bouton_tous = BoutonCustom(texte="Tous", taille=(75, 30), custom_command=lambda : self.changer_interface(self.interface_amis))
        bouton_blocked = BoutonCustom(texte="Bloqués", taille=(75, 30), custom_command=lambda : self.changer_interface(self.interface_blocked))
        style = """QPushButton {
            background-color: #5865F2;
            color: white;
            border-radius: 12px;
            border: none;
        }

        QPushButton QLabel {
            font-size: 13px;
        }

        QPushButton:hover {
            background-color: #4752C4;
        }

        QPushButton:focus {
            outline: none;
            border: none;
        }
        """
        bouton_ajouter = BoutonCustom(texte="Ajouter", taille=(75, 30), style=style, custom_command=lambda : self.changer_interface(self.interface_ajouter_amis))
        groupe_bouton_amis = GroupeBoutons([bouton_tous, bouton_blocked, bouton_ajouter])
        bouton_tous.setChecked(True)

        layout_amis.addWidget(label_logo_amis)
        layout_amis.addWidget(groupe_bouton_amis)
        layout_amis.addStretch()
        self.categorie_amis = QWidget()
        self.categorie_amis.setLayout(layout_amis)



        layout_demandes = QHBoxLayout()
        label_logo_demandes = TexteEtImage(texte="Demandes", chemin_image=obtenir_vrai_chemin("images/demandes.svg"))
        bouton_recues = BoutonCustom(texte="Reçues", taille=(75, 30), custom_command=lambda : self.changer_interface(self.interface_demandes_recues))
        bouton_envoyees = BoutonCustom(texte="Envoyées", taille=(75, 30), custom_command=lambda : self.changer_interface(self.interface_demandes_envoyees))
        groupe_boutons_demandes = GroupeBoutons([bouton_recues, bouton_envoyees])
        bouton_recues.setChecked(True)

        layout_demandes.addWidget(label_logo_demandes)
        layout_demandes.addWidget(groupe_boutons_demandes)
        layout_demandes.addStretch()
        self.categorie_demandes = QWidget()
        self.categorie_demandes.setLayout(layout_demandes)



        self.ligne_categorie.addWidget(self.categorie_amis)
        self.ligne_categorie.addWidget(self.categorie_demandes)
        self.ligne_categorie.setCurrentWidget(self.categorie_amis)

        self.layout.addWidget(self.ligne_categorie, 0, 1, Qt.AlignmentFlag.AlignTop)

    def extra_bouton_clique(self, item):
        data = item.data(Qt.ItemDataRole.UserRole)
        print(f"Extra bouton cliqué : {data}")

        if data == "bouton_ami":
            self.ligne_categorie.setCurrentWidget(self.categorie_amis)
            self.changer_interface(self.interface_amis)
        elif data == "bouton_demandes":
            self.ligne_categorie.setCurrentWidget(self.categorie_demandes)
            self.changer_interface(self.interface_demandes_recues)
    
    def contact_clique(self, item=None, ami_id:int=None):
        if item:
            ami_id = item.data(Qt.ItemDataRole.UserRole)
        print(f"Ami id cliqué : {ami_id}")
        self.mp_manager.choisir_conv(ami_id)

        self.changer_interface(self.interface_mp)


    def new_friend(self, friend_id:int):
        def succes(rep1):
            def succes2(rep2):
                conv_id = rep1.get('conversation_id')
                ami = Ami.depuis_dict(rep2, conv_id)
                self.cache.upsert_ami(ami)

                self.liste_amis.append(friend_id)
                self.interface_amis.ajouter_ami(friend_id)
                self.widget_colonne_contacts.ajouter_item(data=friend_id, widget=WidgetAmi(friend_id, self.cache))

            self.requettes_manager.executer(func=lambda : self.session.gestionnaire_utilisateurs.obtenir_infos(friend_id), func_succes=succes2, func_erreur=erreur)
        
        def erreur(e):
            print(f"Erreur serveur la création de conv ou d'obtention d'infos avec {friend_id} : {e}")

        self.requettes_manager.executer(func=lambda : self.session.gestionnaire_conv.creer_conv(friend_id), func_succes=succes, func_erreur=erreur)

    def remove_friend(self, friend_id:int, localement:bool=False):
        if friend_id not in self.liste_amis:
            print(f"Impossible de retirer l'ami {friend_id} : introuvable dans self.liste_amis")
        else:
            if localement:
                self.cache.invalider_ami(friend_id)
                self.interface_amis.retirer_ami(friend_id)
                self.widget_colonne_contacts.retirer_item(data=friend_id)
                self.liste_amis.remove(friend_id)
            else:
                def succes(rep):
                    self.cache.invalider_ami(friend_id)
                    self.interface_amis.retirer_ami(friend_id)
                    self.widget_colonne_contacts.retirer_item(data=friend_id)
                    self.liste_amis.remove(friend_id)

                def erreur(e):
                    print(f"Erreur serveur lors de la suppression de {friend_id} : {e}")
                    return
                
                self.requettes_manager.executer(func=lambda : self.session.gestionnaire_amis.enlever_ami(ami_id=friend_id), func_succes=succes, func_erreur=erreur)
    
    def block_friend(self, friend_id:int, localement:bool=False):
        if localement:
            print("succès")
            self.cache.block(friend_id)
            self.interface_blocked.new_blocked(friend_id)
            self.remove_friend(friend_id, True)
        else:
            def succes(rep):
                print("succès")
                self.cache.block(friend_id)
                self.interface_blocked.new_blocked(friend_id)
                self.remove_friend(friend_id, True)

            def erreur(e):
                print(f"Erreur serveur lors du bloquage de {friend_id} : {e}")
                return

            self.requettes_manager.executer(func=lambda : self.session.gestionnaire_amis.bloquer_ami(ami_id=friend_id), func_succes=succes, func_erreur=erreur)

    def unblock_friend(self, friend_id:int, localement:bool=False):
        if localement:
            self.cache.unblock(friend_id)
            self.interface_blocked.unblock(friend_id)
        else:
            def succes(rep):
                self.cache.unblock(friend_id)
                self.interface_blocked.unblock(friend_id)
            
            def erreur(e):
                print(f"Erreur serveur lors du débloquage de {friend_id} : {e}")

            self.requettes_manager.executer(func=lambda : self.session.gestionnaire_amis.debloquer_ami(friend_id), func_succes=succes, func_erreur=erreur)

    def send_msg(self, friend_id:int, msg:str):
        conv_id = self.cache.conv_id_par_ami_id(friend_id)
        def succes(rep):
            msg_id = rep.get('message_id')  # id du message dans la conv
            self.cache.add_msg(id_=friend_id, conv_id=conv_id, auteur_id=self.session.user_info.get('username'), msg=msg)

            self.mp_manager.ajouter_msg(ami_id=friend_id, auteur=self.session.user_info.get('username'), message=msg)
        def erreur(e):
            print(f"Erreur serveur lors de l'envoi d'un message à {friend_id} : {e}")


        self.requettes_manager.executer(func=lambda : self.session.gestionnaire_conv.envoyer_msg(conv_id, msg), func_succes=succes, func_erreur=erreur)

    def new_msg(self, msg_infos:dict):
        print(f'LAAAAAAAAAAA : {msg_infos}')
        if msg_infos.get('sender_id') == self.session.user_id:  # Si le message perçu est en fait un message que l'on a nous même envoyé, on ne fait rien
            return
        
        ami = self.cache.ami_par_id(msg_infos.get("sender_id"))
        self.cache.add_msg(id_=ami.id, conv_id=msg_infos.get("conversation_id"), auteur_id=ami.id, msg=msg_infos.get("content"), timestamp=msg_infos.get('created_at'))
        self.mp_manager.ajouter_msg(ami_id=ami.id, auteur=ami.username, message=msg_infos.get('content'), heure=msg_infos.get('created_at'), pp_id=ami.pp_id)

    def trouver_amis(self) -> None:
        def succes1(rep1):    # Ici rep renvoie direct la liste d'ids
            amis_cache = self.cache.amis_ids()
            if sorted(amis_cache) != sorted(rep1):
                def succes2(rep2):  # Ici renvoie direct une liste de dicos
                    for a in rep2:
                        uid = a.get('user_id')
                        if uid in amis_manquants:
                            self.new_friend(uid)
                        elif uid in amis_en_trop:
                            self.remove_friend(uid, True)
                        else:
                            print(f"uid amis impossible : {uid}")

                amis_manquants = [a for a in rep1 if a not in amis_cache]
                amis_en_trop = [a for a in amis_cache if a not in rep1]
                self.requettes_manager.executer(func=lambda : self.session.gestionnaire_utilisateurs.obtenir_infos_multiples(ids=amis_manquants+amis_en_trop), func_succes=succes2, func_erreur=erreur)


            else:
                self.liste_amis = amis_cache
        def erreur(e):
            print(f"Erreur serveur lors de l'accès à la liste d'amis ou leurs infos : {e}")
            self.liste_amis = []

        self.requettes_manager.executer(func=lambda : self.session.gestionnaire_amis.obtenir_amis(seulement_ids=True), func_succes=succes1, func_erreur=erreur)

    def trouver_blocked(self) -> None:
        def succes1(rep1):    # Ici rep renvoie direct la liste d'ids
            blocked_cache = self.cache.blocked_ids()
            if sorted(blocked_cache) != sorted(rep1):
                def succes2(rep2):  # Ici renvoie direct une liste de dicos
                    for a in rep2:
                        uid = a.get('user_id')
                        if uid in blocked_manquants:
                            self.block_friend(uid, True)
                        elif uid in blocked_en_trop:
                            self.unblock_friend(uid, True)
                        else:
                            print(f"uid blocked impossible : {uid}")

                blocked_manquants = [b for b in rep1 if b not in blocked_cache]
                blocked_en_trop = [b for b in blocked_cache if b not in rep1]
                self.requettes_manager.executer(func=lambda : self.session.gestionnaire_utilisateurs.obtenir_infos_multiples(ids=blocked_manquants+blocked_en_trop), func_succes=succes2, func_erreur=erreur)

            else:
                return
        def erreur(e):
            print(f"Erreur serveur lors de l'accès à la liste de blocked ou leurs infos : {e}")

        self.requettes_manager.executer(func=self.session.gestionnaire_amis.obtenir_blocked_ids, func_succes=succes1, func_erreur=erreur)