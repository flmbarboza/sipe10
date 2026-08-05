import gspread
import streamlit as st
from google.oauth2.service_account import Credentials


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]


def get_client():

    credentials = Credentials.from_service_account_info(
        st.secrets["google_service_account"],
        scopes=SCOPES
    )

    return gspread.authorize(credentials)



def save_many(events):

    print("INICIANDO GOOGLE SHEETS")

    client = get_client()

    spreadsheet = client.open("SIPE10 Analytics")

    sheet = spreadsheet.worksheet("events")

    sheet.append_row(
        [
            "teste",
            "analytics",
            "funcionando"
        ]
    )
