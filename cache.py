import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass

TTL_AMIS = timedelta(minutes=5)

# ─────────────────────────────────────────
#  Modèle
# ─────────────────────────────────────────

@dataclass
class Ami:
    id: int
    username: str
    avatar_id: str | None = None
    mail: str | None = None
    phone: str | None = None
    date_of_birth: str | None = None
    en_ligne: bool = False          # volatile : jamais persisté en SQLite

    @staticmethod
    def depuis_dict(d: dict) -> "Ami":
        """Construit un Ami depuis la réponse brute de l'API."""
        return Ami(
            id=d.get("user_id"),
            username=d.get("username"),
            avatar_id=d.get("avatar_id"),
            mail=d.get("mail"),
            phone=d.get("phone"),
            date_of_birth=d.get("date_of_birth"),
        )

    def __eq__(self, autre):
        if isinstance(autre, Ami):
            return self.id == autre.id
        return False

    def __hash__(self):
        return hash(self.id)

# ─────────────────────────────────────────
#  Cache SQLite + dict mémoire
# ─────────────────────────────────────────

class Cache:
    def __init__(self, user_id: int):
        chemin = Path(f"data/cache_{user_id}.db")
        chemin.parent.mkdir(parents=True, exist_ok=True)

        self._conn = sqlite3.connect(chemin)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._init_tables()

        # Chargement initial du dict depuis SQLite
        # Toutes les lectures passeront par ce dict → jamais d'I/O disque pendant la session
        self._amis: dict[int, Ami] = {
            a.id: a for a in self._lire_amis_sqlite()
        }

    # ── Tables ───────────────────────────────────────────────

    def _init_tables(self):
        self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS amis (
                id            INTEGER PRIMARY KEY,
                username      TEXT    NOT NULL,
                avatar_id     TEXT,
                mail          TEXT,
                phone         TEXT,
                date_of_birth TEXT
            );

            CREATE TABLE IF NOT EXISTS cache_meta (
                cle    TEXT PRIMARY KEY,
                valeur TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS messages (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                auteur_id       INTEGER NOT NULL,
                contenu         TEXT    NOT NULL,
                timestamp       TEXT    NOT NULL,
                lu              INTEGER NOT NULL DEFAULT 0
            );
            CREATE INDEX IF NOT EXISTS idx_messages_conv
                ON messages(conversation_id, timestamp);
        """)
        self._conn.commit()

    # ── TTL ──────────────────────────────────────────────────

    def _get_meta(self, cle: str) -> str | None:
        row = self._conn.execute(
            "SELECT valeur FROM cache_meta WHERE cle = ?", (cle,)
        ).fetchone()
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

    # ── Lecture (depuis dict mémoire uniquement) ─────────────

    def amis(self) -> list[Ami]:
        return list(self._amis.values())

    def amis_ids(self) -> list[int]:
        return list(self._amis.keys())    

    def ami_par_id(self, id_: int) -> Ami | None:
        return self._amis.get(id_)

    # ── Écriture (SQLite + dict) ──────────────────────────────

    def ecrire_amis(self, amis: list[Ami]):
        """Sync complète : remplace tout le cache. Met à jour TTL."""
        with self._conn:
            self._conn.execute("DELETE FROM amis")
            self._conn.executemany(
                """INSERT INTO amis (id, username, avatar_id, mail, phone, date_of_birth)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                [(a.id, a.username, a.avatar_id, a.mail, a.phone, a.date_of_birth) for a in amis]
            )
        self._set_meta("amis_sync_at", datetime.now().isoformat())
        # Mise à jour du dict (on préserve les statuts en_ligne déjà en mémoire)
        for a in amis:
            if a.id in self._amis:
                a.en_ligne = self._amis[a.id].en_ligne
        self._amis = {a.id: a for a in amis}

    def upsert_ami(self, ami: Ami):
        """Ajoute ou met à jour un ami (ex: friend_request_accepted)."""
        with self._conn:
            self._conn.execute(
                """INSERT OR REPLACE INTO amis
                   (id, username, avatar_id, mail, phone, date_of_birth)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (ami.id, ami.username, ami.avatar_id, ami.mail, ami.phone, ami.date_of_birth)
            )
        self._amis[ami.id] = ami

    def invalider_ami(self, id_: int):
        """Retire un ami du cache (ex: remove_friend)."""
        with self._conn:
            self._conn.execute("DELETE FROM amis WHERE id = ?", (id_,))
        self._amis.pop(id_, None)

    def set_statut_ami(self, id_: int, en_ligne: bool):
        """Met à jour le statut online/offline — dict uniquement, pas SQLite."""
        if id_ in self._amis:
            self._amis[id_].en_ligne = en_ligne

    # ── Invalidation totale (déconnexion) ────────────────────

    def invalider_tout(self):
        """Vide tout le cache. Appelé à la déconnexion."""
        with self._conn:
            self._conn.execute("DELETE FROM amis")
            self._conn.execute("DELETE FROM cache_meta")
        self._amis = {}

    # ── Lecture SQLite brute (usage interne uniquement) ───────

    def _lire_amis_sqlite(self) -> list[Ami]:
        rows = self._conn.execute(
            "SELECT id, username, avatar_id, mail, phone, date_of_birth FROM amis"
        ).fetchall()
        return [Ami(**dict(r)) for r in rows]

    # ── Cycle de vie ─────────────────────────────────────────

    def fermer(self):
        self._conn.close()