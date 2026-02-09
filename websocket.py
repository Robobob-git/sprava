import json
import websocket
from PyQt6.QtCore import QThread, pyqtSignal

class WebSocketClient(QThread):
    message_received = pyqtSignal(dict)
    disconnected = pyqtSignal()

    def __init__(self, api_token):
        super().__init__()
        self.url = f"ws://localhost:8000/ws/{api_token}"

    def run(self):
        self.ws = websocket.WebSocketApp(
            self.url,
            on_message=self.on_message,
            on_close=self.on_close,
        )
        self.ws.run_forever()

    def on_message(self, ws, message):
        data = json.loads(message)
        self.message_received.emit(data)

    def on_close(self, ws, *_):
        self.disconnected.emit()
