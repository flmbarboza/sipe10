import time

import streamlit as st

from .tracker import track
from .enums import EventType


def init_page(module):
    """
    Inicializa o rastreamento de uma página Streamlit.

    Deve ser chamado uma vez no início
    de cada arquivo dentro de pages/.
    """

    key = f"analytics_page_{module.value}"

    if key not in st.session_state:

        st.session_state[key] = {
            "start_time": time.time(),
            "module": module.value,
        }

        track(
            EventType.PAGE_OPEN,
            module=module
        )


def close_page(module):
    """
    Registra encerramento da página.
    """

    key = f"analytics_page_{module.value}"

    if key in st.session_state:

        start = (
            st.session_state[key]
            ["start_time"]
        )

        duration = (
            time.time() - start
        )

        track(
            EventType.PAGE_CLOSE,
            module=module,
            duration=duration
        )

        del st.session_state[key]
