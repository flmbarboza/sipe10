import platform
import socket
import sys


APP_VERSION = "1.0.0"


def get_environment():

    try:
        import streamlit

        streamlit_version = streamlit.__version__

    except Exception:

        streamlit_version = None


    return {

        "app_version": APP_VERSION,

        "python_version": sys.version.split()[0],

        "streamlit_version": streamlit_version,

        "platform": platform.platform(),

        "machine": platform.machine(),

        "hostname": socket.gethostname(),

    }
