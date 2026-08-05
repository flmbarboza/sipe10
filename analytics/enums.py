from enum import Enum


class EventType(str, Enum):
    PAGE_OPEN = "page_open"
    PAGE_CLOSE = "page_close"

    MODULE_START = "module_start"
    MODULE_FINISH = "module_finish"

    SESSION_START = "session_start"

    SESSION_END = "session_end"
    
    BUTTON_CLICK = "button_click"

    SAVE = "save"

    AI_REQUEST = "ai_request"
    AI_RESPONSE = "ai_response"

    PDF_EXPORT = "pdf_export"

    ERROR = "error"


class Module(str, Enum):
    HOME = "home"

    CANVAS = "canvas"

    PESTEL = "pestel"

    PORTER = "porter"

    SWOT = "swot"

    PLANEJAMENTO = "planejamento"

    FINANCEIRO = "financeiro"

    PLANO_ACAO = "plano_acao"

    MONITORAMENTO = "monitoramento"

    REVIEW = "revisao"

    PAINEL = "painel"

    RELATORIO = "relatorio"

    SYSTEM = "system"
