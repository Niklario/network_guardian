
import sqlite3
import hashlib
import json
import time
from datetime import datetime


class Database:

    def __init__(self):
        self.conn = sqlite3.connect(
            "/data/network_guardian.db"
        )
        self.conn.row_factory = sqlite3.Row

        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA busy_timeout=5000")

        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS dns_queries (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                epoch REAL NOT NULL,
                client TEXT NOT NULL,
                domain TEXT NOT NULL,
                query_type TEXT,
                reason TEXT,
                status TEXT,
                blocked INTEGER,
                cached INTEGER,
                elapsed_ms REAL,
                upstream TEXT,
                answers TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_epoch
            ON dns_queries(epoch);

            CREATE INDEX IF NOT EXISTS idx_client_epoch
            ON dns_queries(client, epoch);

            CREATE INDEX IF NOT EXISTS idx_client_domain
            ON dns_queries(client, domain);

            CREATE TABLE IF NOT EXISTS security_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                client TEXT,
                event_type TEXT,
                severity TEXT,
                message TEXT
            );

            CREATE TABLE IF NOT EXISTS metadata (
                key TEXT PRIMARY KEY,
                value TEXT
            );
        """)

        self.conn.commit()

    def get_meta(self, key, default=None):
        row = self.conn.execute(
            "SELECT value FROM metadata WHERE key=?",
            (key,)
        ).fetchone()

        return row["value"] if row else default

    def set_meta(self, key, value):
        with self.conn:
            self.conn.execute("""
                INSERT INTO metadata(key, value)
                VALUES (?, ?)
                ON CONFLICT(key)
                DO UPDATE SET value=excluded.value
            """, (key, str(value)))

    def save_queries(self, entries):
        inserted = 0

        with self.conn:
            for entry in entries:
                question = entry.get("question", {})
                timestamp = entry["time"]

                epoch = datetime.fromisoformat(
                    timestamp.replace("Z", "+00:00")
                ).timestamp()

                client = entry.get("client", "unknown")
                domain = question.get("name", "").lower()
                query_type = question.get("type", "")
                reason = entry.get("reason", "")

                identity = json.dumps([
                    timestamp,
                    client,
                    domain,
                    query_type,
                    entry.get("client_proto", "")
                ])

                query_id = hashlib.sha256(
                    identity.encode()
                ).hexdigest()

                blocked = int(
                    reason.startswith("Filtered")
                )

                cursor = self.conn.execute("""
                    INSERT OR IGNORE INTO dns_queries
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?,
                            ?, ?, ?, ?)
                """, (
                    query_id,
                    timestamp,
                    epoch,
                    client,
                    domain,
                    query_type,
                    reason,
                    entry.get("status", ""),
                    blocked,
                    int(entry.get("cached", False)),
                    float(entry.get("elapsedMs") or 0),
                    entry.get("upstream", ""),
                    json.dumps(entry.get("answer", []))
                ))

                inserted += cursor.rowcount

        return inserted

    def total_queries(self):
        return self.conn.execute(
            "SELECT COUNT(*) FROM dns_queries"
        ).fetchone()[0]

    def cleanup(self, retention_days):
        cutoff = time.time() - retention_days * 86400

        with self.conn:
            self.conn.execute(
                "DELETE FROM dns_queries WHERE epoch < ?",
                (cutoff,)
            )

            self.conn.execute("""
                DELETE FROM security_events
                WHERE timestamp < ?
            """, (cutoff,))

    def save_event(self, client, event_type,
                   severity, message, cooldown=3600):

        now = time.time()

        existing = self.conn.execute("""
            SELECT id FROM security_events
            WHERE client = ?
              AND event_type = ?
              AND timestamp > ?
            LIMIT 1
        """, (
            client,
            event_type,
            now - cooldown
        )).fetchone()

        if existing:
            return False

        with self.conn:
            self.conn.execute("""
                INSERT INTO security_events
                (timestamp, client, event_type,
                 severity, message)
                VALUES (?, ?, ?, ?, ?)
            """, (
                now, client, event_type,
                severity, message
            ))

        return True
