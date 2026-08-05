from contextvars import ContextVar
from uuid import uuid4

_operation_id = ContextVar(
    "operation_id",
    default=None
)

_session_id = ContextVar(
    "session_id",
    default=str(uuid4())
)


def current_session():

    sid = _session_id.get()

    if sid is None:
        sid = str(uuid4())
        _session_id.set(sid)

    return sid


def current_operation():

    return _operation_id.get()


def start_operation():

    op = str(uuid4())

    _operation_id.set(op)

    return op


def finish_operation():

    _operation_id.set(None)
