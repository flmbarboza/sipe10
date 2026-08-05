from pprint import pprint

from .models import Event


def track(
    event,
    module=None,
    duration=None,
    metadata=None,
):
    """
    Registra um evento do sistema.

    Nesta primeira sprint apenas imprime
    o evento no terminal.
    """

    e = Event(
        event=event.value if hasattr(event, "value") else str(event),
        module=module.value if hasattr(module, "value") else (
            module or ""
        ),
        duration=duration,
        metadata=metadata or {},
    )

    print("\n========== EVENT ==========")
    pprint(e)
    print("===========================\n")
