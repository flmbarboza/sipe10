from inspect import stack

from utils.data_manager import get_data

from .buffer import buffer
from .models import Event, now, new_uuid
from .session import get_session, get_operation


_last_timestamp = None


def _page_name():

    try:
        frame = stack()[2]
        return frame.filename.split("/")[-1]

    except Exception:
        return ""


def track(
    event,
    module,
    action="",
    metadata=None
):

    global _last_timestamp

    if metadata is None:
        metadata = {}

    data = get_data()

    empresa = data.get("empresa", {})

    e = Event(
        timestamp=now(),
        event_id=new_uuid(),
        session_id=get_session(),
        operation_id=get_operation(),
        page=_page_name(),
        module=module,
        event=event,
        action=action,
        company_name=empresa.get("nome", ""),
        company_sector=empresa.get("setor", ""),
        metadata=metadata
    )

    buffer.add(e)
