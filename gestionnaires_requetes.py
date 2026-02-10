import requests

LIEN_API = "http://161.35.17.40:8000" 

class GestionRequetes:
    def __init__(self, token=None):
        self.token = token

    def faire_requete(self, url:str, type_de_r:str, body:dict=None, files=None):
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

        else:
            print(f"Erreur, ce type de requete n'est pas renseigné : {type_de_r}")
            return


        if rep.status_code == 200:
            return rep.json()
        elif rep.status_code == 401:
            print(f"CODE : {rep.status_code}, Token invalide ou expiré")
        elif rep.status_code == 500:
            print(f"CODE : {rep.status_code}, Erreur interne du serveur")
        else:
            print("Erreur :", rep.status_code, rep.text)
        return

class GestionUtilisateurs:
    def __init__(self, token):
        self.token = token

        self.gestionnaire_de_requetes = GestionRequetes(token=self.token)
    
    def obtenir_id(self, nom:str):
        rep = self.gestionnaire_de_requetes.faire_requete(url=f"/user/username?username={nom}", type_de_r='get')
        return rep.get("user_id")

    def obtenir_nom(self, son_id:int):
        rep = self.gestionnaire_de_requetes.faire_requete(url=f"/user/username?user_id={son_id}", type_de_r='get')
        return rep.get("username")
    
    def obtenir_noms(self, ids:list[int]) -> list[str]:
        ids_amis = self.obtenir_infos(ids=ids)
        return [user.get('username') for user in ids_amis]

    def obtenir_infos(self, ids:list[int]) -> list:
        if ids == []:
            print("La liste d'ids est vide pour obtenir_infos")
            return

        body = {'user_id' : ids}
        rep = self.gestionnaire_de_requetes.faire_requete(url=f"/user/batch", type_de_r='post', body=body)
        if rep:
            return rep.get('users')
        else:
            return

    def changer_pp(self, pp_path:str):
        with open(pp_path, "rb") as image_file:
            files = {"file": image_file}
            rep = self.gestionnaire_de_requetes.faire_requete(url=f"/me/change_avatar", type_de_r='post', files=files)
        print(rep)
        return

class GestionAmis:
    def __init__(self, token):
        self.token = token

        self.gestionnaire_de_requetes = GestionRequetes(token=self.token)
        self.gestion_utilisateurs = GestionUtilisateurs(token=self.token)
    
    def obtenir_amis(self, toutes_infos:bool=False, seulement_ids:bool=False, seulement_noms:bool=False) -> list:
        if not toutes_infos and not seulement_ids and not seulement_noms:
            print("Manque un renseignement sur l'appel obtenir_amis")
            return
        
        rep = self.gestionnaire_de_requetes.faire_requete(url=f"/me/friends", type_de_r='get')
        friends_ids = rep.get('friends_ids')
        if seulement_ids and not toutes_infos and not seulement_noms:
            return friends_ids
        elif seulement_noms and not toutes_infos and not seulement_ids:
            return self.gestion_utilisateurs.obtenir_noms(ids=friends_ids)
        elif toutes_infos and not seulement_ids and not seulement_noms:
            return self.gestion_utilisateurs.obtenir_infos(ids=friends_ids)

        else:
            print("Informations en confliction sur l'appel obtenir_amis")
            return

    def demander_en_ami(self, nom_ami:str=None, id_ami:int=None):
        if not nom_ami and not id_ami:
            print("Veuillez renseigner le nom ou l'id le l'ami à ajouter")
            return
        if nom_ami:
            id_ami = self.gestion_utilisateurs.obtenir_id(nom_ami)

        body = {"receiver_id" : id_ami}
        rep = self.gestionnaire_de_requetes.faire_requete(url=f"/me/send_friend_request", type_de_r='post', body=body)
        print(rep)
        return rep
    
    def obtenir_demandes_amis_recues(self):
        rep = self.gestionnaire_de_requetes.faire_requete(url="/me/friend_requests", type_de_r='get')
        print(rep)

    def accepter_demande_ami(self, nom_ami:str=None, id_ami:int=None):
        if not nom_ami and id_ami:
            return
        elif nom_ami:
            id_ami = self.gestion_utilisateurs.obtenir_id(nom_ami)

        body = {"sender_id": id_ami}
        rep = self.gestionnaire_de_requetes.faire_requete(url=f"/me/accept_friend_request", type_de_r='post',body=body)
        print(rep)
        return rep

    def annuler_demande_ami(self, nom_ami):
        self.gestionnaire_de_requetes.faire_requete(url=f"/me/cancel_friend_request/{nom_ami}", type_de_r='get')

    def refuser_demande_ami(self, nom_ami):
        self.gestionnaire_de_requetes.faire_requete(url=f"/me/reject_friend_request/{nom_ami}", type_de_r='get')
    
    def enlever_ami(self, nom_ami:str=None, id_ami:int=None):
        if not nom_ami and not id_ami:
            return
        elif nom_ami: 
            id_ami = self.gestion_utilisateurs.obtenir_id(nom_ami)

        body = {'friend_id':id_ami}
        rep = self.gestionnaire_de_requetes.faire_requete(url=f"/me/remove_friend", type_de_r='delete', body=body)
        print(rep)
        return rep
    

    def bloquer_ami(self, nom_ami):
        self.gestionnaire_de_requetes.faire_requete(url=f"/me/block_user/{nom_ami}", type_de_r='get')
    
    def debloquer_ami(self, nom_ami):
        self.gestionnaire_de_requetes.faire_requete(url=f"/me/unblock_user/{nom_ami}", type_de_r='get')
    
class GestionConnexions:
    def __init__(self):
        self.requetur_sans_token = GestionRequetes()
        
    def inscription(self, pseudo:str, mail:str, mdp:str, date_naissance:str):
        body = {"username": pseudo, "mail": mail, "password": mdp, "date_of_birth": date_naissance}
        rep = self.requetur_sans_token.faire_requete(url=f"/signup", type_de_r='post',body=body)
        print(rep)
        return rep

    
    def connexion(self, mail:str, mdp:str):
        body = {"mail": mail, "password": mdp}
        rep = self.requetur_sans_token.faire_requete(url=f"/login", type_de_r='post',body=body)
        
        if rep.get('status_code') == 401:
            return
        else:
            print(rep)
            return rep

class GestionMedia:
    def __init__(self, token:str):
        self.gestionnaire_de_requetes = GestionRequetes(token=self.token)
