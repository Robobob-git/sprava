import requests
import hashlib

from gestionnaires_requetes import GestionAmis, GestionConnexions, GestionUtilisateurs
from autre_fonctions import obtenir_vrai_chemin


def main():
    import os
    os.environ["HTTP_PROXY"] = "http://192.168.228.254:3128"
    os.environ["HTTPS_PROXY"] = "http://192.168.228.254:3128"

    gestionnaire_connections = GestionConnexions()

    rep1 = gestionnaire_connections.connexion(mail="p1@mail.com", mdp="p1")
    rep2 = gestionnaire_connections.connexion(mail="p2@mail.com", mdp="p2")

    token1 = rep1.get("api_token")
    user_id1 = rep1.get("user_id")
    token2 = rep2.get("api_token")
    user_id2 = rep2.get("user_id")


    gestionnaire_amis1 = GestionAmis(token=token1)
    gestionnaire_amis2 = GestionAmis(token=token2)

    gestionnaire_utilisateur1 = GestionUtilisateurs(token=token1)


    id_amis1:list = gestionnaire_amis1.obtenir_amis(seulement_ids=True)
    print(id_amis1)

    if id_amis1 == []:
        gestionnaire_amis1.demander_en_ami("p2")
        demandes_de_amis2 = gestionnaire_amis2.obtenir_demandes_amis_recues()
        print(f'amis 2 a : {demandes_de_amis2}')
        gestionnaire_amis2.accepter_demande_ami("p1")

    if id_amis1 != []:
        id_amis1:list = gestionnaire_amis1.obtenir_amis(seulement_ids=True)
        print(f"d'abord : {id_amis1}")

        print(f'user_id : {user_id2}')
        gestionnaire_amis1.enlever_ami(id_ami=user_id2)

        id_amis1:list = gestionnaire_amis1.obtenir_amis(seulement_ids=True)
        print(f"ensuite : {id_amis1}")

    if not rep1.get('avatar_id'):
        gestionnaire_utilisateur1.changer_pp(obtenir_vrai_chemin('images/pp1.png'))


if __name__ == "__main__":
    print("début")
    
    main()
    
    print("fin")

