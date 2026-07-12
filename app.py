import streamlit as st

st.set_page_config(
    page_title="SIPE",
    page_icon="🎯",
    layout="wide"
)

# Estado do tema
if "tema" not in st.session_state:
    st.session_state.tema = "claro"


# CSS do tema
if st.session_state.tema == "escuro":
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #0e1117;
            color: white;
        }

        </style>
        """,
        unsafe_allow_html=True
    )


# Cabeçalho personalizado
col1, col2 = st.columns([8, 1])

with col1:
    st.title("🎯 SIPE")
    st.caption("Sistema Integrado de Planejamento Estratégico")

with col2:
    if st.session_state.tema == "claro":
        icone = "🌙"
        tooltip = "Modo escuro"
    else:
        icone = "☀️"
        tooltip = "Modo claro"

    if st.button(icone, help=tooltip):
        if st.session_state.tema == "claro":
            st.session_state.tema = "escuro"
        else:
            st.session_state.tema = "claro"

        st.rerun()
        
st.switch_page("pages/00_🏠_Início.py")
