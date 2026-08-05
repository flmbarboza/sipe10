import streamlit as st
import uuid


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
