import threading

from PyQt6.QtCore import QObject, pyqtSignal

from ws_test import WSClient


class WSBridge(QObject):
    """Thread-safe Qt bridge between WSClient and the UI.

    The socket.io client runs in a worker thread.
    UI notifications go through Qt signals.
    """

    connected_changed = pyqtSignal(bool)
    friend_status_changed = pyqtSignal(int, bool, dict)
    online_friends_received = pyqtSignal(list)
    new_message_received = pyqtSignal(dict)
    messages_read_received = pyqtSignal(dict)

    new_friend_request = pyqtSignal(int, str)
    friend_request_accepted = pyqtSignal(int)
    friend_request_rejected = pyqtSignal(int)
    friend_request_canceled = pyqtSignal(int)

    friend_removed = pyqtSignal(int)
    user_updated = pyqtSignal(int, str, str)    # (user_id, username, avatar_id)
    user_blocked = pyqtSignal(int)
    user_unblocked = pyqtSignal(int)

    error_occurred = pyqtSignal(str)

    def __init__(self, session, parent=None) -> None:
        super().__init__(parent)
        self.session = session
        self._client = None
        self._thread = None
        self._lock = threading.Lock()

    def start(self, token: str, timeout: int = 10) -> None:
        """Initialize and connect websocket in a background thread."""
        with self._lock:
            if self._thread and self._thread.is_alive():
                return

            self._client = WSClient(token=token, session=self.session, on_ui=self._on_ws_event)
            self._thread = threading.Thread(
                target=self._connect_worker,
                args=(timeout,),
                name="ws-bridge-connect",
                daemon=True,
            )
            self._thread.start()

    def _connect_worker(self, timeout: int) -> None:
        if self._client is None:
            return

        try:
            self._client.connect(timeout=timeout)
            self.connected_changed.emit(True)
        except Exception as exc:  # pragma: no cover - network dependent
            self.error_occurred.emit(f"Websocket connection failed: {exc}")
            self.connected_changed.emit(False)

    def stop(self) -> None:
        """Disconnect websocket cleanly."""
        with self._lock:
            if self._client is None:
                return

            try:
                self._client.disconnect()
            except Exception as exc:  # pragma: no cover - network dependent
                self.error_occurred.emit(f"Websocket disconnection error: {exc}")
            finally:
                self.connected_changed.emit(False)
                self._client = None
                self._thread = None

    def send_message(self, receiver_id: int, content: str) -> None:
        if self._client is None:
            self.error_occurred.emit("WS is not initialized: cannot send message")
            return
        self._client.send_message(receiver_id=receiver_id, content=content)

    def set_typing(self, receiver_id: int, is_typing: bool) -> None:
        if self._client is None:
            return
        self._client.set_typing(receiver_id=receiver_id, is_typing=is_typing)

    def mark_read(self, conversation_id: int) -> None:
        if self._client is None:
            return
        self._client.mark_read(conversation_id=conversation_id)

    def _on_ws_event(self, event_name: str, data) -> None:
        if event_name == "friend_status_change":
            user_id = int(data.get("user_id", -1))
            online = data.get("status") == "online"
            self.friend_status_changed.emit(user_id, online, data)
            return

        if event_name == "online_friends":
            friends = data.get("friends", [])
            if not isinstance(friends, list):
                friends = []
            self.online_friends_received.emit(friends)
            return

        if event_name == "new_message":
            self.new_message_received.emit(data)
            return

        if event_name == "messages_read":
            self.messages_read_received.emit(data)


        if event_name == "new_friend_request":
            self.new_friend_request.emit(data.get('sender_id'), data.get('sender_username'))
            # data exemple : {"sender_id": 1, "sender_username": "alice"}

        if event_name == "friend_request_accepted":
            self.friend_request_accepted.emit(data.get('friend_id'))
            # data exemple : {"friend_id": 2, "friend_username": "bob"}

        if event_name == "friend_request_rejected":
            self.friend_request_rejected.emit(data.get('user_id'))
            # data exemple : {"user_id": 2, "username": "bob"}

        if event_name == "friend_request_canceled":
            self.friend_request_canceled.emit(data.get('sender_id'))
            # data exemple : {"sender_id": 1}


        if event_name == "friend_removed":
            self.friend_removed.emit(data.get('user_id'))
            # data exemple : {"user_id": 1, "username": "alice"}

        if event_name == "user_updated":
            self.user_updated.emit(data.get('user_id'), data.get('username'), data.get('avatar_id'))
            # data exemple : {"user_id": 1, "username": "alice_new", "avatar_id": "abc-123.png"}

        if event_name == "user_blocked":
            self.user_blocked.emit(data.get('user_id'))
            # data exemple : {"user_id": 1}
        
        if event_name == "user_unblocked":
            self.user_unblocked.emit(data.get('user_id'))
            # data exemple : {"user_id": 1}


        
