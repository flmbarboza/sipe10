import pandas as pd
import streamlit as st
from utils.data_manager import init_data, get_data, sidebar_data_controls
from utils.ai_helper import sidebar_api_key_input, ai_assist_widget

st.set_page_config(page_title="5 Forças de Porter", page_icon="⚔️", layout="wide")
init_data()
data = get_data()

st.sidebar.title("🧭 Gestor Estratégico")
sidebar_api_key_input()
sidebar_data_controls()

st.title("⚔️ 5 Forças de Porter")
st.caption(
    "Avalie a intensidade de cada força competitiva do setor (1 = muito baixa, 5 = muito alta) "
    "e registre suas observações. Isso ajuda a construir a Análise SWOT."
)

AJUDA = {
    "Rivalidade entre concorrentes": "Número e força dos concorrentes diretos, guerra de preços, diferenciação.",
    "Poder de barganha dos clientes": "Concentração de clientes, sensibilidade a preço, custo de troca.",
    "Poder de barganha dos fornecedores": "Concentração de fornecedores, insumos críticos, custo de troca.",
    "Ameaça de novos entrantes": "Barreiras de entrada, capital necessário, regulação, economia de escala.",
    "Ameaça de produtos substitutos": "Alternativas que atendem à mesma necessidade do cliente.",
}


def system_prompt():
    return (
        "Você é um consultor especialista no modelo das 5 Forças de Porter. Responda em "
        "português do Brasil, de forma prática e aplicada ao setor e localidade informados."
    )


for forca, ajuda in AJUDA.items():
    st.markdown(f"### {forca}")
    st.caption(ajuda)
    col1, col2 = st.columns([1, 3])
    with col1:
        intensidade = st.slider(
            "Intensidade", min_value=1, max_value=5,
            value=int(data["porter"][forca].get("intensidade", 3)),
            key=f"porter_int_{forca}",
        )
        data["porter"][forca]["intensidade"] = intensidade
    with col2:
        notas = st.text_area(
            "Observações", value=data["porter"][forca].get("notas", ""),
            key=f"porter_notas_{forca}", height=100,
        )
        data["porter"][forca]["notas"] = notas

    def builder(instrucao, forca=forca, ajuda=ajuda):
        setor = data["empresa"].get("setor") or "não informado"
        cidade = data["empresa"].get("cidade_estado") or "não informado"
        atual = data["porter"][forca].get("notas", "")
        base = (
            f"Setor: {setor}. Localização: {cidade}.\n"
            f"Força de Porter: {forca} ({ajuda})\n"
            f"Observações já escritas: {atual or '(vazio)'}\n"
        )
        if instrucao:
            base += f"Pedido específico: {instrucao}\n"
        else:
            base += (
                "Sugira uma análise objetiva desta força para este setor/local, em até 5 bullets, "
                "e indique se a intensidade tende a ser baixa, média ou alta e por quê.\n"
            )
        return base

    ai_assist_widget(f"porter_{forca}", forca, system_prompt(), builder)
    st.markdown("---")

st.subheader("📊 Resumo visual")
df_resumo = pd.DataFrame(
    [{"Força": f, "Intensidade": v["intensidade"]} for f, v in data["porter"].items()]
).set_index("Força")
st.bar_chart(df_resumo)

media = df_resumo["Intensidade"].mean()
st.metric("Intensidade competitiva média do setor", f"{media:.1f} / 5")
