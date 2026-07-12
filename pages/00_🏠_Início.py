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
    "📋 Business Model Canvas",
    "🌍 Análise PESTEL",
    "⚔️ 5 Forças de Porter",
    "🎯 Análise SWOT",
    "🧭 Planejamento Estratégico",
    "✅ Plano de Ação (5W2H)",
    "📋 Planos por Função",
    "💰 Orçamento",
    "🛃 Monitoramento",
    "🔄 Revisão Estratégica",
    "📈 Painel de Controle",
    "📄 Relatório Completo",
]

cols = st.columns(2)
for i, etapa in enumerate(etapas):
    with cols[i % 2]:
        st.markdown(f"**{etapa}**")

st.divider()

st.subheader("📊 Resumo do Planejamento")

# Calcular progresso
total_secoes = 11
preenchidas = 0

if data.get("empresa", {}).get("nome"):
    preenchidas += 1
if data.get("bmc") and any(data["bmc"].values()):
    preenchidas += 1
if data.get("pestel") and any([any([i.get("descricao") for i in itens]) for itens in data["pestel"].values()]):
    preenchidas += 1
if data.get("porter_analise") and any([v.get("notas") for v in data["porter_analise"].values()]):
    preenchidas += 1
if data.get("swot") and any([any([i.get("descricao") for i in itens]) for itens in data["swot"].values()]):
    preenchidas += 1
if data.get("mvv") and (data["mvv"].get("missao") or data["mvv"].get("visao")):
    preenchidas += 1
if data.get("objetivos") and any([o.get("objetivo") for o in data["objetivos"]]):
    preenchidas += 1
if data.get("acao_5w2h") and any([a.get("what") for a in data["acao_5w2h"]]):
    preenchidas += 1
if data.get("departamentos") and any([any([v for v in depto.values() if v]) for depto in data["departamentos"].values()]):
    preenchidas += 1
if data.get("orcamento") and (data["orcamento"].get("receitas") or data["orcamento"].get("investimentos")):
    preenchidas += 1
if data.get("monitoramento") and data["monitoramento"].get("alertas"):
    preenchidas += 1

progresso = (preenchidas / total_secoes) * 100

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Progresso Total", f"{progresso:.0f}%")
with col2:
    st.metric("Seções Preenchidas", f"{preenchidas}/{total_secoes}")
with col3:
    total_acoes = len([a for a in data.get("acao_5w2h", []) if a.get("what")])
    st.metric("Ações Totais", total_acoes)
with col4:
    deptos = len(data.get("departamentos", {}))
    st.metric("Departamentos", deptos)

# Barra de progresso
st.progress(progresso / 100, text=f"Progresso do planejamento: {progresso:.0f}%")

st.info(
    "💡 Use o botão **'⬇️ Baixar dados (.json)'** na barra lateral sempre que quiser "
    "salvar seu progresso, e **'⬆️ Carregar dados (.json)'** para retomar depois.",
    icon="💡",
)

st.divider()

# ========== BOTÃO PRÓXIMA ETAPA ==========
paginas = [
    "1_📋_Business_Model_Canvas",
    "2_🌍_Análise_PESTEL",
    "3_⚔️_5_Forças_de_Porter",
    "4_🎯_Análise_SWOT",
    "5_🧭_Planejamento_Estratégico",
    "6_✅_Plano_de_Ação_5W2H",
    "7_📋_Planos_por_Função",
    "8_💰_Orçamento",
    "9_🛃_Monitoramento",
    "10_🔄_Revisão",
    "11_📈_Painel_de_Controle",
    "12_📄_Relatório_Completo",
]

proxima_pagina = None
for i, pagina in enumerate(paginas):
    if i == 0 and not any(data.get("bmc", {}).values()):
        proxima_pagina = pagina
        break
    elif i == 1 and not any([any([i.get("descricao") for i in itens]) for itens in data.get("pestel", {}).values()]):
        proxima_pagina = pagina
        break
    elif i == 2 and not any([v.get("notas") for v in data.get("porter_analise", {}).values()]):
        proxima_pagina = pagina
        break
    elif i == 3 and not any([any([i.get("descricao") for i in itens]) for itens in data.get("swot", {}).values()]):
        proxima_pagina = pagina
        break
    elif i == 4 and not any([o.get("objetivo") for o in data.get("objetivos", [])]):
        proxima_pagina = pagina
        break
    elif i == 5 and not any([a.get("what") for a in data.get("acao_5w2h", [])]):
        proxima_pagina = pagina
        break
    elif i == 6 and not any([any([v for v in depto.values() if v]) for depto in data.get("departamentos", {}).values()]):
        proxima_pagina = pagina
        break
    elif i == 7 and not (data.get("orcamento", {}).get("receitas") or data.get("orcamento", {}).get("investimentos")):
        proxima_pagina = pagina
        break
    elif i == 8 and not data.get("monitoramento", {}).get("alertas"):
        proxima_pagina = pagina
        break
    elif i == 9:
        proxima_pagina = pagina
        break

if proxima_pagina:
    col_prox1, col_prox2, col_prox3 = st.columns([1, 2, 1])
    with col_prox2:
        if st.button("➡️ Próxima Etapa", use_container_width=True):
            st.switch_page(f"pages/{proxima_pagina}.py")

st.divider()

# ========== ASSISTENTE IA PARA AJUDA ==========
st.subheader("💬 Assistente IA - Ajuda com o Planejamento")

col_chat1, col_chat2 = st.columns([5, 1])
with col_chat2:
    if st.button("🗑️ Limpar Chat", use_container_width=True):
        st.session_state.messages_home = []
        st.rerun()

if "messages_home" not in st.session_state:
    st.session_state.messages_home = []

for msg in st.session_state.messages_home:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if pergunta := st.chat_input("Pergunte ao assistente sobre o planejamento estratégico..."):
    st.session_state.messages_home.append({"role": "user", "content": pergunta})
    
    with st.chat_message("user"):
        st.markdown(pergunta)
    
    with st.spinner("🤔 Pensando..."):
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"], base_url="https://openrouter.ai/api/v1")
            
            empresa_nome = data.get("empresa", {}).get("nome", "a empresa")
            empresa_setor = data.get("empresa", {}).get("setor", "não informado")
            
            contexto = f"""
            SIPE - SISTEMA INTEGRADO DE PLANEJAMENTO ESTRATÉGICO
            
            EMPRESA: {empresa_nome}
            SETOR: {empresa_setor}
            PROGRESSO: {progresso:.0f}%
            SEÇÕES PREENCHIDAS: {preenchidas}/{total_secoes}
            TOTAL DE AÇÕES: {len([a for a in data.get('acao_5w2h', []) if a.get('what')])}
            DEPARTAMENTOS: {len(data.get('departamentos', {}))}
            """
            
            mensagens = [
                {"role": "system", "content": f"""Você é um assistente especialista em Planejamento Estratégico.

{contexto}

O SIPE possui as seguintes seções:
1. Business Model Canvas
2. Análise PESTEL
3. 5 Forças de Porter
4. Análise SWOT
5. Planejamento Estratégico (MVV, SWOT Cruzada, Objetivos)
6. Plano de Ação 5W2H
7. Planos por Função (Departamentais)
8. Orçamento
9. Monitoramento
10. Revisão Estratégica
11. Painel de Controle
12. Relatório Completo

Responda em português do Brasil, de forma prática e objetiva."""}
            ] + st.session_state.messages_home[:-1]
            
            response = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=mensagens,
                temperature=0.7
            )
            
            resposta = response.choices[0].message.content
            st.session_state.messages_home.append({"role": "assistant", "content": resposta})
            
            with st.chat_message("assistant"):
                st.markdown(resposta)
                
        except Exception as e:
            st.error(f"❌ Erro ao processar sua pergunta: {str(e)}")
