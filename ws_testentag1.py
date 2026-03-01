"""
Test indépendant du WebSocket API
==================================
Couvre :
  - Authentification (token valide / invalide → code 4008)
  - Connexion / Déconnexion + friend_status_change
  - Connexions multiples simultanées (même utilisateur)
  - send_message → new_message (reçu par les deux participants)
  - typing / stop_typing → user_typing
  - mark_read → messages_read
  - get_online_friends → online_friends

Dépendances : pip install websockets requests
"""

import asyncio
import json
import time
import requests

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
API_HTTP  = "http://161.35.17.40:8000"
API_WS    = "ws://161.35.17.40:8000"

USER1_MAIL = "p1@mail.com"
USER1_MDP  = "p1"
USER2_MAIL = "p2@mail.com"
USER2_MDP  = "p2"

TIMEOUT    = 5   # secondes max d'attente pour un message WS

# ─────────────────────────────────────────────
# HELPERS HTTP
# ─────────────────────────────────────────────

def http_login(mail: str, mdp: str) -> dict:
    r = requests.post(f"{API_HTTP}/login", json={"mail": mail, "password": mdp})
    data = r.json()
    assert data.get("status_code") == 200, f"Login échoué pour {mail}: {data}"
    print(f"  ✔ Login OK → user_id={data['user_id']}, token={data['api_token'][:8]}...")
    return data

def http_get_friends_ids(token: str) -> list:
    r = requests.get(f"{API_HTTP}/me/friends", headers={"Authorization": token})
    return r.json().get("friends_ids", [])

def http_send_friend_request(token: str, target_username: str):
    r = requests.post(f"{API_HTTP}/me/send_friend_request",
                      headers={"Authorization": token},
                      json={"username": target_username})
    return r.json()

def http_accept_friend_request(token: str, sender_id: int):
    r = requests.post(f"{API_HTTP}/me/accept_friend_request",
                      headers={"Authorization": token},
                      json={"sender_id": sender_id})
    return r.json()

def ensure_friends(token1: str, user1_id: int, user1_name: str,
                   token2: str, user2_id: int, user2_name: str):
    """S'assure que p1 et p2 sont amis (crée la relation si besoin)."""
    friends = http_get_friends_ids(token1)
    if user2_id not in friends:
        print(f"  → {user1_name} et {user2_name} ne sont pas amis, envoi de demande...")
        http_send_friend_request(token1, user2_name)
        http_accept_friend_request(token2, user1_id)
        print("  ✔ Amitié établie.")
    else:
        print(f"  �� {user1_name} et {user2_name} sont déjà amis.")

def http_get_or_create_conversation(token1: str, token2_user_id: int) -> int:
    """Récupère ou crée une conversation entre user1 et user2, retourne conversation_id."""
    r = requests.get(f"{API_HTTP}/conversations", headers={"Authorization": token1})
    convs = r.json()
    if isinstance(convs, list):
        for c in convs:
            if c.get("other_user_id") == token2_user_id:
                return c["id"]
    # Crée la conversation
    r = requests.post(f"{API_HTTP}/create_conversation",
                      headers={"Authorization": token1},
                      json={"other_user_id": token2_user_id})
    data = r.json()
    conv_id = data.get("conversation_id")
    assert conv_id, f"Impossible de créer la conversation : {data}"
    print(f"  ✔ Conversation créée : id={conv_id}")
    return conv_id

# ─────────────────────────────────────────────
# HELPERS WEBSOCKET
# ─────────────────────────────────────────────

async def wait_for_message(ws, expected_type: str, timeout: int = TIMEOUT) -> dict | None:
    """Attend un message d'un type précis dans la fenêtre de timeout."""
    deadline = asyncio.get_event_loop().time() + timeout
    while asyncio.get_event_loop().time() < deadline:
        remaining = deadline - asyncio.get_event_loop().time()
        try:
            raw = await asyncio.wait_for(ws.recv(), timeout=remaining)
            msg = json.loads(raw)
            if msg.get("type") == expected_type:
                return msg
            else:
                print(f"    (message ignoré : type={msg.get('type')})")
        except asyncio.TimeoutError:
            break
    return None

async def collect_messages(ws, duration: float = 1.5) -> list[dict]:
    """Collecte tous les messages pendant `duration` secondes."""
    msgs = []
    deadline = asyncio.get_event_loop().time() + duration
    while asyncio.get_event_loop().time() < deadline:
        remaining = deadline - asyncio.get_event_loop().time()
        try:
            raw = await asyncio.wait_for(ws.recv(), timeout=remaining)
            msgs.append(json.loads(raw))
        except asyncio.TimeoutError:
            break
    return msgs

# ────────────────────────────────────────���────
# TESTS
# ─────────────────────────────────────────────

async def test_invalid_token():
    """Token invalide → le serveur doit fermer avec code 4008."""
    print("\n[TEST 1] Token invalide → fermeture code 4008")
    import websockets
    try:
        async with websockets.connect(f"{API_WS}/ws/TOKEN_INVALIDE_123") as ws:
            # Le serveur devrait fermer immédiatement
            try:
                await asyncio.wait_for(ws.recv(), timeout=TIMEOUT)
            except websockets.exceptions.ConnectionClosedError as e:
                assert e.code == 4008, f"Code attendu 4008, reçu {e.code}"
                print("  ✔ Connexion refusée avec code 4008.")
                return
            print("  ✘ Le serveur n'a pas fermé la connexion.")
    except websockets.exceptions.ConnectionClosedError as e:
        assert e.code == 4008, f"Code attendu 4008, reçu {e.code}"
        print("  ✔ Connexion refusée avec code 4008.")


async def test_connection_and_friend_status(token1: str, token2: str, user1_id: int, user2_id: int):
    """Connexion de user1 → user2 doit recevoir friend_status_change online.
       Déconnexion de user1 → user2 doit recevoir friend_status_change offline."""
    import websockets
    print("\n[TEST 2] Connexion/Déconnexion → friend_status_change")

    async with websockets.connect(f"{API_WS}/ws/{token2}") as ws2:
        # Vider les messages éventuels
        await asyncio.sleep(0.3)

        # user1 se connecte
        async with websockets.connect(f"{API_WS}/ws/{token1}") as ws1:
            msg = await wait_for_message(ws2, "friend_status_change")
            assert msg is not None, "Pas de friend_status_change à la connexion"
            assert msg["user_id"] == user1_id
            assert msg["status"] == "online"
            print(f"  ✔ friend_status_change online reçu : {msg}")

        # ws1 est maintenant fermé → user1 déconnecté
        msg = await wait_for_message(ws2, "friend_status_change")
        assert msg is not None, "Pas de friend_status_change à la déconnexion"
        assert msg["user_id"] == user1_id
        assert msg["status"] == "offline"
        print(f"  ✔ friend_status_change offline reçu : {msg}")


async def test_multiple_connections(token1: str, user1_id: int, token2: str, user2_id: int):
    """Un utilisateur peut avoir plusieurs connexions simultanées.
       Il n'est hors-ligne que quand TOUTES ses connexions sont fermées."""
    import websockets
    print("\n[TEST 3] Connexions multiples (même utilisateur)")

    async with websockets.connect(f"{API_WS}/ws/{token2}") as ws2:
        await asyncio.sleep(0.3)

        async with websockets.connect(f"{API_WS}/ws/{token1}") as ws1a:
            await wait_for_message(ws2, "friend_status_change")  # online

            # Deuxième connexion user1
            async with websockets.connect(f"{API_WS}/ws/{token1}") as ws1b:
                # Pas forcément de nouveau "online" (déjà connecté)
                pass  # ws1b se ferme

            # user1 doit encore être en ligne (ws1a toujours ouverte)
            offline_msg = await collect_messages(ws2, duration=1.5)
            offline_events = [m for m in offline_msg if m.get("type") == "friend_status_change" and m.get("status") == "offline"]
            assert len(offline_events) == 0, f"User1 ne devrait pas être offline, il a encore ws1a ! {offline_events}"
            print("  ✔ User1 reste online après fermeture de sa 2e connexion.")

        # ws1a fermée → maintenant offline
        msg = await wait_for_message(ws2, "friend_status_change")
        assert msg and msg["status"] == "offline"
        print("  ✔ User1 passe offline quand toutes ses connexions sont fermées.")


async def test_send_message(token1: str, user1_id: int, token2: str, user2_id: int, conv_id: int):
    """send_message → new_message reçu par les deux participants."""
    import websockets
    print("\n[TEST 4] send_message → new_message (expéditeur + destinataire)")

    async with websockets.connect(f"{API_WS}/ws/{token1}") as ws1, \
               websockets.connect(f"{API_WS}/ws/{token2}") as ws2:

        payload = json.dumps({
            "type": "send_message",
            "receiver_id": user2_id,
            "content": "Hello depuis le test automatisé !"
        })
        await ws1.send(payload)

        msg1 = await wait_for_message(ws1, "new_message")
        msg2 = await wait_for_message(ws2, "new_message")

        assert msg1 is not None, "L'expéditeur n'a pas reçu new_message"
        assert msg2 is not None, "Le destinataire n'a pas reçu new_message"

        for m in [msg1, msg2]:
            assert m["sender_id"] == user1_id
            assert m["receiver_id"] == user2_id
            assert m["content"] == "Hello depuis le test automatisé !"
            assert "message_id" in m
            assert "timestamp" in m

        print(f"  ✔ new_message reçu par ws1 : message_id={msg1['message_id']}")
        print(f"  ✔ new_message reçu par ws2 : message_id={msg2['message_id']}")
        return msg1["message_id"]


async def test_typing(token1: str, user1_id: int, token2: str, user2_id: int):
    """typing / stop_typing → user_typing (is_typing true/false)"""
    import websockets
    print("\n[TEST 5] typing / stop_typing → user_typing")

    async with websockets.connect(f"{API_WS}/ws/{token1}") as ws1, \
               websockets.connect(f"{API_WS}/ws/{token2}") as ws2:

        # typing
        await ws1.send(json.dumps({"type": "typing", "receiver_id": user2_id}))
        msg = await wait_for_message(ws2, "user_typing")
        assert msg is not None, "Pas de user_typing reçu"
        assert msg["user_id"] == user1_id
        assert msg["is_typing"] is True
        print(f"  ✔ user_typing(is_typing=True) reçu : {msg}")

        # stop_typing
        await ws1.send(json.dumps({"type": "stop_typing", "receiver_id": user2_id}))
        msg = await wait_for_message(ws2, "user_typing")
        assert msg is not None, "Pas de user_typing(stop) reçu"
        assert msg["user_id"] == user1_id
        assert msg["is_typing"] is False
        print(f"  ✔ user_typing(is_typing=False) reçu : {msg}")


async def test_mark_read(token1: str, user1_id: int, token2: str, user2_id: int, conv_id: int):
    """mark_read → messages_read notifié à l'autre participant."""
    import websockets
    print("\n[TEST 6] mark_read → messages_read")

    async with websockets.connect(f"{API_WS}/ws/{token1}") as ws1, \
               websockets.connect(f"{API_WS}/ws/{token2}") as ws2:

        # user1 marque la conversation comme lue
        await ws1.send(json.dumps({"type": "mark_read", "conversation_id": conv_id}))

        # L'autre participant (ws2) doit recevoir messages_read
        msg = await wait_for_message(ws2, "messages_read")
        assert msg is not None, "Pas de messages_read reçu"
        assert msg["conversation_id"] == conv_id
        assert msg["user_id"] == user1_id
        print(f"  ✔ messages_read reçu par l'autre participant : {msg}")


async def test_get_online_friends(token1: str, token2: str, user2_id: int):
    """get_online_friends → online_friends contenant user2 si connecté."""
    import websockets
    print("\n[TEST 7] get_online_friends → online_friends")

    async with websockets.connect(f"{API_WS}/ws/{token2}") as ws2, \
               websockets.connect(f"{API_WS}/ws/{token1}") as ws1:

        await asyncio.sleep(0.5)  # laisser le temps aux deux de s'enregistrer

        await ws1.send(json.dumps({"type": "get_online_friends"}))
        msg = await wait_for_message(ws1, "online_friends")
        assert msg is not None, "Pas de online_friends reçu"
        assert isinstance(msg["friends"], list)
        assert user2_id in msg["friends"], f"user2_id={user2_id} devrait être dans friends={msg['friends']}"
        print(f"  ✔ online_friends reçu : {msg}")


# ─────────────────────────────────────────────
# RUNNER PRINCIPAL
# ─────────────────────────────────────────────

async def main():
    print("=" * 55)
    print("  SUITE DE TESTS WEBSOCKET")
    print("=" * 55)

    # 1. Authentification HTTP
    print("\n[SETUP] Connexion des deux utilisateurs via HTTP...")
    info1 = http_login(USER1_MAIL, USER1_MDP)
    info2 = http_login(USER2_MAIL, USER2_MDP)

    token1    = info1["api_token"]
    token2    = info2["api_token"]
    user1_id  = info1["user_id"]
    user2_id  = info2["user_id"]
    user1_name = info1.get("username", "p1")
    user2_name = info2.get("username", "p2")

    # 2. S'assurer qu'ils sont amis
    print("\n[SETUP] Vérification de l'amitié...")
    ensure_friends(token1, user1_id, user1_name, token2, user2_id, user2_name)

    # 3. S'assurer qu'une conversation existe
    print("\n[SETUP] Vérification/création de la conversation...")
    conv_id = http_get_or_create_conversation(token1, user2_id)
    print(f"  ✔ conversation_id={conv_id}")

    # ── Tests WS ──
    results = {}

    tests = [
        ("Token invalide",          test_invalid_token()),
        ("Connexion/Déconnexion",   test_connection_and_friend_status(token1, token2, user1_id, user2_id)),
        ("Connexions multiples",    test_multiple_connections(token1, user1_id, token2, user2_id)),
        ("send_message",            test_send_message(token1, user1_id, token2, user2_id, conv_id)),
        ("typing/stop_typing",      test_typing(token1, user1_id, token2, user2_id)),
        ("mark_read",               test_mark_read(token1, user1_id, token2, user2_id, conv_id)),
        ("get_online_friends",      test_get_online_friends(token1, token2, user2_id)),
    ]

    for name, coro in tests:
        try:
            await coro
            results[name] = "✅ PASS"
        except (AssertionError, Exception) as e:
            results[name] = f"❌ FAIL — {e}"

    # ── Résumé ──
    print("\n" + "=" * 55)
    print("  RÉSUMÉ")
    print("=" * 55)
    for name, status in results.items():
        print(f"  {status}  |  {name}")
    print("=" * 55)

    nb_fail = sum(1 for s in results.values() if s.startswith("❌"))
    if nb_fail == 0:
        print("  🎉 Tous les tests sont passés !")
    else:
        print(f"  ⚠️  {nb_fail} test(s) en échec.")

if __name__ == "__main__":
    asyncio.run(main())