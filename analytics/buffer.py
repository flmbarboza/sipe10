from threading import Lock

from . import sheets


class Buffer:

    def __init__(self):

        self.events = []

        self.lock = Lock()

        self.max_size = 1


    def add(self, event):

        with self.lock:

            self.events.append(event)

            if len(self.events) >= self.max_size:

                self.flush()


    def flush(self):

        if not self.events:
            return

        sheets.save_many(self.events)

        self.events.clear()



buffer = Buffer()
