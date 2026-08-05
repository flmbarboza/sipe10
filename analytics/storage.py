from pathlib import Path
import sqlite3
import json

from .models import Event

DB_PATH = Path("analytics.db")


class Storage:

    def __init__(self):

        self.conn = sqlite3.connect(
            DB_PATH,
            check_same_thread=False
        )

        self.create_tables()

    def create_tables(self):

        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS events(

            event_id TEXT PRIMARY KEY,

            operation_id TEXT,

            session_id TEXT,

            timestamp TEXT,

            event TEXT,

            module TEXT,

            duration REAL,

            metadata TEXT,

            status TEXT
        )
        """)

        self.conn.commit()

    def save_many(self, events: list[Event]):

        if not events:
            return

        rows = []

        for e in events:

            rows.append(
                (
                    e.event_id,
                    e.operation_id,
                    e.session_id,
                    e.timestamp,
                    e.event,
                    e.module,
                    e.duration,
                    json.dumps(e.metadata, ensure_ascii=False),
                    "PENDING",
                )
            )

        self.conn.executemany(
            """
            INSERT INTO events
            (
                event_id,
                operation_id,
                session_id,
                timestamp,
                event,
                module,
                duration,
                metadata,
                status,
                app_version
            )
            VALUES (?,?,?,?,?,?,?,?,?,?)
            """,
            rows,
        )

    def get_pending(self, limit=100):

        cursor = self.conn.execute(
            """
            SELECT
                event_id,
                operation_id,
                session_id,
                timestamp,
                event,
                module,
                duration,
                metadata
            FROM events
            WHERE status='PENDING'
            ORDER BY timestamp
            LIMIT ?
            """,
            (limit,)
        )

        rows = cursor.fetchall()

        events = []

        for row in rows:

            events.append({

                "event_id": row[0],
                "operation_id": row[1],
                "session_id": row[2],
                "timestamp": row[3],
                "event": row[4],
                "module": row[5],
                "duration": row[6],
                "metadata": json.loads(row[7]),
            })

        return events


    def mark_sent(self, ids):

        if not ids:
            return

        self.conn.executemany(
            """
            UPDATE events
            SET status='SENT'
            WHERE event_id=?
            """,
            [(i,) for i in ids]
        )

        self.conn.commit()

storage = Storage()
