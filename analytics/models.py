from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4


@dataclass(slots=True)
class Event:
    """
    Representa um evento único ocorrido no sistema.
    """

    # Identificador do evento
    event_id: str = field(default_factory=lambda: str(uuid4()))

    # Agrupa eventos da mesma operação
    operation_id: str = ""

    # Agrupa toda a navegação do usuário
    session_id: str = ""

    # Momento UTC
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    # Tipo do evento
    event: str = ""

    # Canvas, SWOT, Financeiro...
    module: str = ""

    # Quanto tempo levou
    duration: float | None = None

    # Dados específicos
    metadata: dict = field(default_factory=dict)
