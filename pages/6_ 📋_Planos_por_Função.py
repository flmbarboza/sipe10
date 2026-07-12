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

# ========== FUNÇÕES DE IA ==========
def gerar_plano_departamento_ia(departamento):
    """Gera plano completo para um departamento usando IA"""
    try:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"], base_url="https://openrouter.ai/api/v1")
        
        empresa_nome = data.get("empresa", {}).get("nome", "a empresa")
        empresa_setor = data.get("empresa", {}).get("setor", "não informado")
        
        # Coletar dados estratégicos
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
        
        FORMATO DE SAÍDA: Retorne APENAS um JSON com:
        {{
            "objetivos": [
                {{"objetivo": "texto", "estrategia": "texto", "prioridade": "Alta/Média/Baixa", 
                  "responsavel": "texto", "prazo": "texto", "status": "Não iniciado"}}
            ],
            "acoes": [
                {{"acao": "texto", "origem": "texto", "responsavel": "texto", 
                  "data_inicio": "texto", "data_fim": "texto", "recursos": "texto", 
                  "custo": "texto", "indicador": "texto", "meta": "texto", "situacao": "Não iniciado"}}
            ],
            "indicadores": [
                {{"indicador": "texto", "formula": "texto", "meta": "texto", 
                  "valor_atual": "texto", "frequencia": "texto", "responsavel": "texto"}}
            ],
            "recursos": [
                {{"recurso": "texto", "tipo": "texto", "quantidade": "texto", 
                  "valor_estimado": "texto", "observacoes": "texto"}}
            ],
            "riscos": [
                {{"risco": "texto", "probabilidade": "texto", "impacto": "texto", 
                  "plano_mitigacao": "texto"}}
            ]
        }}
        
        Cada seção deve ter de 3 a 5 itens. Responda APENAS com o JSON.
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

# ========== FUNÇÕES DE RENDERIZAÇÃO ==========
def render_tabela(dados, colunas, titulo, chave, depto):
    """Renderiza uma tabela editável genérica"""
    st.markdown(f"**{titulo}**")
    
    if dados:
        df = pd.DataFrame(dados)
        # Garantir que todas as colunas existam
        for col in colunas:
            if col not in df.columns:
                df[col] = ""
    else:
        df = pd.DataFrame(columns=colunas)
    
    df_hash = hash(str(df.to_dict())) if not df.empty else 0
    editor_key = f"{depto}_{chave}_{df_hash}"
    
    edited = st.data_editor(
        df,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        key=editor_key,
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
                if valor and not valido:
                    valido = True
            if valido:
                novos_dados.append(item)
        
        if novos_dados != dados:
            return novos_dados
    return dados

# ========== TABS POR DEPARTAMENTO ==========
tabs = st.tabs(DEPARTAMENTOS)

for tab, depto in zip(tabs, DEPARTAMENTOS):
    with tab:
        st.subheader(f"📋 Plano - {depto}")
        
        # Botão IA
        col_ia1, col_ia2 = st.columns([3, 1])
        with col_ia1:
            st.caption(f"🤖 A IA vai gerar um plano completo para o departamento de {depto} baseado nas análises estratégicas")
        with col_ia2:
            if st.button(f"🤖 Sugerir Plano", key=f"ia_{depto}", use_container_width=True):
                with st.spinner(f"Gerando plano para {depto}..."):
                    resultado = gerar_plano_departamento_ia(depto)
                    if resultado:
                        for secao in ["objetivos", "acoes", "indicadores", "recursos", "riscos"]:
                            if secao in resultado and resultado[secao]:
                                data["departamentos"][depto][secao] = resultado[secao]
                        st.success(f"✅ Plano gerado para {depto}!")
                        st.rerun()
        
        st.divider()
        
        # Objetivos
        with st.expander("🎯 Objetivos", expanded=True):
            colunas_obj = ["Objetivo", "Estratégia relacionada", "Prioridade", "Responsável", "Prazo", "Status"]
            novos = render_tabela(
                data["departamentos"][depto]["objetivos"],
                colunas_obj,
                "Objetivos do departamento",
                "objetivos",
                depto
            )
            if novos != data["departamentos"][depto]["objetivos"]:
                data["departamentos"][depto]["objetivos"] = novos
        
        # Plano de Ações
        with st.expander("📋 Plano de Ações", expanded=True):
            colunas_acoes = ["Ação", "Origem", "Responsável", "Data início", "Data fim", 
                           "Recursos necessários", "Custo estimado", "Indicador", "Meta", "Situação"]
            novos = render_tabela(
                data["departamentos"][depto]["acoes"],
                colunas_acoes,
                "Plano de ações do departamento",
                "acoes",
                depto
            )
            if novos != data["departamentos"][depto]["acoes"]:
                data["departamentos"][depto]["acoes"] = novos
        
        # Indicadores
        with st.expander("📊 Indicadores"):
            colunas_ind = ["Indicador", "Fórmula", "Meta", "Valor Atual", "Frequência", "Responsável"]
            novos = render_tabela(
                data["departamentos"][depto]["indicadores"],
                colunas_ind,
                "Indicadores do departamento",
                "indicadores",
                depto
            )
            if novos != data["departamentos"][depto]["indicadores"]:
                data["departamentos"][depto]["indicadores"] = novos
        
        # Recursos
        with st.expander("💰 Recursos Necessários"):
            colunas_rec = ["Recurso", "Tipo", "Quantidade", "Valor estimado", "Observações"]
            novos = render_tabela(
                data["departamentos"][depto]["recursos"],
                colunas_rec,
                "Recursos necessários",
                "recursos",
                depto
            )
            if novos != data["departamentos"][depto]["recursos"]:
                data["departamentos"][depto]["recursos"] = novos
        
        # Riscos
        with st.expander("⚠️ Riscos"):
            colunas_riscos = ["Risco", "Probabilidade", "Impacto", "Plano de mitigação"]
            novos = render_tabela(
                data["departamentos"][depto]["riscos"],
                colunas_riscos,
                "Riscos do departamento",
                "riscos",
                depto
            )
            if novos != data["departamentos"][depto]["riscos"]:
                data["departamentos"][depto]["riscos"] = novos

# ========== ASSISTENTE IA ==========
st.divider()
st.subheader("💬 Assistente IA - Ajuda com Planos Departamentais")

col_chat1, col_chat2 = st.columns([5, 1])
with col_chat2:
    if st.button("🗑️ Limpar Chat", use_container_width=True):
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
