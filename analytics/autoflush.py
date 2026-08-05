import threading
import time

from .buffer import buffer


class AutoFlush:

    def __init__(self, interval=30):

        self.interval = interval

        self.running = False

    def _worker(self):

        while self.running:

            time.sleep(self.interval)

            buffer.flush()

    def start(self):

        if self.running:
            return

        self.running = True

        threading.Thread(
            target=self._worker,
            daemon=True
        ).start()


autoflush = AutoFlush()
