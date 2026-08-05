from .bus import event_bus
from .context import current_operation
from .context import current_session
from .environment import get_environment
from .models import Event



def track(
    event,
    module=None,
    duration=None,
    metadata=None,
):

    event_metadata = {}

    event_metadata.update(
        get_environment()
    )


    if metadata:

        event_metadata.update(
            metadata
        )


    e = Event(

        operation_id=
        current_operation() or "",

        session_id=
        current_session(),

        event=
        event.value
        if hasattr(event, "value")
        else str(event),


        module=
        module.value
        if hasattr(module, "value")
        else (module or ""),


        duration=duration,


        metadata=event_metadata
    )


    event_bus.publish(e)
