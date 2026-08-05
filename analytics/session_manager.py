import time
import streamlit as st

from .context import current_session
from .tracker import track
from .enums import EventType


SESSION_KEY = "analytics_session"


SESSION_TIMEOUT = 1800  # 30 minutos


def init_session():

    if SESSION_KEY not in st.session_state:

        st.session_state[SESSION_KEY] = {

            "session_id": current_session(),

            "started_at": time.time(),

            "last_activity": time.time(),

        }


        track(
            EventType.SESSION_START
        )


    else:

        update_activity()



def update_activity():

    session = st.session_state[SESSION_KEY]

    session["last_activity"] = time.time()



def close_session():

    if SESSION_KEY not in st.session_state:

        return


    session = st.session_state[SESSION_KEY]


    duration = (
        time.time()
        -
        session["started_at"]
    )


    track(
        EventType.SESSION_END,
        duration=duration
    )


    del st.session_state[SESSION_KEY]



def check_timeout():

    if SESSION_KEY not in st.session_state:

        return


    session = st.session_state[SESSION_KEY]


    inactive = (
        time.time()
        -
        session["last_activity"]
    )


    if inactive > SESSION_TIMEOUT:

        close_session()
