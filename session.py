from cache import Cache
from gestionnaires_requetes import GestionAmis, GestionUtilisateurs, GestionConversations
from ws_bridge import WSBridge


class Session:
    def __init__(self, user_info: dict, token: str, requettes_manager, test: bool = False):
        self.token = token
        self.user_info = user_info
        self.user_id = user_info.get("user_id")
        self.test = test

        self.cache = Cache(self.user_id)


        if test:
            return

        self.ws_bridge = WSBridge(session=self)
        self.ws_bridge.start(token=self.token, timeout=10)

        self.requettes_manager = requettes_manager
        self.gestionnaire_amis = GestionAmis(token=token)
        self.gestionnaire_utilisateurs = GestionUtilisateurs(token=token)
        self.gestionnaire_conv = GestionConversations(token=token)

    def stop_ws(self) -> None:
        if self.ws_bridge is None:
            return

        self.ws_bridge.stop()
        self.ws_bridge = None

    def fermer(self) -> None:
        self.stop_ws()
        self.cache.invalider_tout()
        self.cache.fermer()