import requests

LIEN_API = "http://100.30.122.130:8000/" 

class GestionRequetes:
    def __init__(self, token=None):
        self.token = token

    def faire_requete(self, url:str, type_de_r:str, body:dict=None, files=None, path:str=None):
        if self.token is not None:
            headers = {"Authorization": f"{self.token}"}
        else:
            headers = None

        if type_de_r == 'get':
            rep = requests.get(f"{LIEN_API}{url}", headers=headers)

        elif type_de_r == 'post':
            rep = requests.post(f"{LIEN_API}{url}", headers=headers, json=body, files=files)
        
        elif type_de_r == 'delete':
            rep = requests.delete(f"{LIEN_API}{url}", headers=headers, json=body)

        elif type_de_r == 'put':
            rep = requests.put(f"{LIEN_API}{url}", headers=headers, json=body)

        else:
            return


        if rep.status_code == 200:
            if path:
                with open(path, "wb") as f:
                    for chunk in rep.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                return True
            else:
                return rep.json()
        elif rep.status_code == 401:
            pass
        elif rep.status_code == 500:
            pass
        else:
            pass
        return

class GestionUtilisateurs:
    def __init__(self, token):
        self.token = token

        self.gestionnaire_de_requetes = GestionRequetes(token=self.token)
    
    def obtenir_id(self, nom:str) -> int:
        rep = self.gestionnaire_de_requetes.faire_requete(url=f"/user/username?username={nom}", type_de_r='get')
        return rep.get("user_id")

    def obtenir_nom(self, id_:int) -> str:
        rep = self.gestionnaire_de_requetes.faire_requete(url=f"/user?user_id={id_}", type_de_r='get')
        return rep.get("username")
    
    def obtenir_noms(self, ids:list[int]) -> list[str]:
        if ids == []:
            return []
        ids_amis = self.obtenir_infos_multiples(ids=ids)
        return [user.get('username') for user in ids_amis]

    def obtenir_infos(self, id_:int):
        rep = self.gestionnaire_de_requetes.faire_requete(url=f"/user?user_id={id_}", type_de_r="get")
        return rep

    def obtenir_infos_multiples(self, ids:list[int]) -> list:
        if ids == []:
            return

        body = {'user_id' : ids}
        rep = self.gestionnaire_de_requetes.faire_requete(url=f"/user/batch", type_de_r='post', body=body)
        if rep:
            return rep.get('users')
        else:
            return

    def changer_nom(self, nom:str):
        body = {"username" : nom}
        rep = self.gestionnaire_de_requetes.faire_requete(url=f"/me/change_username", type_de_r='post', body=body)
        return rep

    def changer_mail(self, mail:str):
        body = {"mail" : mail}
        rep = self.gestionnaire_de_requetes.faire_requete(url=f"/me/change_mail", type_de_r='post', body=body)
        return rep
    
    def changer_mdp(self, mdp:str):
        body = {"password" : mdp}
        rep = self.gestionnaire_de_requetes.faire_requete(url=f"/me/change_password", type_de_r='post', body=body)
        return rep

    def changer_pp(self, pp_path:str):
        with open(pp_path, "rb") as image_file:
            files = {"file": image_file}
            rep = self.gestionnaire_de_requetes.faire_requete(url=f"/me/change_avatar", type_de_r='post', files=files)
        return rep

class GestionAmis:
    def __init__(self, token):
        self.token = token

        self.gestionnaire_de_requetes = GestionRequetes(token=self.token)
        self.gestion_utilisateurs = GestionUtilisateurs(token=self.token)
    
    def obtenir_amis(self, toutes_infos:bool=False, seulement_ids:bool=False, seulement_noms:bool=False) -> list:
        if not toutes_infos and not seulement_ids and not seulement_noms:
            return
        
        rep = self.gestionnaire_de_requetes.faire_requete(url=f"/me/friends", type_de_r='get')
        friends_ids = rep.get('friends_ids')
        if seulement_ids and not toutes_infos and not seulement_noms:
            return friends_ids
        elif seulement_noms and not toutes_infos and not seulement_ids:
            return self.gestion_utilisateurs.obtenir_noms(ids=friends_ids)
        elif toutes_infos and not seulement_ids and not seulement_noms:
            return self.gestion_utilisateurs.obtenir_infos_multiples(ids=friends_ids)

        else:
            return

    def demander_en_ami(self, nom_ami:str=None, ami_id:int=None):
        if not nom_ami and not ami_id:
            return
        if nom_ami:
            ami_id = self.gestion_utilisateurs.obtenir_id(nom_ami)

        body = {"receiver_id" : ami_id}
        rep = self.gestionnaire_de_requetes.faire_requete(url=f"/me/send_friend_request", type_de_r='post', body=body)
        return rep
    
    def obtenir_demandes_amis_recues(self):
        rep = self.gestionnaire_de_requetes.faire_requete(url="/me/friend_requests", type_de_r='get')
        return rep

    def obtenir_demandes_amis_envoyees(self):
        rep = self.gestionnaire_de_requetes.faire_requete(url='/me/sent_friend_requests', type_de_r='get')
        return rep

    def accepter_demande_ami(self, nom_ami:str=None, ami_id:int=None):
        if not nom_ami and not ami_id:
            return
        elif nom_ami:
            ami_id = self.gestion_utilisateurs.obtenir_id(nom_ami)

        body = {"sender_id": ami_id}
        rep = self.gestionnaire_de_requetes.faire_requete(url=f"/me/accept_friend_request", type_de_r='post',body=body)
        return rep

    def annuler_demande_ami(self, ami_id:int):
        body = {"receiver_id" : ami_id}
        rep = self.gestionnaire_de_requetes.faire_requete(url=f"/me/cancel_friend_request", body=body, type_de_r='delete')
        return rep

    def refuser_demande_ami(self, ami_id:int):
        body = {"sender_id": ami_id}
        rep = self.gestionnaire_de_requetes.faire_requete(url=f"/me/reject_friend_request", type_de_r='delete', body=body)
        return rep

    def enlever_ami(self, nom_ami:str=None, ami_id:int=None):
        if not nom_ami and not ami_id:
            return
        elif nom_ami: 
            ami_id = self.gestion_utilisateurs.obtenir_id(nom_ami)

        body = {'friend_id': ami_id}
        rep = self.gestionnaire_de_requetes.faire_requete(url=f"/me/remove_friend", type_de_r='delete', body=body)
        return rep
    

    def bloquer_ami(self, ami_id):
        body = {"friend_id" : ami_id}
        rep = self.gestionnaire_de_requetes.faire_requete(url=f"/me/block_user", body=body, type_de_r='post')
        return rep
    
    def debloquer_ami(self, ami_id):
        body = {"friend_id" : ami_id}
        rep = self.gestionnaire_de_requetes.faire_requete(url=f"/me/unblock_user", body=body, type_de_r='delete')
        return rep
    
    def obtenir_blocked_ids(self) -> list[int]:
        rep = self.gestionnaire_de_requetes.faire_requete(url="/me/blocked_users", type_de_r='get')
        if rep and rep.get('status_code') == 200:
            return rep.get('blocked_users_ids')
        else:
            return
    
class GestionConnexions:
    def __init__(self):
        self.requetur_sans_token = GestionRequetes()
        
    def inscription(self, pseudo:str, mail:str, mdp:str, date_naissance:str):
        body = {"username": pseudo, "mail": mail, "password": mdp, "date_of_birth": date_naissance}
        rep = self.requetur_sans_token.faire_requete(url=f"/signup", type_de_r='post',body=body)
        return rep

    
    def connexion(self, mail:str, mdp:str):
        body = {"mail": mail, "password": mdp}
        rep = self.requetur_sans_token.faire_requete(url=f"/login", type_de_r='post',body=body)
        
        if rep.get('status_code') == 401:
            return
        else:
            return rep

class GestionConversations:
    def __init__(self, token):
        self.token = token

        self.gestionnaire_de_requetes = GestionRequetes(token=self.token)
    
    def creer_conv(self, ami_id:int):
        body = {"user2_id" : ami_id}
        rep = self.gestionnaire_de_requetes.faire_requete(url="/create_conversation", body=body, type_de_r='post')
        return rep
    
    def supprimer_conv(self, conv_id:int):
        body = {"conversation_id" : conv_id}
        rep = self.gestionnaire_de_requetes.faire_requete(url="/delete_conversation", body=body, type_de_r='delete')
        return rep
    
    def obtenir_convs(self):
        rep = self.gestionnaire_de_requetes.faire_requete(url="/me/conversations", type_de_r='get')
        return rep
    
    def obtenir_msgs(self, conv_id:int, limite:int=50, offset:int=0):
        rep = self.gestionnaire_de_requetes.faire_requete(url=f"/conversation/messages?conversation_id={conv_id}&limit={limite}&offset={offset}", type_de_r='get')
        return rep
    
    def envoyer_msg(self, conv_id:int, msg:str):
        body = {"conversation_id" : conv_id, "content" : msg}
        rep = self.gestionnaire_de_requetes.faire_requete(url=f"/conversation/send_message", body=body, type_de_r='post')
        return rep
    
    def supprimer_msg(self, msg_id:int):
        body = {"message_id" : msg_id}
        rep = self.gestionnaire_de_requetes.faire_requete(url=f"/conversation/delete_message", body=body, type_de_r='delete')
        return rep
    
    def marquer_lu(self, conv_id:int):
        body = {"conversation_id" : conv_id}
        rep = self.gestionnaire_de_requetes.faire_requete(url=f"/conversation/read", body=body, type_de_r='put')
        return rep

class GestionMedia:
    def __init__(self, token:str):
        self.token = token

        self.gestionnaire_de_requetes = GestionRequetes(token=self.token)

    def download_pp(self, pp_id:str, pp_path:str):
        rep = self.gestionnaire_de_requetes.faire_requete(url=f"/media/avatar?avatar_id={pp_id}", type_de_r='get', path=pp_path)
        return rep  # Ici on a fait en sorte que rep soit True ou None
