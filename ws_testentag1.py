import json
import time
from PyQt6.QtCore import QThread, pyqtSignal


from gestionnaires_requetes import GestionConnexions
from ws_client import WebSocketClient


# -----------------------------
# Fonctions de test
# -----------------------------
def handle_ws_event(event):
    etype = event.get("type", "unknown")
    print(f"[WS Event] type={etype} data={event}")


def main():
    import os
    os.environ["HTTP_PROXY"] = "http://192.168.228.254:3128"
    os.environ["HTTPS_PROXY"] = "http://192.168.228.254:3128"


    # --- Connexion et récupération token ---
    gestionnaire_connections = GestionConnexions()
    rep1 = gestionnaire_connections.connexion(mail="p1@mail.com", mdp="p1")
    token1 = rep1.get("api_token")
    print("Token récupéré :", token1)

    # --- Création et lancement WebSocket ---
    ws = WebSocketClient(token1)
    ws.message_received.connect(handle_ws_event)
    ws.start()

    print("WebSocket thread démarré. Ctrl+C pour arrêter.")

    # --- Loop Python pour garder le thread vivant ---
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Arrêt demandé, fermeture du WebSocket...")
        ws.stop()
        print("Thread WebSocket fermé proprement.")


if __name__ == "__main__":
    print("=== Début du test WebSocket ===")
    main()
    print("=== Fin du test ===")