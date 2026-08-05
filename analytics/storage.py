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
            VALUES (?,?,?,?,?,?,?,?,?)
            """,
            rows,
        )

        self.conn.commit()


storage = Storage()
