from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4


@dataclass(slots=True)
class Event:

    event_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    operation_id: str = ""

    session_id: str = ""

    timestamp: str = field(
        default_factory=lambda:
        datetime.now(timezone.utc).isoformat()
    )

    event: str = ""

    module: str = ""

    duration: float | None = None

    metadata: dict = field(
        default_factory=dict
    )
