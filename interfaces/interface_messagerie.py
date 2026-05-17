from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QMainWindow, QHBoxLayout, QGridLayout, QWidget, QLabel, QStackedWidget
from PyQt6.QtGui import QPixmap

from autre_fonctions import obtenir_vrai_chemin, obtenir_pp_chemin, download_pp, changer_pp

from interfaces.interface_graphique import BoutonCustom, TexteEtImage, GroupeBoutons

from interfaces.interface_barre_laterale import InterfaceBarreLaterale
from interfaces.interface_amis import InterfaceAmis
from interfaces.interface_blocked import InterfaceBlocked
from interfaces.interface_ajouter_ami import InterfaceAjouterAmi
from interfaces.interface_demandes import InterfaceDemandesRecues, InterfaceDemandesEnvoyees
from interfaces.interface_para import InterfacePara
from interfaces.interface_mp import MpManager

from cache import Ami

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
    deconnexion = pyqtSignal()

    def __init__(self, fenetre_principale:QMainWindow, session):
        super().__init__()
        self.fenetre_principale = fenetre_principale
        self.session = session

        self.requettes_manager = session.requettes_manager
        self.cache = session.cache

        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.layout.setColumnStretch(0, 1)
        self.layout.setColumnStretch(1, 4)

        self.liste_amis = self.cache.amis_ids()
        self.trouver_amis()
        self.trouver_blocked()


        self._faire_ui()
        self._connecter_signaux()

    def _connecter_signaux(self):
        wsb = self.session.ws_bridge


        wsb.new_message_received.connect(self.new_msg)

        wsb.new_friend_request.connect(lambda id_, pseudo: self.interface_demandes_recues.ajouter_demande(id_, pseudo))
        wsb.friend_request_accepted.connect(self.new_friend)
        wsb.friend_request_rejected.connect(self.interface_demandes_envoyees.retirer_demande)
        wsb.friend_request_canceled.connect(self.interface_demandes_envoyees.retirer_demande)

        wsb.friend_removed.connect(lambda id_: self.remove_friend(id_, True))

        wsb.user_updated.connect(self.friend_update)

    def _faire_ui(self):
        self._faire_header_compte()
        self._faire_interfaces()
        self._faire_ligne_categorie()
    
    def _faire_header_compte(self):
        self.header_compte = QWidget()
        layout = QHBoxLayout(self.header_compte)

        self.nom_label = QLabel(self.session.user_info.get("username"))

        self.user_pp = QLabel()
        changer_pp(tailles=30, labels=self.user_pp, default=True)

        bouton_para = BoutonCustom(taille=(25, 25), chemin_image=obtenir_vrai_chemin("images/settings_white.svg"), custom_command=lambda : self.extra_bouton_clique("bouton_compte"))
        bouton_deco = BoutonCustom(taille=(25, 25), chemin_image=obtenir_vrai_chemin("images/disconnect_white.svg"), custom_command=self.deco)

        layout.addWidget(self.user_pp)
        layout.addWidget(self.nom_label)
        layout.addWidget(bouton_para)
        layout.addWidget(bouton_deco)

        self.layout.addWidget(self.header_compte, 0, 0)

    def _faire_interfaces(self):
        self.interface_barre_laterale = InterfaceBarreLaterale(session=self.session, liste_amis=self.liste_amis)
        self.layout.addWidget(self.interface_barre_laterale, 1, 0, 2, 1)
        self.interface_barre_laterale.contact_clique_event.connect(self.contact_clique)
        self.interface_barre_laterale.extra_bouton_clique_event.connect(self.extra_bouton_clique)

        self.interface = QStackedWidget()
        self.layout.addWidget(self.interface, 1, 1)

        self.interface_amis = InterfaceAmis(amis=self.liste_amis, session=self.session)
        self.interface_blocked = InterfaceBlocked(session = self.session)
        self.interface_ajouter_amis = InterfaceAjouterAmi(session=self.session)
        self.interface_demandes_recues = InterfaceDemandesRecues(session=self.session)
        self.interface_demandes_envoyees = InterfaceDemandesEnvoyees(session=self.session)
        self.interface_para = InterfacePara(session = self.session)

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
        self.interface.addWidget(self.interface_para)
        self.interface_para.nouv_nom.connect(self.nom_label.setText)
        self.interface_para.nouv_pp.connect(self.new_pp)
        
        self.interface.addWidget(self.interface_demandes_recues)
        self.interface.addWidget(self.interface_demandes_envoyees)
        self.interface_demandes_recues.ami_accept.connect(self.new_friend)

        self.interface.addWidget(self.interface_mp)
        self.mp_manager.envoi_msg.connect(lambda ami_id, msg : self.send_msg(ami_id, msg))

        self.interface.setCurrentWidget(self.interface_amis)

        # Mise à jour si nécessaire de la pp
        pp_id = self.session.user_info['avatar_id']
        pp_path = obtenir_pp_chemin(self.session.user_id, pp_id)
        if pp_path == '':
            self.new_pp(pp_id)
        else:
            changer_pp(tailles=30, labels=self.user_pp, path=pp_path)

    def changer_interface(self, interface):
        if interface == self.interface:
            return

        self.interface.setCurrentWidget(interface)

    def _faire_ligne_categorie(self):
        self.ligne_categorie = QStackedWidget()

        self.categorie_vide = QWidget()
        lay = QHBoxLayout(self.categorie_vide)
        lay.addWidget

        layout_amis = QHBoxLayout()
        label_logo_amis = TexteEtImage(texte="Amis", chemin_image=obtenir_vrai_chemin("images/friends_white.svg"))
        style = """
        QPushButton {
            background-color: #2b2d31;
            color: white;
            border: none;
            border-radius: 6px;
        }
        QPushButton:checked {
            background-color: #3a3d42;
        }
        QPushButton:hover {
            background-color: #404249;
        }
        QPushButton:focus {
            outline: none;
            border: none;
        }"""
        bouton_tous = BoutonCustom(texte="Tous", taille=(75, 30), style=style, custom_command=lambda : self.changer_interface(self.interface_amis))
        bouton_blocked = BoutonCustom(texte="Bloqués", taille=(75, 30), style=style, custom_command=lambda : self.changer_interface(self.interface_blocked))
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
        groupe_boutons_amis = GroupeBoutons([bouton_tous, bouton_blocked, bouton_ajouter])
        bouton_tous.setChecked(True)

        layout_amis.addWidget(label_logo_amis)
        layout_amis.addWidget(groupe_boutons_amis)
        layout_amis.setAlignment(groupe_boutons_amis, Qt.AlignmentFlag.AlignLeft)
        layout_amis.addStretch()
        layout_amis.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.categorie_amis = QWidget()
        self.categorie_amis.setLayout(layout_amis)



        layout_demandes = QHBoxLayout()
        label_logo_demandes = TexteEtImage(texte="Demandes", chemin_image=obtenir_vrai_chemin("images/demandes_white.svg"))
        style = """
        QPushButton {
            background-color: #2b2d31;
            color: white;
            border-radius: 12px;
            border: none;
            font-size: 12px;
        }
        QPushButton:checked {
            background-color: #3a3d42;
        }
        QPushButton:hover {
            background-color: #404249;
        }
        QPushButton:focus {
            outline: none;
            border: none;
        }
        """
        bouton_recues = BoutonCustom(texte="Reçues", taille=(75, 30), style=style, custom_command=lambda : self.changer_interface(self.interface_demandes_recues))
        bouton_envoyees = BoutonCustom(texte="Envoyées", taille=(75, 30), style=style, custom_command=lambda : self.changer_interface(self.interface_demandes_envoyees))
        groupe_boutons_demandes = GroupeBoutons([bouton_recues, bouton_envoyees])
        bouton_recues.setChecked(True)

        layout_demandes.addWidget(label_logo_demandes)
        layout_demandes.addWidget(groupe_boutons_demandes)
        layout_demandes.setAlignment(groupe_boutons_demandes, Qt.AlignmentFlag.AlignLeft)
        layout_demandes.addStretch()
        self.categorie_demandes = QWidget()
        self.categorie_demandes.setLayout(layout_demandes)


        self.ligne_categorie.addWidget(self.categorie_vide)
        self.ligne_categorie.addWidget(self.mp_manager.widget_header)
        self.ligne_categorie.addWidget(self.categorie_amis)
        self.ligne_categorie.addWidget(self.categorie_demandes)
        self.ligne_categorie.setCurrentWidget(self.categorie_amis)

        self.layout.addWidget(self.ligne_categorie, 0, 1, Qt.AlignmentFlag.AlignTop)

    def extra_bouton_clique(self, data:str):
        if data == "bouton_compte":
            self.ligne_categorie.setCurrentWidget(self.categorie_vide)
            self.changer_interface(self.interface_para)
        if data == "bouton_ami":
            self.ligne_categorie.setCurrentWidget(self.categorie_amis)
            self.changer_interface(self.interface_amis)
        elif data == "bouton_demandes":
            self.ligne_categorie.setCurrentWidget(self.categorie_demandes)
            self.changer_interface(self.interface_demandes_recues)
    
    def contact_clique(self, ami_id:int):
        self.ligne_categorie.setCurrentWidget(self.mp_manager.widget_header)
        self.mp_manager.choisir_conv(ami_id)

        self.changer_interface(self.interface_mp)

    def deco(self):
        self.session.fermer()
        self.deconnexion.emit()

    def new_pp(self, pp_id:str):
        old_pp_id = self.session.user_info["avatar_id"]
        self.session.user_info["avatar_id"] = pp_id
        download_pp(pp_id=pp_id, old_pp_id=old_pp_id, tailles=[30, 50], labels=[self.user_pp, self.interface_para.pp], session=self.session)

    def new_friend(self, friend_id:int):
        def succes(rep1):
            def succes2(rep2):
                conv_id = rep1.get('conversation_id')
                ami = Ami.depuis_dict(rep2, conv_id)
                self.cache.upsert_ami(ami)

                self.liste_amis.append(friend_id)
                self.interface_amis.ajouter_ami(friend_id)
                self.interface_barre_laterale.ajouter_ami(friend_id)

            self.requettes_manager.executer(func=lambda : self.session.gestionnaire_utilisateurs.obtenir_infos(friend_id), func_succes=succes2, func_erreur=erreur)
        
        def erreur(e):
            pass

        self.requettes_manager.executer(func=lambda : self.session.gestionnaire_conv.creer_conv(friend_id), func_succes=succes, func_erreur=erreur)

    def remove_friend(self, friend_id:int, localement:bool=False):
        if friend_id not in self.liste_amis:
            pass
        else:
            if localement:
                self.cache.invalider_ami(friend_id)
                self.interface_amis.retirer_ami(friend_id)
                self.interface_barre_laterale.retirer_ami(friend_id)
                self.liste_amis.remove(friend_id)
            else:
                def succes(rep):
                    self.cache.invalider_ami(friend_id)
                    self.interface_amis.retirer_ami(friend_id)
                    self.interface_barre_laterale.retirer_ami(friend_id)
                    self.liste_amis.remove(friend_id)

                def erreur(e):
                    return
                
                self.requettes_manager.executer(func=lambda : self.session.gestionnaire_amis.enlever_ami(ami_id=friend_id), func_succes=succes, func_erreur=erreur)
    
    def block_friend(self, friend_id:int, localement:bool=False):
        if localement:
            self.cache.block(friend_id)
            self.interface_blocked.new_blocked(friend_id)
            self.remove_friend(friend_id, True)
        else:
            def succes(rep):
                self.cache.block(friend_id)
                self.interface_blocked.new_blocked(friend_id)
                self.remove_friend(friend_id, True)

            def erreur(e):
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
                # Vous lisez vraiment ça ?
            
            def erreur(e):
                pass

            self.requettes_manager.executer(func=lambda : self.session.gestionnaire_amis.debloquer_ami(friend_id), func_succes=succes, func_erreur=erreur)

    def send_msg(self, friend_id:int, msg:str):
        conv_id = self.cache.conv_id_par_ami_id(friend_id)
        def succes(rep):
            self.mp_manager.ajouter_msg(msg_id=rep['message_id'], ami_id=friend_id, sender_id=self.session.user_id, pp_id=self.session.user_info['avatar_id'], message=msg, avec_cache=True)
        def erreur(e):
            pass


        self.requettes_manager.executer(func=lambda : self.session.gestionnaire_conv.envoyer_msg(conv_id, msg), func_succes=succes, func_erreur=erreur)


    def new_msg(self, msg_infos:dict):
        if msg_infos.get('sender_id') == self.session.user_id:  # Si le message perçu est en fait un message que l'on a nous même envoyé, on ne fait rien
            return
        
        ami = self.cache.ami_par_id(msg_infos.get("sender_id"))
        self.mp_manager.ajouter_msg(msg_id=msg_infos['message_id'], ami_id=ami.id, sender_id=msg_infos['sender_id'], message=msg_infos.get('content'), heure=msg_infos.get('created_at'), pp_id=ami.pp_id, avec_cache=True)

    def friend_update(self, friend_id:int, new_pseudo:str, new_pp:str):
        old_ami = self.cache.ami_par_id(friend_id)
        new_ami = Ami(id=friend_id, username=new_pseudo, pp_id=new_pp, mail=old_ami.mail, phone=old_ami.phone, date_of_birth=old_ami.date_of_birth, online=old_ami.online, conv_id=old_ami.conv_id)
        
        if old_ami.username != new_pseudo or old_ami.pp_id != new_pp:
            self.cache.upsert_ami(new_ami)
            

            self.interface_amis.retirer_ami(friend_id)
            self.interface_amis.ajouter_ami(friend_id)

            self.interface_barre_laterale.retirer_ami(friend_id)
            self.interface_barre_laterale.ajouter_ami(friend_id)

            self.mp_manager.supprimer_conv(friend_id)
            self.mp_manager.ajouter_conv(friend_id)
            
            download_pp(pp_id=new_pp, old_pp_id=old_ami.pp_id, labels=self.mp_manager.headers[friend_id].pp, tailles=40, session=self.session)




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
                            pass

                amis_manquants = [a for a in rep1 if a not in amis_cache]
                amis_en_trop = [a for a in amis_cache if a not in rep1]
                self.requettes_manager.executer(func=lambda : self.session.gestionnaire_utilisateurs.obtenir_infos_multiples(ids=amis_manquants+amis_en_trop), func_succes=succes2, func_erreur=erreur)


            else:
                self.liste_amis = amis_cache
        def erreur(e):
            self.liste_amis = []

        self.requettes_manager.executer(func=lambda : self.session.gestionnaire_amis.obtenir_amis(seulement_ids=True), func_succes=succes1, func_erreur=erreur)

    def trouver_blocked(self) -> None:
        def succes1(rep1):    # Ici rep renvoie direct la liste d'ids
            if rep1 is None:
                return
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
                            pass

                blocked_manquants = [b for b in rep1 if b not in blocked_cache]
                blocked_en_trop = [b for b in blocked_cache if b not in rep1]
                self.requettes_manager.executer(func=lambda : self.session.gestionnaire_utilisateurs.obtenir_infos_multiples(ids=blocked_manquants+blocked_en_trop), func_succes=succes2, func_erreur=erreur)

            else:
                return
        def erreur(e):
            pass

        self.requettes_manager.executer(func=self.session.gestionnaire_amis.obtenir_blocked_ids, func_succes=succes1, func_erreur=erreur)