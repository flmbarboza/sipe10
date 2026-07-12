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

        if "pestel" not in data:
            data["pestel"] = {}
        
        # Criar uma cópia dos dados para edição
        itens = data["pestel"].get(cat, [])
        
        # Garantir que todos os itens tenham todos os campos
        for item in itens:
            if "descricao" not in item:
                item["descricao"] = ""
            if "tipo" not in item:
                item["tipo"] = "Oportunidade"
            if "impacto" not in item:
                item["impacto"] = "Médio"
        
        df = pd.DataFrame(itens) if itens else pd.DataFrame(columns=["descricao", "tipo", "impacto"])
        
        # Usar um key único que inclui o estado atual dos dados para forçar recriação
        df_hash = hash(str(itens)) if itens else 0
        editor_key = f"editor_pestel_{cat}_{df_hash}"
        
        edited = st.data_editor(
            df, 
            num_rows="dynamic", 
            width="stretch", 
            key=editor_key,
            column_config={
                "descricao": st.column_config.TextColumn("Descrição do fator", width="large"),
                "tipo": st.column_config.SelectboxColumn("Tipo", options=TIPOS),
                "impacto": st.column_config.SelectboxColumn("Impacto", options=IMPACTOS),
            },
            hide_index=True,
        )
        
        # Verificar se houve mudanças usando comparação profunda
        novos_itens = edited.fillna("").to_dict("records")
        
        # Remover itens vazios (sem descrição)
        novos_itens = [item for item in novos_itens if item.get("descricao", "").strip()]
        
        # Só atualizar se houve mudança real
        itens_atuais = data["pestel"].get(cat, [])
        
        # Comparar de forma robusta
        if len(novos_itens) != len(itens_atuais):
            data["pestel"][cat] = novos_itens
        else:
            # Verificar se o conteúdo mudou
            mudou = False
            for i, (novo, atual) in enumerate(zip(novos_itens, itens_atuais)):
                if novo.get("descricao") != atual.get("descricao") or \
                   novo.get("tipo") != atual.get("tipo") or \
                   novo.get("impacto") != atual.get("impacto"):
                    mudou = True
                    break
            
            if mudou:
                data["pestel"][cat] = novos_itens

        def builder(instrucao, cat=cat, ajuda=ajuda):
            setor = data.get("empresa", {}).get("setor") or "não informado"
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
