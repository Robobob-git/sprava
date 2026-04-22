import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

TTL_AMIS = timedelta(minutes=5)

class Ami:
    def __init__(self, id:int, username:str, pp_id:int = None, mail:str = None, phone:str = None, date_of_birth:str = None, online:bool = False, conv_id:int = None):
        self.id = id
        self.username = username
        self.pp_id = pp_id
        self.mail = mail
        self.phone = phone
        self.date_of_birth = date_of_birth
        self.online = online
        
        self.conv_id = conv_id

    @staticmethod
    def depuis_dict(d: dict, conv_id:int):
        return Ami(
            id=d.get("user_id"),
            username=d.get("username"),
            pp_id=d.get("pp_id"),
            mail=d.get("mail"),
            phone=d.get("phone"),
            date_of_birth=d.get("date_of_birth"),

            conv_id=conv_id
        )

    def __eq__(self, autre):
        """Permet de comparer 2 instances Ami"""
        if isinstance(autre, Ami):
            return self.id == autre.id
        return False

    def __hash__(self):
        return hash(self.id)

class Blocked:
    def __init__(self, id:int, username:str, pp_id:int = None):
        self.id = id
        self.username = username
        self.pp_id = pp_id


#  Cache SQLite + dict mémoire

class Cache:
    def __init__(self, user_id: int):
        chemin = Path(f"data/cache_{user_id}.db")
        chemin.parent.mkdir(parents=True, exist_ok=True)

        self._conn = sqlite3.connect(chemin)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._init_tables()

        # Chargement initial du dict depuis SQLite
        # Toutes les lectures passeront par ce dict
        self._amis: dict[int, Ami] = {a.id: a for a in self._lire_amis_sqlite()}
        self._blocked: dict[int, Blocked] = self._lire_blocked_sqlite()

    # Tables

    def _init_tables(self):
        self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS amis (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                pp_id TEXT,
                mail TEXT,
                phone TEXT,
                date_of_birth TEXT,
                conv_id INTEGER
            );
                                 
            CREATE TABLE IF NOT EXISTS blocked (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                pp_id TEXT
            );

            CREATE TABLE IF NOT EXISTS cache_meta (
                cle    TEXT PRIMARY KEY,
                valeur TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conv_id INTEGER NOT NULL,
                auteur_id INTEGER NOT NULL,
                contenu TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                lu INTEGER NOT NULL DEFAULT 0
            );
            CREATE INDEX IF NOT EXISTS idx_messages_conv
                ON messages(conv_id, timestamp);
        """)
        self._conn.commit()

    # TTL

    def _get_meta(self, cle: str) -> str | None:
        row = self._conn.execute("SELECT valeur FROM cache_meta WHERE cle = ?", (cle,)).fetchone()
        return row["valeur"] if row else None

    def _set_meta(self, cle: str, valeur: str):
        with self._conn:
            self._conn.execute(
                "INSERT OR REPLACE INTO cache_meta (cle, valeur) VALUES (?, ?)",
                (cle, valeur)
            )

    def est_perime(self) -> bool:
        """True si le cache des amis n'a jamais été sync ou si TTL expiré."""
        derniere_sync = self._get_meta("amis_sync_at")
        if not derniere_sync:
            return True
        age = datetime.now() - datetime.fromisoformat(derniere_sync)
        return age > TTL_AMIS

    # Lecture (depuis dict mémoire uniquement)

    def amis(self) -> list[Ami]:
        return list(self._amis.values())

    def amis_ids(self) -> list[int]:
        return list(self._amis.keys())    

    def ami_par_id(self, id_:int) -> Ami:
        return self._amis.get(id_)
    

    def blocked(self) -> list[Blocked]:
        return list(self._blocked.values())

    def blocked_ids(self) -> set[int]:
        return set(self._blocked)
    
    def blocked_par_id(self, id_:int) -> Blocked:
        return self._blocked.get(id_)
    
    def is_blocked(self, id_:int) -> bool:
        return id_ in self._blocked
    

    def conv_id_par_ami_id(self, id_:int) -> int:
        return self.ami_par_id(id_).conv_id

    # Écriture (SQLite + dict)

    def ecrire_amis(self, amis: list[Ami]):
        """Sync complète : remplace tout le cache. Met à jour TTL."""
        with self._conn:
            self._conn.execute("DELETE FROM amis")
            self._conn.executemany(
                """INSERT INTO amis (id, username, pp_id, mail, phone, date_of_birth, conv_id)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                [(a.id, a.username, a.pp_id, a.mail, a.phone, a.date_of_birth, a.conv_id) for a in amis]
            )
        self._set_meta("amis_sync_at", datetime.now().isoformat())
        # Mise à jour du dict (on préserve les statuts online déjà en mémoire)
        for a in amis:
            if a.id in self._amis:
                a.online = self._amis[a.id].online
        self._amis = {a.id:a for a in amis}

    def upsert_ami(self, ami: Ami):
        """Ajoute ou met à jour un ami (ex: friend_request_accepted)."""
        with self._conn:
            self._conn.execute(
                """INSERT OR REPLACE INTO amis
                   (id, username, pp_id, mail, phone, date_of_birth, conv_id)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (ami.id, ami.username, ami.pp_id, ami.mail, ami.phone, ami.date_of_birth, ami.conv_id)
            )
        self._amis[ami.id] = ami

    def invalider_ami(self, id_:int):
        """Retire un ami du cache (ex: remove_friend)."""
        with self._conn:
            self._conn.execute("DELETE FROM amis WHERE id = ?", (id_,))
        self._amis.pop(id_, None)

    def block(self, id_:int):
        ami = self.ami_par_id(id_)
        if not ami:
            print(f"Impossible de bloquer {id_} : ami introuvable dans le cache")
            return

        blocked = Blocked(id=ami.id, username=ami.username, pp_id=ami.pp_id)
        with self._conn:
            self._conn.execute("INSERT OR IGNORE INTO blocked (id, username, pp_id) VALUES (?, ?, ?)", (blocked.id, blocked.username, blocked.pp_id))
        self._blocked[blocked.id] = blocked

    def unblock(self, id_:int):
        with self._conn:
            self._conn.execute("DELETE FROM blocked WHERE id = ?", (id_))
        self._blocked.pop(id_, None)  

    def add_msg(self, id_:int, conv_id:int, auteur_id:int, msg:str, timestamp:str):
        with self._conn:
            self._conn.execute("INSERT OR IGNORE INTO messages (id, conv_id, auteur_id, contenu, timestamp, lu) VALUES (?, ?, ?, ?, ?, ?)", (id_, conv_id, auteur_id, msg, timestamp, 0))

    def mettre_lu(self, conv_id:int):
        with self._conn:
            self._conn.execute("UPDATE messages SET lu = 1 WHERE conv_id = ?", (conv_id))

    def set_statut_ami(self, id_: int, online: bool):
        """Met à jour le statut online/offline"""
        if id_ in self._amis:
            self._amis[id_].online = online

    # Invalidation totale (déconnexion)

    def invalider_tout(self):
        """Vide tout le cache. Appelé à la déconnexion."""
        with self._conn:
            self._conn.execute("DELETE FROM amis")
            self._conn.execute("DELETE FROM cache_meta")
            self._conn.execute("DELETE FROM blocked")
        self._amis = {}
        self._blocked = {}

    # Lecture SQLite brute (usage interne uniquement)

    def _lire_amis_sqlite(self) -> list[Ami]:
        rows = self._conn.execute("SELECT id, username, pp_id, mail, phone, date_of_birth, conv_id FROM amis").fetchall()
        return [Ami(**dict(r)) for r in rows]
    
    def _lire_blocked_sqlite(self) -> dict[int, Blocked]:
        rows = self._conn.execute("SELECT id, username, pp_id FROM blocked").fetchall()
        for r in rows:
            print(f'r : {r["id"]}\ndict(r) : {dict(r)}')
        return {r["id"]: Blocked(**dict(r)) for r in rows}

    # Cycle de vie

    def fermer(self):
        self._conn.close()