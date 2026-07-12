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
    ("📋", "Business Model Canvas", "Os 9 blocos do seu modelo de negócio.", "1_📋_Business_Model_Canvas"),
    ("🌍", "Análise PESTEL", "Fatores externos: Político, Econômico, Social, Tecnológico, Ecológico, Legal.", "2_🌍_Analise_PESTEL"),
    ("⚔️", "5 Forças de Porter", "Intensidade competitiva do setor.", "3_⚔️_5_Forcas_de_Porter"),
    ("🎯", "Análise SWOT", "Forças, Fraquezas, Oportunidades e Ameaças, alimentada pelas análises acima.", "4_🎯_Analise_SWOT"),
    ("🧭", "Planejamento Estratégico", "Missão, Visão, Valores, SWOT cruzada, Objetivos e KPIs.", "5_🧭_Planejamento_Estrategico"),
    ("✅", "Plano de Ação (5W2H)", "O que, por quê, onde, quando, quem, como e quanto custa.", "6_✅_Plano_de_Acao_5W2H"),
    ("📋", "Planos por Função", "Planos departamentais com objetivos, ações, indicadores e riscos.", "7_📋_Planos_por_Funcao"),
    ("💰", "Orçamento", "Consolidação financeira, fluxo de caixa e indicadores.", "8_💰_Orcamento"),
    ("🛃", "Monitoramento", "Acompanhamento de KPIs, ações e alertas.", "9_🛃_Monitoramento"),
    ("🔄", "Revisão Estratégica", "Revisão periódica com lições aprendidas e recomendações.", "10_🔄_Revisao_Estrategica"),
    ("📈", "Painel de Controle", "Visão consolidada de todo o planejamento.", "11_📈_Painel_de_Controle"),
    ("📄", "Relatório Completo", "Compilação de tudo, pronta para exportar.", "12_📄_Relatorio_Completo"),
]

cols = st.columns(2)
for i, (icone, titulo, desc, pagina) in enumerate(etapas):
    with cols[i % 2]:
        col_etapa1, col_etapa2 = st.columns([4, 1])
        with col_etapa1:
            st.markdown(f"**{icone} {titulo}**")
            st.caption(desc)
        with col_etapa2:
            if st.button("➡️", key=f"go_{i}", help=f"Ir para {titulo}"):
                st.switch_page(f"pages/{pagina}.py")

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
# Encontrar a próxima etapa não concluída
proxima_etapa = None
for icone, titulo, desc, pagina in etapas:
    if titulo == "Business Model Canvas" and not data.get("bmc") or not any(data["bmc"].values()):
        proxima_etapa = (titulo, pagina)
        break
    elif titulo == "Análise PESTEL" and not data.get("pestel") or not any([any([i.get("descricao") for i in itens]) for itens in data["pestel"].values()]):
        proxima_etapa = (titulo, pagina)
        break
    elif titulo == "5 Forças de Porter" and not data.get("porter_analise") or not any([v.get("notas") for v in data["porter_analise"].values()]):
        proxima_etapa = (titulo, pagina)
        break
    elif titulo == "Análise SWOT" and not data.get("swot") or not any([any([i.get("descricao") for i in itens]) for itens in data["swot"].values()]):
        proxima_etapa = (titulo, pagina)
        break
    elif titulo == "Planejamento Estratégico" and not data.get("objetivos") or not any([o.get("objetivo") for o in data["objetivos"]]):
        proxima_etapa = (titulo, pagina)
        break
    elif titulo == "Plano de Ação (5W2H)" and not data.get("acao_5w2h") or not any([a.get("what") for a in data["acao_5w2h"]]):
        proxima_etapa = (titulo, pagina)
        break
    elif titulo == "Planos por Função" and not data.get("departamentos") or not any([any([v for v in depto.values() if v]) for depto in data["departamentos"].values()]):
        proxima_etapa = (titulo, pagina)
        break
    elif titulo == "Orçamento" and not data.get("orcamento") or not (data["orcamento"].get("receitas") or data["orcamento"].get("investimentos")):
        proxima_etapa = (titulo, pagina)
        break
    elif titulo == "Monitoramento" and not data.get("monitoramento") or not data["monitoramento"].get("alertas"):
        proxima_etapa = (titulo, pagina)
        break
    elif titulo == "Revisão Estratégica":
        proxima_etapa = (titulo, pagina)
        break

if proxima_etapa:
    titulo, pagina = proxima_etapa
    col_prox1, col_prox2, col_prox3 = st.columns([1, 2, 1])
    with col_prox2:
        if st.button(f"🚀 Próxima Etapa: {titulo}", use_container_width=True):
            st.switch_page(f"pages/{pagina}.py")

# ========== ASSISTENTE IA PARA AJUDA ==========
st.divider()
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
            import re
            
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
0. Início - Dados da empresa
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
