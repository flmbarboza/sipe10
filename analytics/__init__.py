from .tracker import track
from .enums import EventType, Module
from .bus import event_bus
from .console import console_handler

event_bus.subscribe(console_handler)
