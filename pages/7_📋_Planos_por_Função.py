import pandas as pd
import streamlit as st
import json
import re
from utils.data_manager import init_data, get_data, sidebar_data_controls
from openai import OpenAI

st.set_page_config(page_title="Planos Departamentais", page_icon="🏢", layout="wide")
init_data()
data = get_data()

st.sidebar.title("🧭 Gestor Estratégico")
sidebar_data_controls()

st.title("🏢 Planos Departamentais")
st.caption(
    "Gerencie os planos de ação, objetivos, indicadores e recursos de cada departamento. "
    "A IA pode sugerir planos completos baseados nas análises estratégicas."
)

# ========== DEFINIÇÃO DOS DEPARTAMENTOS ==========
DEPARTAMENTOS = [
    "Financeiro",
    "Comercial",
    "Marketing",
    "Operações",
    "Recursos Humanos",
    "Tecnologia",
    "Inovação",
    "Sustentabilidade",
    "Jurídico"
]

# ========== INICIALIZAR DADOS ==========
if "departamentos" not in data:
    data["departamentos"] = {}
    for depto in DEPARTAMENTOS:
        data["departamentos"][depto] = {
            "objetivos": [],
            "acoes": [],
            "indicadores": [],
            "recursos": [],
            "riscos": []
        }

# ========== FUNÇÃO DE RENDERIZAÇÃO ==========
def render_tabela(departamento, secao, colunas, titulo):
    """Renderiza uma tabela editável e salva diretamente em data"""
    st.markdown(f"**{titulo}**")
    
    dados = data["departamentos"][departamento][secao]
    
    if dados:
        df = pd.DataFrame(dados)
        for col in colunas:
            if col not in df.columns:
                df[col] = ""
        df = df[colunas]
    else:
        df = pd.DataFrame(columns=colunas)
    
    edited = st.data_editor(
        df,
        num_rows="dynamic",
        width="stretch",
        hide_index=True,
        key=f"{departamento}_{secao}",
        column_config={col: st.column_config.TextColumn(col, width="large") for col in colunas}
    )
    
    if edited is not None:
        edited = edited.fillna("")
        novos_dados = []
        for _, row in edited.iterrows():
            item = {}
            valido = False
            for col in colunas:
                valor = str(row.get(col, "")).strip()
                item[col] = valor
                if valor:
                    valido = True
            if valido:
                novos_dados.append(item)
        
        data["departamentos"][departamento][secao] = novos_dados

# ========== FUNÇÕES DE IA ==========
def gerar_plano_departamento_ia(departamento):
    """Gera plano completo para um departamento usando IA"""
    try:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"], base_url="https://openrouter.ai/api/v1")
        
        empresa_nome = data.get("empresa", {}).get("nome", "a empresa")
        empresa_setor = data.get("empresa", {}).get("setor", "não informado")
        
        swot_dados = ""
        if "swot" in data:
            for chave, itens in data["swot"].items():
                if itens:
                    nomes = {"forcas": "Forças", "fraquezas": "Fraquezas", 
                            "oportunidades": "Oportunidades", "ameacas": "Ameaças"}
                    swot_dados += f"\n{nomes.get(chave, chave)}:\n"
                    for item in itens[:3]:
                        swot_dados += f"  - {item.get('descricao', '')}\n"
        
        pestel_dados = ""
        if "pestel" in data:
            for cat, itens in data["pestel"].items():
                if itens:
                    pestel_dados += f"\n{cat}:\n"
                    for item in itens[:2]:
                        pestel_dados += f"  - {item.get('descricao', '')}\n"
        
        porter_dados = ""
        if "porter_analise" in data:
            for forca in data["porter_analise"].values():
                if forca.get("intensidade", 0) >= 4:
                    porter_dados += f"  - {forca.get('nome', '')}: Intensidade {forca.get('intensidade', 0)}/5\n"
        
        prompt = f"""
        Você é um consultor de planejamento estratégico especializado em planos departamentais.
        
        EMPRESA: {empresa_nome}
        SETOR: {empresa_setor}
        DEPARTAMENTO: {departamento}
        
        INFORMAÇÕES ESTRATÉGICAS DA EMPRESA:
        {swot_dados}
        {pestel_dados}
        {porter_dados}
        
        Com base nas informações acima, crie um plano completo para o departamento de {departamento}.
        
        FORMATO DE SAÍDA: Retorne APENAS um JSON com as seguintes chaves EXATAS:
        {{
            "objetivos": [
                {{"Objetivo": "texto", "Estratégia relacionada": "texto", "Prioridade": "Alta", 
                  "Responsável": "texto", "Prazo": "texto", "Status": "Não iniciado"}}
            ],
            "acoes": [
                {{"Ação": "texto", "Origem": "texto", "Responsável": "texto", 
                  "Data início": "texto", "Data fim": "texto", "Recursos necessários": "texto", 
                  "Custo estimado": "texto", "Indicador": "texto", "Meta": "texto", "Situação": "Não iniciado"}}
            ],
            "indicadores": [
                {{"Indicador": "texto", "Fórmula": "texto", "Meta": "texto", 
                  "Valor Atual": "texto", "Frequência": "texto", "Responsável": "texto"}}
            ],
            "recursos": [
                {{"Recurso": "texto", "Tipo": "texto", "Quantidade": "texto", 
                  "Valor estimado": "texto", "Observações": "texto"}}
            ],
            "riscos": [
                {{"Risco": "texto", "Probabilidade": "texto", "Impacto": "texto", 
                  "Plano de mitigação": "texto"}}
            ]
        }}
        
        Cada seção deve ter de 3 a 5 itens.
        Responda APENAS com o JSON.
        """
        
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": "Você é um consultor de planejamento estratégico. Responda em português do Brasil. Retorne APENAS JSON válido."},
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

# ========== TABS POR DEPARTAMENTO ==========
tabs = st.tabs(DEPARTAMENTOS)

for tab, depto in zip(tabs, DEPARTAMENTOS):
    with tab:
        st.subheader(f"📋 Plano - {depto}")
        
        col_ia1, col_ia2 = st.columns([3, 1])
        with col_ia1:
            st.caption(f"🤖 A IA vai gerar um plano completo para o departamento de {depto} baseado nas análises estratégicas")
        with col_ia2:
            if st.button(f"🤖 Sugerir Plano", key=f"ia_{depto}", width="stretch"):
                with st.spinner(f"Gerando plano para {depto}..."):
                    resultado = gerar_plano_departamento_ia(depto)
                    if resultado:
                        if "objetivos" in resultado:
                            data["departamentos"][depto]["objetivos"] = resultado["objetivos"]
                        if "acoes" in resultado:
                            data["departamentos"][depto]["acoes"] = resultado["acoes"]
                        if "indicadores" in resultado:
                            data["departamentos"][depto]["indicadores"] = resultado["indicadores"]
                        if "recursos" in resultado:
                            data["departamentos"][depto]["recursos"] = resultado["recursos"]
                        if "riscos" in resultado:
                            data["departamentos"][depto]["riscos"] = resultado["riscos"]
                        st.success(f"✅ Plano gerado para {depto}!")
                        st.rerun()
        
        st.divider()
        
        with st.expander("🎯 Objetivos", expanded=True):
            render_tabela(
                depto,
                "objetivos",
                ["Objetivo", "Estratégia relacionada", "Prioridade", "Responsável", "Prazo", "Status"],
                "Objetivos do departamento"
            )
        
        with st.expander("📋 Plano de Ações", expanded=True):
            render_tabela(
                depto,
                "acoes",
                ["Ação", "Origem", "Responsável", "Data início", "Data fim", 
                 "Recursos necessários", "Custo estimado", "Indicador", "Meta", "Situação"],
                "Plano de ações do departamento"
            )
        
        with st.expander("📊 Indicadores"):
            render_tabela(
                depto,
                "indicadores",
                ["Indicador", "Fórmula", "Meta", "Valor Atual", "Frequência", "Responsável"],
                "Indicadores do departamento"
            )
        
        with st.expander("💰 Recursos Necessários"):
            render_tabela(
                depto,
                "recursos",
                ["Recurso", "Tipo", "Quantidade", "Valor estimado", "Observações"],
                "Recursos necessários"
            )
        
        with st.expander("⚠️ Riscos"):
            render_tabela(
                depto,
                "riscos",
                ["Risco", "Probabilidade", "Impacto", "Plano de mitigação"],
                "Riscos do departamento"
            )

# ========== BOTÃO PRÓXIMA ETAPA ==========
col_prox1, col_prox2, col_prox3 = st.columns([1, 2, 1])
with col_prox2:
    if st.button("➡️ Próxima Etapa > Orçamento", width="stretch"):
        st.switch_page("pages/8_💰_Orçamento.py")

# ========== ASSISTENTE IA ==========
st.divider()
st.subheader("💬 Assistente IA - Ajuda com Planos Departamentais")

col_chat1, col_chat2 = st.columns([5, 1])
with col_chat2:
    if st.button("🗑️ Limpar Chat", width="stretch"):
        st.session_state.messages_departamentos = []
        st.rerun()

if "messages_departamentos" not in st.session_state:
    st.session_state.messages_departamentos = []

for msg in st.session_state.messages_departamentos:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if pergunta := st.chat_input("Pergunte ao assistente sobre os planos departamentais..."):
    st.session_state.messages_departamentos.append({"role": "user", "content": pergunta})
    
    with st.chat_message("user"):
        st.markdown(pergunta)
    
    with st.spinner("🤔 Pensando..."):
        try:
            client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"], base_url="https://openrouter.ai/api/v1")
            
            contexto = "PLANOS DEPARTAMENTAIS:\n\n"
            for depto in DEPARTAMENTOS:
                dados = data["departamentos"][depto]
                contexto += f"{depto}:\n"
                if dados["objetivos"]:
                    contexto += f"  Objetivos: {len(dados['objetivos'])}\n"
                if dados["acoes"]:
                    contexto += f"  Ações: {len(dados['acoes'])}\n"
                if dados["indicadores"]:
                    contexto += f"  Indicadores: {len(dados['indicadores'])}\n"
            
            empresa_nome = data.get("empresa", {}).get("nome", "a empresa")
            empresa_setor = data.get("empresa", {}).get("setor", "não informado")
            
            mensagens = [
                {"role": "system", "content": f"""Você é um assistente especialista em Planejamento Estratégico Departamental.

EMPRESA: {empresa_nome}
SETOR: {empresa_setor}

{contexto}

Responda em português do Brasil, de forma prática e objetiva."""}
            ] + st.session_state.messages_departamentos[:-1]
            
            response = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=mensagens,
                temperature=0.7
            )
            
            resposta = response.choices[0].message.content
            st.session_state.messages_departamentos.append({"role": "assistant", "content": resposta})
            
            with st.chat_message("assistant"):
                st.markdown(resposta)
                
        except Exception as e:
            st.error(f"❌ Erro ao processar sua pergunta: {str(e)}")
