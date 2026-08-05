from .tracker import track
from .operation import Operation
from .enums import EventType
from .enums import Module
from .bus import event_bus
from .console import console_handler
from .buffer import buffer
from .autoflush import autoflush
from .sync import sync_engine
from .migrations import migrate
from .page_tracker import init_page
from .session_manager import (
    init_session,
    update_activity,
    check_timeout
)

migrate()

sync_engine.start()

event_bus.subscribe(console_handler)
event_bus.subscribe(buffer.add)

autoflush.start()
