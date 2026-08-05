from .storage import storage


class Buffer:

    def __init__(self):

        self.events = []

        self.max_size = 50

    def add(self, event):

        self.events.append(event)

        if len(self.events) >= self.max_size:

            self.flush()

    def flush(self):

        for e in self.events:

            storage.save(e)

        self.events.clear()


buffer = Buffer()
