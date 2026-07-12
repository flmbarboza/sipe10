import pandas as pd
import streamlit as st
import json
import re
from utils.data_manager import init_data, get_data, sidebar_data_controls
from openai import OpenAI

st.set_page_config(page_title="Análise PESTEL", page_icon="🌍", layout="wide")
init_data()
data = get_data()

st.sidebar.title("🧭 Gestor Estratégico")
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

def gerar_pestel_ia(categoria=None):
    """Gera análise PESTEL com IA para uma categoria específica ou todas"""
    try:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"], base_url="https://openrouter.ai/api/v1")
        
        empresa_nome = data.get("empresa", {}).get("nome", "a empresa")
        empresa_setor = data.get("empresa", {}).get("setor", "não informado")
        
        if categoria:
            ajuda = CATEGORIAS.get(categoria, "")
            prompt = f"""
            Você é um consultor especialista em análise de ambiente externo (PESTEL) para empresas no Brasil.
            
            INFORMAÇÕES DA EMPRESA:
            - Nome: {empresa_nome}
            - Setor: {empresa_setor}
            
            Dimensão PESTEL: {categoria}
            Descrição: {ajuda}
            
            Gere de 3 a 5 fatores relevantes para esta dimensão, indicando se cada um tende a ser Oportunidade ou Ameaça.
            Responda APENAS com um JSON no formato:
            {{"itens": [
                {{"descricao": "fator1", "tipo": "Oportunidade", "impacto": "Médio"}},
                {{"descricao": "fator2", "tipo": "Ameaça", "impacto": "Alto"}}
            ]}}
            
            Impacto pode ser: "Alto", "Médio" ou "Baixo".
            """
        else:
            prompt = f"""
            Você é um consultor especialista em análise de ambiente externo (PESTEL) para empresas no Brasil.
            
            INFORMAÇÕES DA EMPRESA:
            - Nome: {empresa_nome}
            - Setor: {empresa_setor}
            
            Gere uma análise PESTEL completa para todas as 6 dimensões.
            
            FORMATO DE SAÍDA: Retorne APENAS um JSON com:
            {{
                "Político": [
                    {{"descricao": "fator1", "tipo": "Oportunidade", "impacto": "Médio"}},
                    {{"descricao": "fator2", "tipo": "Ameaça", "impacto": "Alto"}}
                ],
                "Econômico": [...],
                "Social": [...],
                "Tecnológico": [...],
                "Ecológico": [...],
                "Legal": [...]
            }}
            """
        
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": "Você é um consultor especialista em PESTEL. Responda em português do Brasil. Retorne APENAS JSON válido."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        conteudo = response.choices[0].message.content
        json_match = re.search(r'\{.*\}', conteudo, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return json.loads(conteudo)
        
    except Exception as e:
        st.error(f"Erro na IA: {str(e)}")
        return None

tabs = st.tabs(list(CATEGORIAS.keys()))

for tab, (cat, ajuda) in zip(tabs, CATEGORIAS.items()):
    with tab:
        st.markdown(f"**{cat}** — {ajuda}")

        if "pestel" not in data:
            data["pestel"] = {}
        
        if cat not in data["pestel"]:
            data["pestel"][cat] = []
        
        itens = data["pestel"].get(cat, [])
        
        for item in itens:
            if "tipo" not in item or item["tipo"] not in TIPOS:
                item["tipo"] = "Oportunidade"
            if "impacto" not in item or item["impacto"] not in IMPACTOS:
                item["impacto"] = "Médio"
            if "descricao" not in item:
                item["descricao"] = ""
        
        if itens:
            df = pd.DataFrame(itens)
        else:
            df = pd.DataFrame(columns=["descricao", "tipo", "impacto"])
        
        df_hash = hash(str(sorted([str(item) for item in itens]))) if itens else 0
        editor_key = f"editor_pestel_{cat}_{df_hash}"
        
        edited = st.data_editor(
            df, 
            num_rows="dynamic", 
            width="stretch", 
            key=editor_key,
            column_config={
                "descricao": st.column_config.TextColumn("Descrição do fator", width="large"),
                "tipo": st.column_config.SelectboxColumn(
                    "Tipo", 
                    options=TIPOS,
                    required=True,
                    default="Oportunidade"
                ),
                "impacto": st.column_config.SelectboxColumn(
                    "Impacto", 
                    options=IMPACTOS,
                    required=True,
                    default="Médio"
                ),
            },
            hide_index=True,
        )
        
        if edited is not None and not edited.empty:
            edited = edited.fillna("")
            
            for idx, row in edited.iterrows():
                descricao = row.get("descricao", "").strip()
                
                if pd.isna(row.get("tipo")) or row.get("tipo") == "":
                    edited.at[idx, "tipo"] = "Oportunidade"
                if pd.isna(row.get("impacto")) or row.get("impacto") == "":
                    edited.at[idx, "impacto"] = "Médio"
            
            novos_itens = []
            for _, row in edited.iterrows():
                descricao = row.get("descricao", "").strip()
                if descricao:
                    novos_itens.append({
                        "descricao": descricao,
                        "tipo": row.get("tipo", "Oportunidade"),
                        "impacto": row.get("impacto", "Médio")
                    })
            
            if novos_itens != data["pestel"].get(cat, []):
                data["pestel"][cat] = novos_itens
                st.rerun()
        else:
            if data["pestel"].get(cat, []):
                data["pestel"][cat] = []

        col_btn1, col_btn2 = st.columns([3, 1])
        with col_btn1:
            if st.button(f"🤖 Sugerir para {cat}", key=f"sugerir_pestel_{cat}", use_container_width=True):
                with st.spinner(f"Gerando análise para {cat}..."):
                    resultado = gerar_pestel_ia(cat)
                    if resultado and "itens" in resultado:
                        itens_existentes = data["pestel"].get(cat, [])
                        existentes_desc = {item["descricao"].lower().strip() for item in itens_existentes}
                        adicionados = 0
                        for item in resultado["itens"]:
                            if item.get("descricao") and item["descricao"].lower().strip() not in existentes_desc:
                                itens_existentes.append({
                                    "descricao": item.get("descricao", ""),
                                    "tipo": item.get("tipo", "Oportunidade"),
                                    "impacto": item.get("impacto", "Médio")
                                })
                                adicionados += 1
                        if adicionados > 0:
                            data["pestel"][cat] = itens_existentes
                            st.success(f"✅ {adicionados} itens adicionados para {cat}!")
                            st.rerun()
                        else:
                            st.info(f"ℹ️ Todos os itens sugeridos já existem em {cat}.")
        with col_btn2:
            if st.button(f"🗑️", key=f"limpar_pestel_{cat}", use_container_width=True):
                data["pestel"][cat] = []
                st.rerun()

st.divider()

st.subheader("🚀 Ações com IA")
col_gerar1, col_gerar2, col_gerar3 = st.columns([3, 1, 1])
with col_gerar1:
    st.caption("A IA vai gerar análise para todas as categorias PESTEL")
with col_gerar2:
    if st.button("🔄 Gerar PESTEL Completo", use_container_width=True):
        with st.spinner("Gerando análise PESTEL completa..."):
            resultado = gerar_pestel_ia()
            if resultado:
                total_adicionados = 0
                for cat in CATEGORIAS.keys():
                    if cat in resultado and resultado[cat]:
                        itens_existentes = data["pestel"].get(cat, [])
                        existentes_desc = {item["descricao"].lower().strip() for item in itens_existentes}
                        for item in resultado[cat]:
                            if item.get("descricao") and item["descricao"].lower().strip() not in existentes_desc:
                                itens_existentes.append({
                                    "descricao": item.get("descricao", ""),
                                    "tipo": item.get("tipo", "Oportunidade"),
                                    "impacto": item.get("impacto", "Médio")
                                })
                                total_adicionados += 1
                        data["pestel"][cat] = itens_existentes
                if total_adicionados > 0:
                    st.success(f"✅ {total_adicionados} itens adicionados à análise PESTEL!")
                    st.rerun()
                else:
                    st.info("ℹ️ Todos os itens sugeridos já existem.")
with col_gerar3:
    if st.button("🗑️ Limpar PESTEL", use_container_width=True):
        for cat in CATEGORIAS.keys():
            data["pestel"][cat] = []
        st.rerun()

st.divider()
st.info(
    "💡 Preencha também a página **⚔️ 5 Forças de Porter**. Depois, vá para "
    "**🎯 Análise SWOT** para consolidar tudo automaticamente."
)

st.divider()
st.subheader("💬 Assistente IA - Ajuda com a Análise PESTEL")

col_chat1, col_chat2 = st.columns([5, 1])
with col_chat2:
    if st.button("🗑️ Limpar Chat", use_container_width=True):
        st.session_state.messages_pestel = []
        st.rerun()

if "messages_pestel" not in st.session_state:
    st.session_state.messages_pestel = []

for msg in st.session_state.messages_pestel:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

st.divider()

pergunta = st.text_area(
    "",
    placeholder="Pergunte ao assistente sobre a análise PESTEL...",
    height=80,
    key="pergunta_pestel"
)

col1, col2 = st.columns([5,1])

with col2:
    enviar = st.button("🤖", width="stretch")

if enviar and pergunta.strip():
    st.session_state.messages_pestel.append({"role": "user", "content": pergunta})
    
    with st.chat_message("user"):
        st.markdown(pergunta)
    
    with st.spinner("🤔 Pensando..."):
        try:
            client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"], base_url="https://openrouter.ai/api/v1")
            
            pestel_atual = ""
            for cat, itens in data["pestel"].items():
                pestel_atual += f"\n{cat}:\n"
                if itens:
                    for item in itens:
                        pestel_atual += f"  • {item.get('descricao', '')} ({item.get('tipo', '')}, impacto {item.get('impacto', '')})\n"
                else:
                    pestel_atual += "  (vazio)\n"
            
            empresa_nome = data.get("empresa", {}).get("nome", "a empresa")
            empresa_setor = data.get("empresa", {}).get("setor", "não informado")
            
            mensagens = [
                {"role": "system", "content": f"""Você é um assistente especialista em Análise PESTEL e Estratégia.

EMPRESA: {empresa_nome}
SETOR: {empresa_setor}

ANÁLISE PESTEL ATUAL:
{pestel_atual}

Responda em português do Brasil, de forma prática e objetiva."""}
            ] + st.session_state.messages_pestel[:-1]
            
            response = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=mensagens,
                temperature=0.7
            )
            
            resposta = response.choices[0].message.content
            st.session_state.messages_pestel.append({"role": "assistant", "content": resposta})
            
            with st.chat_message("assistant"):
                st.markdown(resposta)
                
        except Exception as e:
            st.error(f"❌ Erro ao processar sua pergunta: {str(e)}")

st.divider()

# ========== BOTÃO PRÓXIMA ETAPA ==========
col_prox1, col_prox2, col_prox3 = st.columns([1, 2, 1])
with col_prox2:
    if st.button("➡️ Próxima Etapa > 5 Forças de Porter", width="stretch"):
        st.switch_page("pages/3_⚔️_5_Forças_de_Porter.py")
