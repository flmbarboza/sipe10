from .bus import event_bus
from .models import Event


def track(
    event,
    module=None,
    duration=None,
    metadata=None,
):

    e = Event(
        event=event.value if hasattr(event, "value") else str(event),
        module=module.value if hasattr(module, "value") else (
            module or ""
        ),
        duration=duration,
        metadata=metadata or {},
    )

    event_bus.publish(e)
