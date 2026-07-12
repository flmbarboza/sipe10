import pandas as pd
import streamlit as st
import json
import re
from utils.data_manager import init_data, get_data, sidebar_data_controls
from openai import OpenAI

st.set_page_config(page_title="5 Forças de Porter", page_icon="⚔️", layout="wide")
init_data()
data = get_data()

st.sidebar.title("🧭 Gestor Estratégico")
sidebar_data_controls()

st.title("⚔️ 5 Forças de Porter")
st.caption(
    "Avalie a intensidade de cada força competitiva do setor (1 = muito baixa, 5 = muito alta) "
    "e registre suas observações. Isso ajuda a construir a Análise SWOT."
)

FORCAS = [
    {"id": "rivalidade", "nome": "Rivalidade entre concorrentes", 
     "ajuda": "Número e força dos concorrentes diretos, guerra de preços, diferenciação."},
    {"id": "clientes", "nome": "Poder de barganha dos clientes", 
     "ajuda": "Concentração de clientes, sensibilidade a preço, custo de troca."},
    {"id": "fornecedores", "nome": "Poder de barganha dos fornecedores", 
     "ajuda": "Concentração de fornecedores, insumos críticos, custo de troca."},
    {"id": "entrantes", "nome": "Ameaça de novos entrantes", 
     "ajuda": "Barreiras de entrada, capital necessário, regulação, economia de escala."},
    {"id": "substitutos", "nome": "Ameaça de produtos substitutos", 
     "ajuda": "Alternativas que atendem à mesma necessidade do cliente."},
]

if "porter_analise" not in data:
    data["porter_analise"] = {}
    for forca in FORCAS:
        data["porter_analise"][forca["id"]] = {
            "intensidade": 3,
            "notas": "",
            "nome": forca["nome"]
        }

empresa_nome = data.get("empresa", {}).get("nome", "a empresa")
empresa_setor = data.get("empresa", {}).get("setor", "não informado")
empresa_cidade = data.get("empresa", {}).get("cidade_estado", "")

def gerar_analise_ia(forca_id=None):
    try:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"], base_url="https://openrouter.ai/api/v1")
        
        if forca_id:
            forca = next(f for f in FORCAS if f["id"] == forca_id)
            prompt = f"""
            INFORMAÇÕES DA EMPRESA:
            - Nome: {empresa_nome}
            - Setor: {empresa_setor}
            - Localização: {empresa_cidade or "Não informado"}
            
            Força de Porter: {forca['nome']}
            Descrição: {forca['ajuda']}
            
            Gere uma análise objetiva para esta força.
            Responda APENAS com um JSON: {{"intensidade": 3, "notas": "análise detalhada"}}
            """
        else:
            prompt = f"""
            INFORMAÇÕES DA EMPRESA:
            - Nome: {empresa_nome}
            - Setor: {empresa_setor}
            - Localização: {empresa_cidade or "Não informado"}
            
            Analise as 5 Forças de Porter para este setor.
            
            FORMATO DE SAÍDA: Retorne APENAS um JSON com:
            {{
                "rivalidade": {{"intensidade": 3, "notas": "análise"}},
                "clientes": {{"intensidade": 3, "notas": "análise"}},
                "fornecedores": {{"intensidade": 3, "notas": "análise"}},
                "entrantes": {{"intensidade": 3, "notas": "análise"}},
                "substitutos": {{"intensidade": 3, "notas": "análise"}}
            }}
            """
        
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": "Você é um consultor especialista em Porter. Responda APENAS com JSON válido."},
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
    st.caption("A IA vai analisar seu setor e gerar análise para todas as 5 forças")
with col_gerar2:
    if st.button("🔄 Gerar Análise Completa", use_container_width=True):
        with st.spinner("Gerando análise completa..."):
            resultado = gerar_analise_ia()
            if resultado:
                for forca in FORCAS:
                    if forca["id"] in resultado:
                        data["porter_analise"][forca["id"]]["intensidade"] = resultado[forca["id"]]["intensidade"]
                        data["porter_analise"][forca["id"]]["notas"] = resultado[forca["id"]]["notas"]
                st.success("✅ Análise completa gerada!")
                st.rerun()
with col_gerar3:
    if st.button("🗑️ Limpar Análise", use_container_width=True):
        for forca in FORCAS:
            data["porter_analise"][forca["id"]]["intensidade"] = 3
            data["porter_analise"][forca["id"]]["notas"] = ""
        st.rerun()

st.divider()

for forca in FORCAS:
    st.markdown(f"### {forca['nome']}")
    st.caption(forca['ajuda'])
    
    with st.container():
        col1, col2, col3 = st.columns([1, 3, 1])
        
        with col1:
            intensidade = st.slider(
                "Intensidade",
                min_value=1,
                max_value=5,
                value=data["porter_analise"][forca["id"]]["intensidade"],
                key=f"slider_{forca['id']}"
            )
            if data["porter_analise"][forca["id"]]["intensidade"] != intensidade:
                data["porter_analise"][forca["id"]]["intensidade"] = intensidade
            
            labels = {1: "Muito Baixa", 2: "Baixa", 3: "Média", 4: "Alta", 5: "Muito Alta"}
            st.caption(f"**{labels.get(intensidade, 'Média')}**")
        
        with col2:
            notas = st.text_area(
                "Observações",
                value=data["porter_analise"][forca["id"]]["notas"],
                key=f"text_{forca['id']}",
                height=100
            )
            if data["porter_analise"][forca["id"]]["notas"] != notas:
                data["porter_analise"][forca["id"]]["notas"] = notas
        
        with col3:
            st.write("")
            st.write("")
            
            if st.button(f"🤖 IA", key=f"ia_{forca['id']}", use_container_width=True):
                with st.spinner(f"Gerando análise para {forca['nome']}..."):
                    resultado = gerar_analise_ia(forca["id"])
                    if resultado:
                        data["porter_analise"][forca["id"]]["intensidade"] = resultado.get("intensidade", 3)
                        data["porter_analise"][forca["id"]]["notas"] = resultado.get("notas", "")
                        st.success(f"✅ Análise atualizada para {forca['nome']}!")
                        st.rerun()
            
            if st.button(f"🗑️", key=f"limpar_{forca['id']}", use_container_width=True):
                data["porter_analise"][forca["id"]]["intensidade"] = 3
                data["porter_analise"][forca["id"]]["notas"] = ""
                st.rerun()
    
    st.markdown("---")

st.subheader("📊 Resumo visual")

df_resumo = pd.DataFrame([
    {"Força": forca["nome"], "Intensidade": data["porter_analise"][forca["id"]]["intensidade"]}
    for forca in FORCAS
]).set_index("Força")
st.bar_chart(df_resumo)

media = df_resumo["Intensidade"].mean() if not df_resumo.empty else 0
st.metric("Intensidade competitiva média do setor", f"{media:.1f} / 5")

st.divider()
col_export1, col_export2 = st.columns(2)
with col_export1:
    if st.button("📋 Ver Análise Completa", use_container_width=True):
        texto = "ANÁLISE DAS 5 FORÇAS DE PORTER\n" + "="*50 + "\n\n"
        for forca in FORCAS:
            dados = data["porter_analise"][forca["id"]]
            texto += f"{forca['nome']}:\n"
            texto += f"  Intensidade: {dados['intensidade']}/5\n"
            texto += f"  Observações: {dados['notas'] or '(vazio)'}\n\n"
        st.code(texto, language="markdown")

st.divider()
st.subheader("💬 Assistente IA - Ajuda com as 5 Forças de Porter")

col_chat1, col_chat2 = st.columns([5, 1])
with col_chat2:
    if st.button("🗑️ Limpar Chat", use_container_width=True):
        st.session_state.messages_porter = []
        st.rerun()

if "messages_porter" not in st.session_state:
    st.session_state.messages_porter = []

for msg in st.session_state.messages_porter:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if pergunta := st.chat_input("Pergunte ao assistente sobre as 5 Forças de Porter..."):
    st.session_state.messages_porter.append({"role": "user", "content": pergunta})
    
    with st.chat_message("user"):
        st.markdown(pergunta)
    
    with st.spinner("🤔 Pensando..."):
        try:
            client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"], base_url="https://openrouter.ai/api/v1")
            
            porter_atual = ""
            for forca in FORCAS:
                dados = data["porter_analise"][forca["id"]]
                porter_atual += f"\n{forca['nome']}:\n"
                porter_atual += f"  Intensidade: {dados['intensidade']}/5\n"
                porter_atual += f"  Observações: {dados['notas'] or '(vazio)'}\n"
            
            mensagens = [
                {"role": "system", "content": f"""Você é um assistente especialista em Estratégia e 5 Forças de Porter.

EMPRESA: {empresa_nome}
SETOR: {empresa_setor}
LOCALIZAÇÃO: {empresa_cidade or 'Não informado'}

ANÁLISE ATUAL:
{porter_atual}

Responda em português do Brasil, de forma prática e objetiva."""}
            ] + st.session_state.messages_porter[:-1]
            
            response = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=mensagens,
                temperature=0.7
            )
            
            resposta = response.choices[0].message.content
            st.session_state.messages_porter.append({"role": "assistant", "content": resposta})
            
            with st.chat_message("assistant"):
                st.markdown(resposta)
                
        except Exception as e:
            st.error(f"❌ Erro ao processar sua pergunta: {str(e)}")
