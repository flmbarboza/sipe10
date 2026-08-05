from .bus import event_bus
from .context import current_operation
from .context import current_session
from .models import Event


def track(
    event,
    module=None,
    duration=None,
    metadata=None,
):

    e = Event(

        operation_id=current_operation() or "",

        session_id=current_session(),

        event=event.value if hasattr(event, "value") else str(event),

        module=module.value if hasattr(module, "value") else (
            module or ""
        ),

        duration=duration,

        metadata=metadata or {}
    )

    event_bus.publish(e)
