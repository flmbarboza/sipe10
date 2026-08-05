from inspect import stack
from utils.data_manager import get_data
from .buffer import buffer
from .models import Event, now, new_uuid
from .session import get_session, get_operation, module_duration
import time
from copy import deepcopy
from .observer import observer

_last_event = None
# Guarda o estado inicial de cada coleção observada
_state_cache = {}

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
    global _last_event
    agora = time.time()
    if _last_event is None:
        duration = 0
    else:
        duration = int(
            (agora - _last_event) * 1000
        )
    _last_event = agora
    
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
        duration_ms=duration,
        elapsed_module_ms=module_duration(),
        company_name=empresa.get("nome", ""),
        company_sector=empresa.get("setor", ""),
        metadata=metadata
    )

    buffer.add(e)

def begin_observation(key: str, items: list[dict]):
    """
    Salva uma cópia do estado atual.
    """
    _state_cache[key] = deepcopy(items)


def end_observation(
    key: str,
    items: list[dict],
    module,
):
    """
    Compara o estado anterior com o atual e registra os eventos.
    """

    before = _state_cache.get(key)

    if before is None:
        return

    changes = observer.observe(
        before=before,
        after=items
    )

    for change in changes:

        track(
            event=change.event,
            module=module,
            metadata={
                "item_id": change.item_id,
                "fields": ",".join(change.changed_fields)
            }
        )

    _state_cache[key] = deepcopy(items)

# ==========================================================
# Controle de páginas e módulos
# ==========================================================
from .session import module_enter

def init_page(module=None):
    """
    Inicialização da página.
    Registra entrada no módulo quando informado.
    """
    if module is not None:
        module_enter(module)

        track(
            event="page_opened",
            module=module
        )

def module_started(module):
    """
    Registra o início de um módulo.
    """
    module_enter(module)
    track(
        event="module_started",
        module=module
    )

def module_completed(
    module,
    metadata=None
):
    """
    Registra a conclusão de um módulo.
    """
    track(
        event="module_completed",
        module=module,
        metadata=metadata or {}
    )
