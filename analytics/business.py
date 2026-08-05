from .tracker import track
from .enums import EventType
from .enums import Module



def strategy_started():

    track(
        EventType.STRATEGY_STARTED,
        module=Module.SYSTEM
    )



def strategy_completed():

    track(
        EventType.STRATEGY_COMPLETED,
        module=Module.SYSTEM
    )



def module_started(module):

    track(
        EventType.MODULE_START,
        module=module
    )



def module_completed(
    module,
    metadata=None
):

    track(
        EventType.MODULE_FINISH,
        module=module,
        metadata=metadata
    )



def pdf_generated(
    pages=None
):

    track(
        EventType.PDF_GENERATED,
        module=Module.RELATORIO,
        metadata={
            "pages": pages
        }
    )
