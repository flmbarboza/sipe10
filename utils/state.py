import streamlit as st


def inicializar_estado():
    """
    Inicializa a estrutura de dados do planejamento.
    Executar no início de cada página.
    """

    if "data" not in st.session_state:

        st.session_state.data = {

            "empresa": {
                "nome": "",
                "segmento": "",
                "descricao": ""
            },

            "pestel": {},

            "swot": {
                "forcas": [],
                "fraquezas": [],
                "oportunidades": [],
                "ameacas": []
            },

            "canvas": {},

            "objetivos": [],

            "acoes": []
        }


def obter_dados():

    inicializar_estado()

    return st.session_state.data


def atualizar_dados(chave, valor):

    inicializar_estado()

    st.session_state.data[chave] = valor


def limpar_dados():

    if "data" in st.session_state:
        del st.session_state.data
