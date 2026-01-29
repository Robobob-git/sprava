import requests
import hashlib

from gestionnaires_requetes import GestionAmis, GestionConnexions


def main():
    import os
    os.environ["HTTP_PROXY"] = "http://192.168.228.254:3128"
    os.environ["HTTPS_PROXY"] = "http://192.168.228.254:3128"

    gestionnaire_connections = GestionConnexions()

    rep1 = gestionnaire_connections.connexion(mail="a1@mail.com", mdp="a1")
    rep2 = gestionnaire_connections.connexion(mail="a2@mail.com", mdp="a2")

    token1 = rep1.get("api_token")
    user_id1 = rep1.get("user_id")
    token2 = rep2.get("api_token")
    user_id2 = rep2.get("user_id")


    gestionnaire_amis1 = GestionAmis(user_id=user_id1, token=token1)
    gestionnaire_amis2 = GestionAmis(user_id=user_id2, token=token2)


    id_amis1:list = gestionnaire_amis1.obtenir_amis(seulement_ids=True)
    print(id_amis1)

    if id_amis1 == []:
        gestionnaire_amis1.demander_en_ami("a2")
        gestionnaire_amis2.obtenir_demandes_amis_recues()
        gestionnaire_amis2.accepter_demande_ami("a1")

    if id_amis1 != []:
        id_amis1:list = gestionnaire_amis1.obtenir_amis(seulement_ids=True)
        print(f"d'abord : {id_amis1}")

        print(f'user_id : {user_id2}')
        gestionnaire_amis1.enlever_ami(id_ami=user_id2)

        id_amis1:list = gestionnaire_amis1.obtenir_amis(seulement_ids=True)
        print(f"ensuite : {id_amis1}")
    
    print("amongus")


if __name__ == "__main__":
    print("début")
    
    main()
    
    print("fin")

