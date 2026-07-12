import pandas as pd
import streamlit as st
from utils.data_manager import init_data, get_data, sidebar_data_controls
from utils.ai_helper import sidebar_api_key_input, ai_assist_widget
from openai import OpenAI

st.set_page_config(page_title="Plano de Ação 5W2H", page_icon="✅", layout="wide")
init_data()
data = get_data()

st.sidebar.title("🧭 Gestor Estratégico")
#sidebar_api_key_input()
sidebar_data_controls()

st.title("✅ Plano de Ação (5W2H)")
st.caption(
    "What (o quê), Why (por quê), Where (onde), When (quando), Who (quem), "
    "How (como) e How much (quanto custa)."
)

# ========== SEÇÃO DE INFORMAÇÕES ADICIONAIS ==========
with st.expander("📋 Informações para o Plano de Ação", expanded=True):
    st.markdown("**Preencha as informações abaixo para ajudar a IA a gerar um plano de ação mais preciso:**")
    
    col_info1, col_info2 = st.columns(2)
    
    with col_info1:
        # Pessoas envolvidas
        pessoas = st.text_area(
            "👥 Pessoas envolvidas",
            value=data.get("acao_info", {}).get("pessoas", ""),
            placeholder="Ex: João (Gerente de Vendas), Maria (Marketing), Carlos (Operações)...",
            height=80,
            help="Liste as principais pessoas envolvidas na execução do plano"
        )
        
        # Recursos disponíveis
        recursos = st.text_area(
            "🔧 Recursos disponíveis",
            value=data.get("acao_info", {}).get("recursos", ""),
            placeholder="Ex: Orçamento de R$ 50.000, equipe de 5 pessoas, software X, veículos...",
            height=80,
            help="Recursos materiais, financeiros e humanos disponíveis"
        )
    
    with col_info2:
        # Restrições/limitações
        restricoes = st.text_area(
            "⚠️ Restrições ou limitações",
            value=data.get("acao_info", {}).get("restricoes", ""),
            placeholder="Ex: Prazo máximo de 3 meses, orçamento limitado, falta de pessoal...",
            height=80,
            help="O que pode limitar a execução do plano"
        )
        
        # Observações adicionais
        observacoes = st.text_area(
            "📝 Observações adicionais",
            value=data.get("acao_info", {}).get("observacoes", ""),
            placeholder="Ex: Prioridade para ações de baixo custo, foco em resultados rápidos...",
            height=80,
            help="Qualquer informação adicional relevante"
        )
    
    # Salvar informações
    if "acao_info" not in data:
        data["acao_info"] = {}
    data["acao_info"]["pessoas"] = pessoas
    data["acao_info"]["recursos"] = recursos
    data["acao_info"]["restricoes"] = restricoes
    data["acao_info"]["observacoes"] = observacoes

# ========== BOTÃO PARA GERAR PLANO COM IA ==========
st.divider()

# Verificar se há objetivos definidos
objetivos = [o.get("objetivo", "") for o in data.get("objetivos", []) if o.get("objetivo")]

col_gerar1, col_gerar2 = st.columns([3, 1])
with col_gerar1:
    st.markdown("**🤖 Gerar Plano de Ação com IA**")
    st.caption("A IA vai analisar seus objetivos estratégicos e gerar um plano 5W2H personalizado")
with col_gerar2:
    gerar_plano = st.button("🚀 Gerar Plano", use_container_width=True)

# Processar geração do plano
if gerar_plano:
    if not objetivos:
        st.warning("⚠️ Nenhum objetivo estratégico encontrado. Por favor, defina os objetivos na página de Planejamento Estratégico primeiro.")
    else:
        with st.spinner("🧠 Gerando plano de ação com IA..."):
            try:
                # Preparar o prompt para a IA
                client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"], base_url="https://openrouter.ai/api/v1")
                
                # Buscar informações adicionais
                empresa = data.get("empresa", {}).get("nome", "a empresa")
                setor = data.get("empresa", {}).get("setor", "não informado")
                
                prompt = f"""
                Você é um consultor de gestão especializado em planos de ação 5W2H.
                
                INFORMAÇÕES DA EMPRESA:
                - Nome: {empresa}
                - Setor: {setor}
                
                OBJETIVOS ESTRATÉGICOS:
                {chr(10).join([f"- {obj}" for obj in objetivos])}
                
                PESSOAS ENVOLVIDAS:
                {pessoas or "Não informado"}
                
                RECURSOS DISPONÍVEIS:
                {recursos or "Não informado"}
                
                RESTRIÇÕES:
                {restricoes or "Não informado"}
                
                OBSERVAÇÕES:
                {observacoes or "Não informado"}
                
                Com base nas informações acima, crie um plano de ação 5W2H detalhado com as seguintes características:
                1. Gere de 3 a 5 ações principais
                2. Cada ação deve ter todos os campos do 5W2H preenchidos
                3. Seja específico e prático
                4. Considere as pessoas, recursos e restrições informadas
                
                Formato de saída: APENAS uma tabela com as colunas: What (o quê), Why (por quê), Where (onde), When (quando), Who (quem), How (como), How much (quanto custa), Status (Não iniciado)
                
                Status inicial: "Não iniciado" para todas as ações.
                """
                
                # Chamar a IA
                response = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[
                        {"role": "system", "content": "Você é um consultor de gestão especializado em planos de ação 5W2H. Responda em português do Brasil, de forma prática e orientada a execução. Sempre retorne apenas a tabela no formato solicitado."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7
                )
                
                conteudo = response.choices[0].message.content
                
                # Tentar parsear a tabela
                linhas = conteudo.strip().split('\n')
                novas_acoes = []
                
                # Procurar pela linha de cabeçalho
                header_idx = -1
                for i, linha in enumerate(linhas):
                    if 'What' in linha and 'Why' in linha and 'Where' in linha:
                        header_idx = i
                        break
                
                if header_idx >= 0:
                    # Extrair dados das linhas
                    for linha in linhas[header_idx+1:]:
                        if linha.strip() and '|' in linha:
                            partes = [p.strip() for p in linha.split('|') if p.strip()]
                            if len(partes) >= 7:
                                nova_acao = {
                                    "what": partes[0] if len(partes) > 0 else "",
                                    "why": partes[1] if len(partes) > 1 else "",
                                    "where": partes[2] if len(partes) > 2 else "",
                                    "when": partes[3] if len(partes) > 3 else "",
                                    "who": partes[4] if len(partes) > 4 else "",
                                    "how": partes[5] if len(partes) > 5 else "",
                                    "how_much": partes[6] if len(partes) > 6 else "",
                                    "status": "Não iniciado"
                                }
                                novas_acoes.append(nova_acao)
                
                if novas_acoes:
                    # Mesclar com ações existentes (evitar duplicatas)
                    existentes = data.get("acao_5w2h", [])
                    novos = [a for a in novas_acoes if a not in existentes]
                    
                    if novos:
                        data["acao_5w2h"] = existentes + novos
                        st.success(f"✅ {len(novos)} novas ações geradas e adicionadas ao plano!")
                        st.rerun()
                    else:
                        st.info("ℹ️ As ações geradas já existem no plano.")
                else:
                    st.error("❌ Não foi possível parsear a resposta da IA. Tente novamente.")
                    st.code(conteudo)
                    
            except Exception as e:
                st.error(f"❌ Erro ao gerar plano: {str(e)}")

# ========== EXIBIÇÃO DO PLANO DE AÇÃO ==========
st.divider()
st.subheader("📋 Plano de Ação")

itens = data.get("acao_5w2h", [])
colunas = ["what", "why", "where", "when", "who", "how", "how_much", "status"]
nomes_colunas = {
    "what": "O quê (What)",
    "why": "Por quê (Why)",
    "where": "Onde (Where)",
    "when": "Quando (When)",
    "who": "Quem (Who)",
    "how": "Como (How)",
    "how_much": "Quanto custa (How much)",
    "status": "Status",
}

# Garantir que todos os itens tenham todas as colunas
for item in itens:
    for col in colunas:
        if col not in item:
            item[col] = ""

# Criar DataFrame com tipos corretos
if itens:
    df = pd.DataFrame(itens)
    for col in colunas:
        if col not in df.columns:
            df[col] = ""
        if col != "status":
            df[col] = df[col].astype(str)
else:
    df = pd.DataFrame({col: pd.Series(dtype="object") for col in colunas})

# Hash para forçar recriação
df_hash = hash(str(sorted([str(item) for item in itens]))) if itens else 0
editor_key = f"editor_5w2h_{df_hash}"

edited = st.data_editor(
    df,
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True,
    key=editor_key,
    column_config={
        "what": st.column_config.TextColumn(nomes_colunas["what"], width="large"),
        "why": st.column_config.TextColumn(nomes_colunas["why"], width="large"),
        "where": st.column_config.TextColumn(nomes_colunas["where"]),
        "when": st.column_config.TextColumn(nomes_colunas["when"]),
        "who": st.column_config.TextColumn(nomes_colunas["who"]),
        "how": st.column_config.TextColumn(nomes_colunas["how"], width="large"),
        "how_much": st.column_config.TextColumn(nomes_colunas["how_much"]),
        "status": st.column_config.SelectboxColumn(
            nomes_colunas["status"], options=["Não iniciado", "Em andamento", "Concluído", "Atrasado"]
        ),
    },
)

# Processar dados editados
if edited is not None:
    edited = edited.fillna("")
    novos_itens = []
    for _, row in edited.iterrows():
        what = str(row.get("what", "")).strip()
        if what:
            novo_item = {}
            for col in colunas:
                valor = row.get(col, "")
                if col == "status" and not valor:
                    valor = "Não iniciado"
                novo_item[col] = str(valor).strip() if col != "status" else valor
            novos_itens.append(novo_item)
    
    if novos_itens != data.get("acao_5w2h", []):
        data["acao_5w2h"] = novos_itens
        st.rerun()

# Botão de download
if data.get("acao_5w2h"):
    df_download = pd.DataFrame(data["acao_5w2h"])
    st.download_button(
        "⬇️ Baixar Plano de Ação (CSV)",
        data=df_download.rename(columns=nomes_colunas).to_csv(index=False).encode("utf-8-sig"),
        file_name="plano_de_acao_5w2h.csv",
        mime="text/csv",
    )

st.divider()

# ========== ASSISTENTE IA PARA AJUDA ==========
st.subheader("💬 Assistente IA - Ajuda com o Plano de Ação")

if "messages_acao" not in st.session_state:
    st.session_state.messages_acao = []

for msg in st.session_state.messages_acao:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if pergunta := st.chat_input("Pergunte ao assistente sobre seu plano de ação..."):
    st.session_state.messages_acao.append({"role": "user", "content": pergunta})
    
    with st.chat_message("user"):
        st.markdown(pergunta)
    
    with st.spinner("🤔 Pensando..."):
        try:
            client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"], base_url="https://openrouter.ai/api/v1")
            
            # Preparar contexto com informações do plano atual
            plano_atual = ""
            for i, acao in enumerate(data.get("acao_5w2h", []), 1):
                plano_atual += f"\nAção {i}:\n"
                plano_atual += f"  What: {acao.get('what', '')}\n"
                plano_atual += f"  Why: {acao.get('why', '')}\n"
                plano_atual += f"  Where: {acao.get('where', '')}\n"
                plano_atual += f"  When: {acao.get('when', '')}\n"
                plano_atual += f"  Who: {acao.get('who', '')}\n"
                plano_atual += f"  How: {acao.get('how', '')}\n"
                plano_atual += f"  How much: {acao.get('how_much', '')}\n"
                plano_atual += f"  Status: {acao.get('status', 'Não iniciado')}\n"
            
            mensagens = [
                {"role": "system", "content": f"""Você é um assistente especializado em planos de ação 5W2H e gestão estratégica.

INFORMAÇÕES DA EMPRESA:
- Nome: {data.get('empresa', {}).get('nome', 'a empresa')}
- Setor: {data.get('empresa', {}).get('setor', 'não informado')}

OBJETIVOS ESTRATÉGICOS:
{chr(10).join([f"- {obj}" for obj in objetivos]) if objetivos else 'Nenhum objetivo definido ainda'}

PLANO DE AÇÃO ATUAL:
{plano_atual or 'Nenhuma ação definida ainda'}

PESSOAS ENVOLVIDAS:
{pessoas or 'Não informado'}

RECURSOS DISPONÍVEIS:
{recursos or 'Não informado'}

RESTRIÇÕES:
{restricoes or 'Não informado'}

Responda em português do Brasil, de forma prática e orientada a execução. Seja útil e objetivo."""}
            ] + st.session_state.messages_acao
            
            response = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=mensagens,
                temperature=0.7
            )
            
            resposta = response.choices[0].message.content
            
            st.session_state.messages_acao.append({"role": "assistant", "content": resposta})
            
            with st.chat_message("assistant"):
                st.markdown(resposta)
                
        except Exception as e:
            st.error(f"❌ Erro ao processar sua pergunta: {str(e)}")
