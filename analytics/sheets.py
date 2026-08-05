import gspread
import streamlit as st
from google.oauth2.service_account import Credentials


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets"
]


def get_client():

    credentials = Credentials.from_service_account_info(
        st.secrets["google_service_account"],
        scopes=SCOPES
    )

    return gspread.authorize(credentials)



def save_many(events):

    client = get_client()

    sheet = client.open(
        "SIPE10 Analytics"
    ).worksheet(
        "events"
    )

    rows = []

    for e in events:

        rows.append(
            [
                e.timestamp,
                e.event_id,
                e.operation_id,
                e.session_id,
                e.event,
                e.module,
                str(e.metadata)
            ]
        )

    sheet.append_rows(
        rows,
        value_input_option="USER_ENTERED"
    )
