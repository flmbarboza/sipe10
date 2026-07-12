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
        
        # Garantir que a categoria existe
        if cat not in data["pestel"]:
            data["pestel"][cat] = []
        
        # Buscar dados atuais
        itens = data["pestel"].get(cat, [])
        
        # Criar DataFrame garantindo colunas com valores padrão
        if itens:
            df = pd.DataFrame(itens)
            # Garantir colunas existentes
            for col in ["descricao", "tipo", "impacto"]:
                if col not in df.columns:
                    if col == "tipo":
                        df[col] = "Oportunidade"
                    elif col == "impacto":
                        df[col] = "Médio"
                    else:
                        df[col] = ""
        else:
            # DataFrame vazio com estrutura correta
            df = pd.DataFrame({
                "descricao": pd.Series(dtype="string"),
                "tipo": pd.Series(dtype="string"),
                "impacto": pd.Series(dtype="string")
            })
        
        # CORREÇÃO: Definir valores padrão para novas linhas
        # Criar um dicionário de defaults para o data_editor
        column_defaults = {
            "descricao": "",
            "tipo": "Oportunidade",
            "impacto": "Médio"
        }
        
        # Usar uma chave estável baseada no estado atual
        editor_key = f"editor_pestel_{cat}"
        
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
            # CORREÇÃO PRINCIPAL: Forçar valores padrão para novas linhas
            column_defaults=column_defaults
        )
        
        # Processar dados editados
        if edited is not None and not edited.empty:
            # Substituir NaN por valores vazios
            edited = edited.fillna("")
            
            # Para novas linhas, garantir que tipo e impacto tenham valores
            for idx, row in edited.iterrows():
                if pd.isna(row.get("tipo")) or row.get("tipo") == "":
                    edited.at[idx, "tipo"] = "Oportunidade"
                if pd.isna(row.get("impacto")) or row.get("impacto") == "":
                    edited.at[idx, "impacto"] = "Médio"
            
            # Converter para lista de dicionários, ignorando linhas sem descrição
            novos_itens = []
            for _, row in edited.iterrows():
                descricao = row.get("descricao", "").strip()
                if descricao:  # Só adicionar se tiver descrição
                    novos_itens.append({
                        "descricao": descricao,
                        "tipo": row.get("tipo", "Oportunidade"),
                        "impacto": row.get("impacto", "Médio")
                    })
            
            # Atualizar dados apenas se houve mudança
            if novos_itens != data["pestel"].get(cat, []):
                data["pestel"][cat] = novos_itens
        else:
            # Se o editor está vazio, garantir que a categoria tenha lista vazia
            if data["pestel"].get(cat, []):
                data["pestel"][cat] = []

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
