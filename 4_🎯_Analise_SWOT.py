import pandas as pd
import streamlit as st
from utils.data_manager import init_data, get_data, sidebar_data_controls
from utils.ai_helper import sidebar_api_key_input, ai_assist_widget

st.set_page_config(page_title="Análise SWOT", page_icon="🎯", layout="wide")
init_data()
data = get_data()

st.sidebar.title("🧭 Gestor Estratégico")
sidebar_api_key_input()
sidebar_data_controls()

st.title("🎯 Análise SWOT")
st.caption(
    "Forças e Fraquezas são fatores internos (você controla). Oportunidades e Ameaças são "
    "fatores externos — aqui você pode importar automaticamente o que já foi identificado na "
    "Análise PESTEL e nas 5 Forças de Porter."
)


def itens_pestel_por_tipo(tipo):
    resultado = []
    for cat, itens in data["pestel"].items():
        for item in itens:
            if item.get("tipo") == tipo and item.get("descricao"):
                resultado.append(f"[PESTEL-{cat}] {item['descricao']}")
    return resultado


def itens_porter_alerta():
    alertas = []
    for forca, info in data["porter"].items():
        if info.get("intensidade", 0) >= 4:
            nota = f" — {info['notas']}" if info.get("notas") else ""
            alertas.append(f"[Porter] {forca} está com intensidade alta{nota}")
    return alertas


col_import1, col_import2 = st.columns(2)
with col_import1:
    if st.button("⬇️ Importar Oportunidades da Análise PESTEL", use_container_width=True):
        novas = itens_pestel_por_tipo("Oportunidade")
        existentes = {i["descricao"] for i in data["swot"]["oportunidades"]}
        for texto in novas:
            if texto not in existentes:
                data["swot"]["oportunidades"].append({"descricao": texto})
        st.success(f"{len(novas)} itens verificados/importados.")
        st.rerun()
with col_import2:
    if st.button("⬇️ Importar Ameaças do PESTEL + Porter", use_container_width=True):
        novas = itens_pestel_por_tipo("Ameaça") + itens_porter_alerta()
        existentes = {i["descricao"] for i in data["swot"]["ameacas"]}
        for texto in novas:
            if texto not in existentes:
                data["swot"]["ameacas"].append({"descricao": texto})
        st.success(f"{len(novas)} itens verificados/importados.")
        st.rerun()

st.divider()


def system_prompt():
    return (
        "Você é um consultor de estratégia especialista em análise SWOT. Responda em português "
        "do Brasil, de forma objetiva e prática, considerando o contexto informado."
    )


QUADRANTES = [
    ("forcas", "💪 Forças (interno)", "Vantagens internas: o que a empresa faz bem, recursos únicos, diferenciais."),
    ("fraquezas", "⚠️ Fraquezas (interno)", "Pontos internos a melhorar: limitações de recursos, processos, equipe."),
    ("oportunidades", "🌱 Oportunidades (externo)", "Fatores externos favoráveis que a empresa pode aproveitar."),
    ("ameacas", "🌩️ Ameaças (externo)", "Fatores externos desfavoráveis que podem prejudicar a empresa."),
]

col_a, col_b = st.columns(2)
cols_map = {0: col_a, 1: col_b, 2: col_a, 3: col_b}

for i, (chave, titulo, ajuda) in enumerate(QUADRANTES):
    with cols_map[i]:
        st.markdown(f"#### {titulo}")
        st.caption(ajuda)
        itens = data["swot"].get(chave, [])
        df = pd.DataFrame(itens) if itens else pd.DataFrame(columns=["descricao"])
        if "descricao" not in df.columns:
            df["descricao"] = ""
        edited = st.data_editor(
            df, num_rows="dynamic", use_container_width=True,
            key=f"editor_swot_{chave}", hide_index=True,
            column_config={"descricao": st.column_config.TextColumn("Item", width="large")},
        )
        data["swot"][chave] = edited.fillna("").to_dict("records")

        def builder(instrucao, chave=chave, titulo=titulo, ajuda=ajuda):
            empresa = data["empresa"].get("nome") or "a empresa"
            setor = data["empresa"].get("setor") or "não informado"
            atuais = "; ".join([i.get("descricao", "") for i in data["swot"].get(chave, []) if i.get("descricao")])
            base = (
                f"Empresa: {empresa}. Setor: {setor}.\n"
                f"Quadrante SWOT: {titulo} ({ajuda})\n"
                f"Itens já listados: {atuais or '(nenhum ainda)'}\n"
            )
            if instrucao:
                base += f"Pedido específico: {instrucao}\n"
            else:
                base += "Sugira de 3 a 5 itens objetivos e específicos para este quadrante.\n"
            return base

        ai_assist_widget(f"swot_{chave}", titulo, system_prompt(), builder)

st.divider()
st.info(
    "💡 Depois de concluir a SWOT, vá para **🧭 Planejamento Estratégico** para construir "
    "a **SWOT Cruzada** (cruzamento de Forças/Fraquezas com Oportunidades/Ameaças)."
)
