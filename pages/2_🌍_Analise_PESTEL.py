import pandas as pd
import streamlit as st
from utils.data_manager import init_data, get_data, sidebar_data_controls
from utils.ai_helper import sidebar_api_key_input, ai_assist_widget

st.set_page_config(page_title="Análise PESTEL", page_icon="🌍", layout="wide")
init_data()
data = get_data()

st.sidebar.title("🧭 Gestor Estratégico")
#sidebar_api_key_input()
sidebar_data_controls()

st.title("🌍 Análise PESTEL")
st.caption(
    "Mapeie os fatores externos que afetam o negócio. Estes itens poderão ser usados "
    "depois para alimentar a Análise SWOT (Oportunidades e Ameaças)."
)

CATEGORIAS = {
    "Político": "Legislação, estabilidade política, políticas públicas, tributação...",
    "Econômico": "Inflação, câmbio, juros, renda, ciclo econômico, crédito...",
    "Social": "Comportamento do consumidor, demografia, cultura, tendências sociais...",
    "Tecnológico": "Inovações, automação, novas plataformas, obsolescência...",
    "Ecológico": "Sustentabilidade, clima, regulação ambiental, escassez de recursos...",
    "Legal": "Normas setoriais, direito do consumidor, trabalhista, regulatório...",
}

IMPACTOS = ["Alto", "Médio", "Baixo"]
TIPOS = ["Oportunidade", "Ameaça"]


def system_prompt():
    return (
        "Você é um consultor especialista em análise de ambiente externo (PESTEL) para empresas "
        "no Brasil. Responda em português, de forma objetiva, com exemplos concretos e atuais "
        "aplicáveis ao setor informado."
    )


tabs = st.tabs(list(CATEGORIAS.keys()))

for tab, (cat, ajuda) in zip(tabs, CATEGORIAS.items()):
    with tab:
        st.markdown(f"**{cat}** — {ajuda}")

        itens = data["pestel"].get(cat, [])
        df = pd.DataFrame(itens) if itens else pd.DataFrame(columns=["descricao", "tipo", "impacto"])
        for col, default in [("descricao", ""), ("tipo", "Oportunidade"), ("impacto", "Médio")]:
            if col not in df.columns:
                df[col] = default

        edited = st.data_editor(
            df,
            num_rows="dynamic",
            width="stretch",
            key=f"editor_pestel_{cat}",
            column_config={
                "descricao": st.column_config.TextColumn("Descrição do fator", width="large"),
                "tipo": st.column_config.SelectboxColumn("Tipo", options=TIPOS),
                "impacto": st.column_config.SelectboxColumn("Impacto", options=IMPACTOS),
            },
            hide_index=True,
        )
        data["pestel"][cat] = (
            edited
            .fillna("")
            .to_dict("records")
        )
        #st.write("EDITOR:")
        #st.write(edited)
        
        #st.write("DATA:")
        #st.write(data["pestel"][cat])


        def builder(instrucao, cat=cat, ajuda=ajuda):
            setor = data["empresa"].get("setor") or "não informado"
            itens_atuais = data["pestel"].get(cat, [])
            resumo = "; ".join([i.get("descricao", "") for i in itens_atuais if i.get("descricao")])
            base = (
                f"Setor da empresa: {setor}.\n"
                f"Dimensão PESTEL: {cat} ({ajuda})\n"
                f"Fatores já listados pelo usuário: {resumo or '(nenhum ainda)'}\n"
            )
            if instrucao:
                base += f"Pedido específico: {instrucao}\n"
            else:
                base += (
                    "Sugira de 3 a 5 fatores relevantes desta dimensão para este setor, "
                    "indicando se cada um tende a ser Oportunidade ou Ameaça, em formato de lista curta.\n"
                )
            return base

        ai_assist_widget(f"pestel_{cat}", cat, system_prompt(), builder)

st.divider()
st.info(
    "💡 Preencha também a página **⚔️ 5 Forças de Porter**. Depois, vá para "
    "**🎯 Análise SWOT** para consolidar tudo automaticamente."
)
