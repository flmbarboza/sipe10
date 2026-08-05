from .tracker import (
    track,
    init_page,
    module_started,
    module_completed,
    begin_observation,
    end_observation,
)

from .models import Module, Event

from .session import (
    get_session,
    get_operation,
    new_operation,
)


# Compatibilidade com páginas antigas
def init_session():
    return get_session()


def update_activity():
    return None


def check_timeout():
    return False


__all__ = [
    "track",
    "init_page",
    "module_started",
    "module_completed",
    "begin_observation",
    "end_observation",
    "Module",
    "Event",
    "get_session",
    "get_operation",
    "new_operation",
    "init_session",
    "update_activity",
    "check_timeout",
]
