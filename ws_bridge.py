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
    raw_event_received = pyqtSignal(str, dict)
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
        payload = data if isinstance(data, dict) else {"data": data}
        self.raw_event_received.emit(event_name, payload)

        if event_name == "friend_status_change":
            user_id = int(payload.get("user_id", -1))
            online = payload.get("status") == "online"
            self.friend_status_changed.emit(user_id, online, payload)
            return

        if event_name == "online_friends":
            friends = payload.get("friends", [])
            if not isinstance(friends, list):
                friends = []
            self.online_friends_received.emit(friends)
            return

        if event_name == "new_message":
            self.new_message_received.emit(payload)
            return

        if event_name == "messages_read":
            self.messages_read_received.emit(payload)
