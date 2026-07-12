import pandas as pd
import streamlit as st
from utils.data_manager import init_data, get_data, sidebar_data_controls
from utils.ai_helper import sidebar_api_key_input, ai_assist_widget

st.set_page_config(page_title="Plano de Ação 5W2H", page_icon="✅", layout="wide")
init_data()
data = get_data()

st.sidebar.title("🧭 Gestor Estratégico")
sidebar_api_key_input()
sidebar_data_controls()

st.title("✅ Plano de Ação (5W2H)")
st.caption(
    "What (o quê), Why (por quê), Where (onde), When (quando), Who (quem), "
    "How (como) e How much (quanto custa)."
)

itens = data["acao_5w2h"]
colunas = ["what", "why", "where", "when", "who", "how", "how_much", "status"]
nomes_colunas = {
    "what": "O quê (What)",
    "why": "Por quê (Why)",
    "where": "Onde (Where)",
    "when": "Quando (When)",
    "who": "Quem (Who)",
    "how": "Como (How)",
    "how_much": "Quanto custa (How much)",
    "status": "Status",
}

df = pd.DataFrame(itens) if itens else pd.DataFrame(columns=colunas)
for col in colunas:
    if col not in df.columns:
        df[col] = ""

edited = st.data_editor(
    df,
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True,
    key="editor_5w2h",
    column_config={
        "what": st.column_config.TextColumn(nomes_colunas["what"], width="large"),
        "why": st.column_config.TextColumn(nomes_colunas["why"], width="large"),
        "where": st.column_config.TextColumn(nomes_colunas["where"]),
        "when": st.column_config.TextColumn(nomes_colunas["when"]),
        "who": st.column_config.TextColumn(nomes_colunas["who"]),
        "how": st.column_config.TextColumn(nomes_colunas["how"], width="large"),
        "how_much": st.column_config.TextColumn(nomes_colunas["how_much"]),
        "status": st.column_config.SelectboxColumn(
            nomes_colunas["status"], options=["Não iniciado", "Em andamento", "Concluído", "Atrasado"]
        ),
    },
)
data["acao_5w2h"] = edited.fillna("").to_dict("records")

st.download_button(
    "⬇️ Baixar Plano de Ação (CSV)",
    data=edited.rename(columns=nomes_colunas).to_csv(index=False).encode("utf-8-sig"),
    file_name="plano_de_acao_5w2h.csv",
    mime="text/csv",
)

st.divider()


def system_prompt():
    return (
        "Você é um consultor de gestão especializado em planos de ação (5W2H). Responda em "
        "português do Brasil, de forma prática e orientada a execução."
    )


def builder(instrucao):
    empresa = data["empresa"].get("nome") or "a empresa"
    objetivos = "; ".join([o.get("objetivo", "") for o in data.get("objetivos", []) if o.get("objetivo")])
    base = (
        f"Empresa: {empresa}.\n"
        f"Objetivos estratégicos definidos: {objetivos or '(nenhum ainda)'}\n"
    )
    base += instrucao if instrucao else (
        "Sugira de 3 a 5 ações no formato 5W2H (What, Why, Where, When, Who, How, How much) "
        "para colocar em prática os objetivos estratégicos acima, uma ação por linha, formato de tabela em texto.\n"
    )
    return base


ai_assist_widget("acao_5w2h_geral", "Plano de Ação 5W2H", system_prompt(), builder)
