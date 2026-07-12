import pandas as pd
import streamlit as st
import json
import re
from utils.data_manager import init_data, get_data, sidebar_data_controls
from openai import OpenAI

st.set_page_config(page_title="Análise SWOT", page_icon="🎯", layout="wide")
init_data()
data = get_data()

st.sidebar.title("🧭 Gestor Estratégico")
sidebar_data_controls()

st.title("🎯 Análise SWOT")
st.caption(
    "Forças e Fraquezas são fatores internos (você controla). Oportunidades e Ameaças são "
    "fatores externos — aqui você pode importar automaticamente o que já foi identificado na "
    "Análise PESTEL e nas 5 Forças de Porter."
)

def itens_pestel_por_tipo(tipo):
    resultado = []
    if "pestel" in data:
        for cat, itens in data["pestel"].items():
            for item in itens:
                if item.get("tipo") == tipo and item.get("descricao"):
                    resultado.append(f"[PESTEL-{cat}] {item['descricao']}")
    return resultado

def itens_porter_alerta():
    alertas = []
    if "porter_analise" in data:
        for forca in data["porter_analise"].values():
            if forca.get("intensidade", 0) >= 4:
                nota = f" — {forca['notas']}" if forca.get("notas") else ""
                alertas.append(f"[Porter] {forca.get('nome', 'Força')} está com intensidade alta{nota}")
    return alertas

col_import1, col_import2 = st.columns(2)
with col_import1:
    if st.button("⬇️ Importar Oportunidades da Análise PESTEL", width="stretch"):
        novas = itens_pestel_por_tipo("Oportunidade")
        existentes = {i["descricao"] for i in data["swot"]["oportunidades"]}
        for texto in novas:
            if texto not in existentes:
                data["swot"]["oportunidades"].append({"descricao": texto})
        st.success(f"{len(novas)} itens verificados/importados.")
        st.rerun()
with col_import2:
    if st.button("⬇️ Importar Ameaças do PESTEL + Porter", width="stretch"):
        novas = itens_pestel_por_tipo("Ameaça") + itens_porter_alerta()
        existentes = {i["descricao"] for i in data["swot"]["ameacas"]}
        for texto in novas:
            if texto not in existentes:
                data["swot"]["ameacas"].append({"descricao": texto})
        st.success(f"{len(novas)} itens verificados/importados.")
        st.rerun()

st.divider()

QUADRANTES = [
    ("forcas", "💪 Forças (interno)", "Vantagens internas: o que a empresa faz bem, recursos únicos, diferenciais."),
    ("fraquezas", "⚠️ Fraquezas (interno)", "Pontos internos a melhorar: limitações de recursos, processos, equipe."),
    ("oportunidades", "🌱 Oportunidades (externo)", "Fatores externos favoráveis que a empresa pode aproveitar."),
    ("ameacas", "🌩️ Ameaças (externo)", "Fatores externos desfavoráveis que podem prejudicar a empresa."),
]

def gerar_analise_swot(quadrante=None):
    """Gera análise SWOT com IA para um quadrante específico ou todos"""
    try:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"], base_url="https://openrouter.ai/api/v1")
        
        empresa_nome = data.get("empresa", {}).get("nome", "a empresa")
        empresa_setor = data.get("empresa", {}).get("setor", "não informado")
        
        if quadrante:
            chave, titulo, ajuda = next(q for q in QUADRANTES if q[0] == quadrante)
            prompt = f"""
            Você é um consultor de estratégia especialista em análise SWOT.
            
            INFORMAÇÕES DA EMPRESA:
            - Nome: {empresa_nome}
            - Setor: {empresa_setor}
            
            Quadrante SWOT: {titulo}
            Descrição: {ajuda}
            
            Gere uma lista de 3 a 5 itens em português do Brasil para este quadrante.
            Responda APENAS com um JSON: {{"itens": ["item1", "item2", "item3"]}}
            """
        else:
            prompt = f"""
            Você é um consultor de estratégia especialista em análise SWOT.
            
            INFORMAÇÕES DA EMPRESA:
            - Nome: {empresa_nome}
            - Setor: {empresa_setor}
            
            Gere uma análise SWOT completa com os 4 quadrantes em português do Brasil.
            
            FORMATO DE SAÍDA: Retorne APENAS um JSON com:
            {{
                "forcas": ["item1", "item2", "item3"],
                "fraquezas": ["item1", "item2", "item3"],
                "oportunidades": ["item1", "item2", "item3"],
                "ameacas": ["item1", "item2", "item3"]
            }}
            """
        
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": "Você é um consultor especialista em análise SWOT. Responda em português do Brasil. Retorne APENAS JSON válido."},
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

st.subheader("🚀 Ações com IA")

col_gerar1, col_gerar2, col_gerar3 = st.columns([3, 1, 1])
with col_gerar1:
    st.caption("A IA vai gerar sugestões para todos os 4 quadrantes da SWOT")
with col_gerar2:
    if st.button("🔄 Gerar SWOT Completa", use_container_width=True):
        with st.spinner("Gerando análise SWOT completa..."):
            resultado = gerar_analise_swot()
            if resultado:
                for chave, _, _ in QUADRANTES:
                    if chave in resultado and resultado[chave]:
                        itens_existentes = data["swot"].get(chave, [])
                        existentes_desc = {item["descricao"].lower().strip() for item in itens_existentes}
                        for item in resultado[chave]:
                            if item and item.lower().strip() not in existentes_desc:
                                itens_existentes.append({"descricao": item})
                        data["swot"][chave] = itens_existentes
                st.success("✅ SWOT completa gerada!")
                st.rerun()
with col_gerar3:
    if st.button("🗑️ Limpar SWOT", use_container_width=True):
        for chave, _, _ in QUADRANTES:
            data["swot"][chave] = []
        st.rerun()

st.divider()

col_a, col_b = st.columns(2)
cols_map = {0: col_a, 1: col_b, 2: col_a, 3: col_b}

for i, (chave, titulo, ajuda) in enumerate(QUADRANTES):
    with cols_map[i]:
        st.markdown(f"#### {titulo}")
        st.caption(ajuda)
        
        if "swot" not in data:
            data["swot"] = {}
        if chave not in data["swot"]:
            data["swot"][chave] = []
        
        itens = data["swot"].get(chave, [])
        
        for item in itens:
            if "descricao" not in item:
                item["descricao"] = ""
        
        if itens:
            df = pd.DataFrame(itens)
        else:
            df = pd.DataFrame(columns=["descricao"])
        
        df_hash = hash(str(sorted([item.get("descricao", "") for item in itens]))) if itens else 0
        editor_key = f"editor_swot_{chave}_{df_hash}"
        
        edited = st.data_editor(
            df, 
            num_rows="dynamic", 
            width="stretch",
            key=editor_key, 
            hide_index=True,
            column_config={"descricao": st.column_config.TextColumn("Item", width="large")},
        )
        
        if edited is not None:
            edited = edited.fillna("")
            novos_itens = []
            for _, row in edited.iterrows():
                descricao = row.get("descricao", "").strip()
                if descricao:
                    novos_itens.append({"descricao": descricao})
            
            if novos_itens != data["swot"][chave]:
                data["swot"][chave] = novos_itens
                st.rerun()
        
        col_btn1, col_btn2 = st.columns([3, 1])
        with col_btn1:
            if st.button(f"🤖 Sugerir {titulo.split(' ')[0]}", key=f"sugerir_{chave}", use_container_width=True):
                with st.spinner(f"Gerando sugestões para {titulo}..."):
                    resultado = gerar_analise_swot(chave)
                    if resultado and "itens" in resultado:
                        itens_existentes = data["swot"].get(chave, [])
                        existentes_desc = {item["descricao"].lower().strip() for item in itens_existentes}
                        adicionados = 0
                        for item in resultado["itens"]:
                            if item and item.lower().strip() not in existentes_desc:
                                itens_existentes.append({"descricao": item})
                                adicionados += 1
                        if adicionados > 0:
                            data["swot"][chave] = itens_existentes
                            st.success(f"✅ {adicionados} itens adicionados para {titulo}!")
                            st.rerun()
                        else:
                            st.info(f"ℹ️ Todos os itens sugeridos já existem em {titulo}.")
        
        with col_btn2:
            if st.button(f"🗑️", key=f"limpar_{chave}", use_container_width=True):
                data["swot"][chave] = []
                st.rerun()

st.divider()
st.info(
    "💡 Depois de concluir a SWOT, vá para **🧭 Planejamento Estratégico** para construir "
    "a **SWOT Cruzada** (cruzamento de Forças/Fraquezas com Oportunidades/Ameaças)."
)

st.divider()
st.subheader("💬 Assistente IA - Ajuda com a Análise SWOT")

col_chat1, col_chat2 = st.columns([5, 1])
with col_chat2:
    if st.button("🗑️ Limpar Chat", use_container_width=True):
        st.session_state.messages_swot = []
        st.rerun()

if "messages_swot" not in st.session_state:
    st.session_state.messages_swot = []

for msg in st.session_state.messages_swot:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if pergunta := st.chat_input("Pergunte ao assistente sobre sua análise SWOT..."):
    st.session_state.messages_swot.append({"role": "user", "content": pergunta})
    
    with st.chat_message("user"):
        st.markdown(pergunta)
    
    with st.spinner("🤔 Pensando..."):
        try:
            client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"], base_url="https://openrouter.ai/api/v1")
            
            swot_atual = ""
            for chave, titulo, _ in QUADRANTES:
                itens = data["swot"].get(chave, [])
                swot_atual += f"\n{titulo}:\n"
                if itens:
                    for item in itens:
                        swot_atual += f"  • {item.get('descricao', '')}\n"
                else:
                    swot_atual += "  (vazio)\n"
            
            empresa_nome = data.get("empresa", {}).get("nome", "a empresa")
            empresa_setor = data.get("empresa", {}).get("setor", "não informado")
            
            mensagens = [
                {"role": "system", "content": f"""Você é um assistente especialista em Análise SWOT e Estratégia.

EMPRESA: {empresa_nome}
SETOR: {empresa_setor}

ANÁLISE SWOT ATUAL:
{swot_atual}

Responda em português do Brasil, de forma prática e objetiva."""}
            ] + st.session_state.messages_swot[:-1]
            
            response = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=mensagens,
                temperature=0.7
            )
            
            resposta = response.choices[0].message.content
            st.session_state.messages_swot.append({"role": "assistant", "content": resposta})
            
            with st.chat_message("assistant"):
                st.markdown(resposta)
                
        except Exception as e:
            st.error(f"❌ Erro ao processar sua pergunta: {str(e)}")
