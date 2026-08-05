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


    def flush():
    
        if not self.events:
            return
    
        try:
    
            sheets.save_many(self.events)
    
        except Exception as e:
    
            print(e)
    
        finally:
    
            self.events.clear()



buffer = Buffer()
