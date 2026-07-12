import streamlit as st
from utils.data_manager import init_data, get_data, sidebar_data_controls
from utils.ai_helper import sidebar_api_key_input

st.set_page_config(
    page_title="Gestor Estratégico",
    page_icon="🧭",
    layout="wide",
)

init_data()
data = get_data()

# ---------- Barra lateral (comum a todas as páginas) ----------
st.sidebar.title("🧭 Gestor Estratégico")
#sidebar_api_key_input()
#st.divider() if False else None
sidebar_data_controls()

# ---------- Conteúdo da Home ----------
st.title("🧭 Gestor Estratégico")
st.caption("Ferramenta de apoio ao planejamento estratégico de empresas")

st.markdown("""
Bem-vindo! Este aplicativo guia você pela construção do planejamento estratégico
completo da sua empresa, do modelo de negócio ao plano de ação. Use o menu na
barra lateral para navegar entre as etapas.
""")

with st.form("form_empresa"):
    st.subheader("🏢 Dados da empresa")
    col1, col2 = st.columns(2)
    with col1:
        nome = st.text_input("Nome da empresa", value=data["empresa"]["nome"])
        setor = st.text_input("Setor / Segmento", value=data["empresa"]["setor"])
    with col2:
        cidade = st.text_input("Cidade/Estado", value=data["empresa"]["cidade_estado"])
        responsavel = st.text_input("Responsável pelo planejamento", value=data["empresa"]["responsavel"])
    salvar = st.form_submit_button("Salvar dados da empresa", width="stretch")
    if salvar:
        data["empresa"].update(
            {"nome": nome, "setor": setor, "cidade_estado": cidade, "responsavel": responsavel}
        )
        st.success("Dados da empresa salvos!")

st.divider()

st.subheader("🗺️ Roteiro do planejamento")

etapas = [
    ("📋", "Business Model Canvas", "Os 9 blocos do seu modelo de negócio."),
    ("🌍", "Análise PESTEL", "Fatores externos: Político, Econômico, Social, Tecnológico, Ecológico, Legal."),
    ("⚔️", "5 Forças de Porter", "Intensidade competitiva do setor."),
    ("🎯", "Análise SWOT", "Forças, Fraquezas, Oportunidades e Ameaças, alimentada pelas análises acima."),
    ("🧭", "Planejamento Estratégico", "Missão, Visão, Valores, SWOT cruzada, Objetivos e KPIs."),
    ("💰", "Plano Financeiro", "Receitas, custos, investimento e projeção."),
    ("✅", "Plano de Ação (5W2H)", "O que, por quê, onde, quando, quem, como e quanto custa."),
    ("📄", "Relatório Completo", "Compilação de tudo, pronta para exportar em PDF/Markdown."),
]

cols = st.columns(2)
for i, (icone, titulo, desc) in enumerate(etapas):
    with cols[i % 2]:
        st.markdown(f"**{icone} {titulo}**")
        st.caption(desc)

st.info(
    "💡 Use o botão **'⬇️ Baixar dados (.json)'** na barra lateral sempre que quiser "
    "salvar seu progresso, e **'⬆️ Carregar dados (.json)'** para retomar depois.",
    icon="💡",
)
