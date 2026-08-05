from pathlib import Path
import sqlite3

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

    def save(self, event: Event):

        self.conn.execute(
            """
            INSERT INTO events
            VALUES(?,?,?,?,?,?,?,?,?)
            """,
            (
                event.event_id,
                event.operation_id,
                event.session_id,
                event.timestamp,
                event.event,
                event.module,
                event.duration,
                str(event.metadata),
                "PENDING"
            )
        )

        self.conn.commit()


storage = Storage()
