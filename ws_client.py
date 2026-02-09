import json
import time
from websocket import WebSocketApp
from PyQt6.QtCore import QThread, pyqtSignal
from gestionnaires_requetes import GestionConnexions

# -----------------------------
# Thread WebSocket
# -----------------------------
class WebSocketClient(QThread):
    message_received = pyqtSignal(dict)

    def __init__(self, api_token):
        super().__init__()
        self.url = f"ws://http://161.35.17.40:8000/ws/{api_token}"
        self._ws_app = None
        self._running = True

    def run(self):
        self._ws_app = WebSocketApp(
            self.url,
            on_message=self.on_message,
            on_close=self.on_close,
            on_error=self.on_error,
        )
        # run_forever est bloquant, donc thread indépendant
        self._ws_app.run_forever()

    def on_message(self, ws, message):
        event = json.loads(message)
        self.message_received.emit(event)

    def on_close(self, ws, *args):
        print("WebSocket closed")

    def on_error(self, ws, error):
        print("WebSocket error:", error)

    def stop(self):
        """Arrêt propre du thread et fermeture du WebSocket"""
        self._running = False
        if self._ws_app:
            self._ws_app.close()
        self.quit()
        self.wait()