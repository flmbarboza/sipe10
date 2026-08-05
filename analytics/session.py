import streamlit as st
import uuid
import time


def module_enter(module):

    st.session_state["analytics_current_module"] = module

    st.session_state["analytics_module_start"] = time.time()


def module_duration():

    inicio = st.session_state.get("analytics_module_start")

    if inicio is None:
        return 0

    return int((time.time() - inicio) * 1000)

def get_session():

    if "analytics_session" not in st.session_state:

        st.session_state.analytics_session = uuid.uuid4().hex

    return st.session_state.analytics_session


def get_operation():

    if "analytics_operation" not in st.session_state:

        st.session_state.analytics_operation = uuid.uuid4().hex

    return st.session_state.analytics_operation


def new_operation():

    st.session_state.analytics_operation = uuid.uuid4().hex

    return st.session_state.analytics_operation
