import sqlite3

from .storage import DB_PATH


def migrate():

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.execute(
        """
        PRAGMA table_info(events)
        """
    )

    columns = [
        row[1]
        for row in cursor.fetchall()
    ]


    if "app_version" not in columns:

        conn.execute(
            """
            ALTER TABLE events
            ADD COLUMN app_version TEXT
            """
        )


    conn.commit()

    conn.close()
