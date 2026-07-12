import pandas as pd
import streamlit as st
from utils.data_manager import init_data, get_data, sidebar_data_controls
from utils.ai_helper import sidebar_api_key_input, ai_assist_widget

st.set_page_config(page_title="Plano de Ação 5W2H", page_icon="✅", layout="wide")
init_data()
data = get_data()

st.sidebar.title("🧭 Gestor Estratégico")
#sidebar_api_key_input()
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

# Garantir que todos os itens tenham todas as colunas
for item in itens:
    for col in colunas:
        if col not in item:
            item[col] = ""

# Criar DataFrame com tipos corretos
if itens:
    df = pd.DataFrame(itens)
    for col in colunas:
        if col not in df.columns:
            df[col] = ""
        # Garantir que colunas de texto sejam string
        if col != "status":  # status é seletor, mantém como string
            df[col] = df[col].astype(str)
else:
    # DataFrame vazio com tipos corretos
    df = pd.DataFrame({
        "what": pd.Series(dtype="object"),
        "why": pd.Series(dtype="object"),
        "where": pd.Series(dtype="object"),
        "when": pd.Series(dtype="object"),
        "who": pd.Series(dtype="object"),
        "how": pd.Series(dtype="object"),
        "how_much": pd.Series(dtype="object"),
        "status": pd.Series(dtype="object")
    })

# Hash para forçar recriação
df_hash = hash(str(sorted([str(item) for item in itens]))) if itens else 0
editor_key = f"editor_5w2h_{df_hash}"

edited = st.data_editor(
    df,
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True,
    key=editor_key,
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

# Processar dados editados
if edited is not None:
    edited = edited.fillna("")
    novos_itens = []
    for _, row in edited.iterrows():
        # Verificar se tem pelo menos o "what" preenchido (ação principal)
        what = str(row.get("what", "")).strip()
        if what:  # Só adicionar se tiver o "what"
            novo_item = {}
            for col in colunas:
                valor = row.get(col, "")
                if col == "status" and not valor:
                    valor = "Não iniciado"
                novo_item[col] = str(valor).strip() if col != "status" else valor
            novos_itens.append(novo_item)
    
    if novos_itens != data["acao_5w2h"]:
        data["acao_5w2h"] = novos_itens
        st.rerun()

# Download button precisa usar os dados atuais
if data["acao_5w2h"]:
    df_download = pd.DataFrame(data["acao_5w2h"])
    st.download_button(
        "⬇️ Baixar Plano de Ação (CSV)",
        data=df_download.rename(columns=nomes_colunas).to_csv(index=False).encode("utf-8-sig"),
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
