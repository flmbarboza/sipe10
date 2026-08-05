from enum import Enum


from enum import Enum


class EventType(str, Enum):

    MODULE_START = "module_start"
    MODULE_FINISH = "module_finish"
    
    # Sessão
    SESSION_START = "session_start"
    SESSION_END = "session_end"


    # Navegação
    PAGE_OPEN = "page_open"
    PAGE_CLOSE = "page_close"


    # Jornada estratégica
    STRATEGY_STARTED = "strategy_started"
    STRATEGY_COMPLETED = "strategy_completed"


    # Canvas
    CANVAS_STARTED = "canvas_started"
    CANVAS_SAVED = "canvas_saved"
    CANVAS_COMPLETED = "canvas_completed"


    # Ambiente externo
    PESTEL_STARTED = "pestel_started"
    PESTEL_COMPLETED = "pestel_completed"


    # Competição
    PORTER_STARTED = "porter_started"
    PORTER_COMPLETED = "porter_completed"


    # Diagnóstico
    SWOT_STARTED = "swot_started"
    SWOT_COMPLETED = "swot_completed"


    # Planejamento
    PLAN_STARTED = "plan_started"
    PLAN_COMPLETED = "plan_completed"


    # Financeiro
    FINANCE_STARTED = "finance_started"
    FINANCE_COMPLETED = "finance_completed"


    # Plano de ação
    ACTION_PLAN_STARTED = "action_plan_started"
    ACTION_PLAN_COMPLETED = "action_plan_completed"


    # IA
    AI_REQUEST = "ai_request"
    AI_RESPONSE = "ai_response"
    AI_ERROR = "ai_error"


    # Exportação
    PDF_GENERATED = "pdf_generated"


    # Sistema
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
