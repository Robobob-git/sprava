from websocket import WebSocketClient

from gestionnaires_requetes import GestionConnexions, GestionUtilisateurs
from autre_fonctions import obtenir_vrai_chemin

def main():
    import os
    os.environ["HTTP_PROXY"] = "http://192.168.228.254:3128"
    os.environ["HTTPS_PROXY"] = "http://192.168.228.254:3128"


    gestionnaire_connections = GestionConnexions()
    rep1 = gestionnaire_connections.connexion(mail="p1@mail.com", mdp="p1")
    token1 = rep1.get("api_token")

    def handle_ws_event(self, event):
        match event["type"]:
            case "new_friend_request":
                self.show_friend_request(event)
            case "friend_status_change":
                self.update_friend_status(event)
            case "new_message":
                self.add_message(event)

    ws = WebSocketClient(token1)
    ws.message_received.connect(handle_ws_event)
    ws.start()



if __name__ == "__main__":
    print("début")

    main()

    print("Fin")

