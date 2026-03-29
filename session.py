from cache import Cache
from gestionnaires_requetes import GestionAmis, GestionUtilisateurs

class Session:
    def __init__(self, user_info:dict, token:str):
        self.token = token
        self.user_info = user_info
        self.user_id = user_info.get("user_id")

        self.cache = Cache(self.user_id)
        self.gestionnaire_amis = GestionAmis(token=token)
        self.gestionnaire_utilisateurs = GestionUtilisateurs(token=token)

        '''self.ws = WebSocketClient(token)
        self.ws.start()'''

    def fermer(self):
        self.cache.invalider_tout()
        self.ws.stop()
        self.cache.fermer()