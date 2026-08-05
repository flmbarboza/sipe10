from time import perf_counter

from .context import finish_operation
from .context import start_operation
from .enums import EventType
from .tracker import track


class Operation:

    def __init__(self, module):

        self.module = module

    def __enter__(self):

        self.start = perf_counter()

        start_operation()

        track(
            EventType.MODULE_START,
            module=self.module
        )

        return self

    def __exit__(self, exc_type, exc, tb):

        elapsed = perf_counter() - self.start

        if exc is None:

            track(
                EventType.MODULE_FINISH,
                module=self.module,
                duration=elapsed
            )

        else:

            track(
                EventType.ERROR,
                module=self.module,
                metadata={
                    "error": str(exc)
                }
            )

        finish_operation()

        return False
