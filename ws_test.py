import socketio, threading, time
from typing import Callable

class WSClient:
    def __init__(self, token: str, session, on_ui: Callable):
        self.url = "https://sprava-api-fc44f5e02dd0.herokuapp.com/socket.io/"
        self.token = token
        self.session = session          # accès cache + managers
        self.on_ui = on_ui              # callback thread-safe vers Qt
        self.sio = socketio.Client(reconnection=True)
        self._connected = threading.Event()
        self._register_handlers()

    def _register_handlers(self):
        @self.sio.on("connect")
        def _():
            self._connected.set()
            self.sio.emit("get_online_friends", {})

        @self.sio.on("disconnect")
        def _():
            self._connected.clear()

        @self.sio.on("friend_status_change")
        def _(data):
            uid = data["user_id"]
            online = (data["status"] == "online")
            self.session.cache.set_statut_ami(uid, online)
            self.on_ui("friend_status_change", data)

        @self.sio.on("online_friends")
        def _(data):
            online_ids = set(data.get("friends", []))
            for fid in self.session.cache.amis_ids():
                self.session.cache.set_statut_ami(fid, fid in online_ids)
            self.on_ui("online_friends", data)

        @self.sio.on("new_message")
        def _(data):
            # Option: persister dans cache.messages
            print('ETDRYGUHGJGCJHIOGJDHGUIHLGDHFFGKHGKFHDGKHLJHGFDHKJMKHGFJJKHJMHJFKJMGH')
            self.on_ui("new_message", data)
            # data du type : {'conversation_id': 1, 'message_id': 74, 'sender_id': 2, 'content': 'hj', 'created_at': '2026-04-23T00:40:01.122822', 'media_ids': []}

        @self.sio.on("messages_read")
        def _(data):
            self.on_ui("messages_read", data)

        @self.sio.on("new_friend_request")
        def _(data):
            self.on_ui("new_friend_request", data)

        @self.sio.on("friend_request_accepted")
        def _(data):
            self.on_ui("friend_request_accepted", data)

        @self.sio.on("friend_request_rejected")
        def _(data):
            self.on_ui("friend_request_rejected", data)

        @self.sio.on("friend_request_canceled")
        def _(data):
            self.on_ui("friend_request_canceled", data)

        @self.sio.on("friend_removed")
        def _(data):
            self.on_ui("friend_removed", data)

        @self.sio.on("user_updated")
        def _(data):
            self.on_ui("user_updated", data)

        @self.sio.on("user_blocked")
        def _(data):
            self.on_ui("user_blocked", data)

    def connect(self, timeout=10):
        self.sio.connect(self.url, auth={"token": self.token}, wait_timeout=timeout)
        if not self._connected.wait(timeout):
            raise TimeoutError("WS connect timeout")

    def disconnect(self):
        if self.sio.connected:
            self.sio.disconnect()

    def send_message(self, receiver_id: int, content: str):
        self.sio.emit("send_message", {"receiver_id": receiver_id, "content": content})

    def set_typing(self, receiver_id: int, is_typing: bool):
        self.sio.emit("typing" if is_typing else "stop_typing", {"receiver_id": receiver_id})

    def mark_read(self, conversation_id: int):
        self.sio.emit("mark_read", {"conversation_id": conversation_id})