import threading
import time

from .storage import storage
from .google_sheets import GoogleSheetsDestination


class SyncEngine:

    def __init__(self):

        self.destination = GoogleSheetsDestination()

        self.interval = 60

        self.running = False

    def worker(self):

        while self.running:

            time.sleep(self.interval)

            events = storage.get_pending(100)

            if not events:
                continue

            ok = self.destination.send(events)

            if ok:

                ids = [
                    e["event_id"]
                    for e in events
                ]

                storage.mark_sent(ids)

    def start(self):

        if self.running:
            return

        self.running = True

        threading.Thread(
            target=self.worker,
            daemon=True
        ).start()


sync_engine = SyncEngine()
