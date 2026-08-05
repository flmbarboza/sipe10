from typing import Callable

from .models import Event


class EventBus:
    """Distribui eventos para todos os consumidores registrados."""

    def __init__(self):
        self._subscribers: list[Callable[[Event], None]] = []

    def subscribe(self, handler: Callable[[Event], None]):
        """Registra um consumidor de eventos."""
        self._subscribers.append(handler)

    def publish(self, event: Event):
        """Envia um evento para todos os consumidores."""
        for handler in self._subscribers:
            try:
                handler(event)
            except Exception as e:
                print(f"[Analytics] Erro no subscriber: {e}")


event_bus = EventBus()
