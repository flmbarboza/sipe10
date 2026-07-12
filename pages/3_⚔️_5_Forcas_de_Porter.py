import pandas as pd
import streamlit as st
import json
import re
from utils.data_manager import init_data, get_data, sidebar_data_controls
from utils.ai_helper import sidebar_api_key_input, ai_assist_widget
from openai import OpenAI

st.set_page_config(page_title="5 Forças de Porter", page_icon="⚔️", layout="wide")
init_data()
data = get_data()

st.sidebar.title("🧭 Gestor Estratégico")
#sidebar_api_key_input()
sidebar_data_controls()

st.title("⚔️ 5 Forças de Porter")
st.caption(
    "Avalie a intensidade de cada força competitiva do setor (1 = muito baixa, 5 = muito alta) "
    "e registre suas observações. Isso ajuda a construir a Análise SWOT."
)

AJUDA = {
    "Rivalidade entre concorrentes": "Número e força dos concorrentes diretos, guerra de preços, diferenciação.",
    "Poder de barganha dos clientes": "Concentração de clientes, sensibilidade a preço, custo de troca.",
    "Poder de barganha dos fornecedores": "Concentração de fornecedores, insumos críticos, custo de troca.",
    "Ameaça de novos entrantes": "Barreiras de entrada, capital necessário, regulação, economia de escala.",
    "Ameaça de produtos substitutos": "Alternativas que atendem à mesma necessidade do cliente.",
}

def system_prompt():
    return (
        "Você é um consultor especialista no modelo das 5 Forças de Porter. Responda em "
        "português do Brasil, de forma prática e aplicada ao setor e localidade informados."
    )

# ========== INFORMAÇÕES DA EMPRESA ==========
empresa_nome = data.get("empresa", {}).get("nome", "a empresa")
empresa_setor = data.get("empresa", {}).get("setor", "não informado")
empresa_cidade = data.get("empresa", {}).get("cidade_estado", "")

# ========== BOTÕES DE AÇÃO ==========
st.subheader("🚀 Ações com IA")

col_gerar1, col_gerar2, col_gerar3 = st.columns([3, 1, 1])
with col_gerar1:
    st.caption("A IA vai analisar seu setor e gerar análise para todas as 5 forças")
with col_gerar2:
    gerar_porter = st.button("🔄 Gerar Análise Completa", use_container_width=True)
with col_gerar3:
    limpar_porter = st.button("🗑️ Limpar Análise", use_container_width=True, help="Remove toda a análise")
    
    if limpar_porter:
        for forca in AJUDA.keys():
            data["porter"][forca]["intensidade"] = 3
            data["porter"][forca]["notas"] = ""
        st.rerun()

# Processar geração completa
if gerar_porter:
    if not empresa_setor or empresa_setor == "não informado":
        st.warning("⚠️ Por favor, cadastre o setor da empresa na página inicial para uma análise mais precisa.")
    else:
        with st.spinner("🧠 Gerando análise das 5 Forças de Porter com IA..."):
            try:
                client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"], base_url="https://openrouter.ai/api/v1")
                
                prompt = f"""
                Você é um consultor especialista no modelo das 5 Forças de Porter.
                
                INFORMAÇÕES DA EMPRESA:
                - Nome: {empresa_nome}
                - Setor: {empresa_setor}
                - Localização: {empresa_cidade or "Não informado"}
                
                Analise as 5 Forças de Porter para este setor e localização.
                
                FORMATO DE SAÍDA (OBRIGATÓRIO): Retorne APENAS um JSON com o seguinte formato:
                {{
                    "Rivalidade entre concorrentes": {{
                        "intensidade": 3,
                        "notas": "análise detalhada"
                    }},
                    "Poder de barganha dos clientes": {{
                        "intensidade": 3,
                        "notas": "análise detalhada"
                    }},
                    "Poder de barganha dos fornecedores": {{
                        "intensidade": 3,
                        "notas": "análise detalhada"
                    }},
                    "Ameaça de novos entrantes": {{
                        "intensidade": 3,
                        "notas": "análise detalhada"
                    }},
                    "Ameaça de produtos substitutos": {{
                        "intensidade": 3,
                        "notas": "análise detalhada"
                    }}
                }}
                
                Intensidade deve ser um número de 1 a 5 (1=muito baixa, 5=muito alta).
                As notas devem ser análises objetivas em português do Brasil.
                Responda APENAS com o JSON, sem texto adicional.
                """
                
                response = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[
                        {"role": "system", "content": "Você é um consultor especialista em Porter. Responda em português do Brasil. Retorne APENAS JSON válido."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7
                )
                
                conteudo = response.choices[0].message.content
                
                try:
                    json_match = re.search(r'\{.*\}', conteudo, re.DOTALL)
                    if json_match:
                        dados = json.loads(json_match.group())
                    else:
                        dados = json.loads(conteudo)
                    
                    atualizados = 0
                    for forca in AJUDA.keys():
                        if forca in dados:
                            intensidade = dados[forca].get("intensidade", 3)
                            notas = dados[forca].get("notas", "")
                            
                            # Validar intensidade
                            if isinstance(intensidade, (int, float)):
                                intensidade = max(1, min(5, int(intensidade)))
                            else:
                                intensidade = 3
                            
                            # CORREÇÃO: Atualizar apenas se estiver vazio
                            if not data["porter"][forca].get("notas", ""):
                                data["porter"][forca]["intensidade"] = intensidade
                                data["porter"][forca]["notas"] = notas
                                atualizados += 1
                    
                    if atualizados > 0:
                        st.success(f"✅ {atualizados} forças foram analisadas pela IA!")
                        st.rerun()
                    else:
                        st.info("ℹ️ Todas as forças já estão preenchidas. Use 'Limpar Análise' para recomeçar.")
                        
                except json.JSONDecodeError as e:
                    st.error(f"❌ Erro ao parsear resposta da IA: {str(e)}")
                    st.code(conteudo)
                    
            except Exception as e:
                st.error(f"❌ Erro ao gerar análise: {str(e)}")

st.divider()

# ========== EXIBIÇÃO DAS FORÇAS ==========
for forca, ajuda in AJUDA.items():
    st.markdown(f"### {forca}")
    st.caption(ajuda)
    
    col1, col2 = st.columns([1, 3])
    with col1:
        intensidade = st.slider(
            "Intensidade", min_value=1, max_value=5,
            value=int(data["porter"][forca].get("intensidade", 3)),
            key=f"porter_int_{forca}",
        )
        data["porter"][forca]["intensidade"] = intensidade
        
        # Mostrar label da intensidade
        labels = {1: "Muito Baixa", 2: "Baixa", 3: "Média", 4: "Alta", 5: "Muito Alta"}
        st.caption(f"**{labels.get(intensidade, 'Média')}**")
    
    with col2:
        notas = st.text_area(
            "Observações", value=data["porter"][forca].get("notas", ""),
            key=f"porter_notas_{forca}", height=100,
        )
        data["porter"][forca]["notas"] = notas
    
    # Botão para sugerir com IA para esta força específica
    col_btn1, col_btn2 = st.columns([1, 5])
    with col_btn1:
        # CORREÇÃO: Botão Sugerir com key única
        if st.button(f"🤖 Sugerir", key=f"sugerir_{forca}", use_container_width=True):
            with st.spinner(f"Gerando análise para {forca}..."):
                try:
                    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"], base_url="https://openrouter.ai/api/v1")
                    
                    prompt_individual = f"""
                    INFORMAÇÕES DA EMPRESA:
                    - Nome: {empresa_nome}
                    - Setor: {empresa_setor}
                    - Localização: {empresa_cidade or "Não informado"}
                    
                    Força de Porter: {forca}
                    Descrição: {ajuda}
                    
                    Gere uma análise objetiva para esta força, incluindo:
                    1. Uma avaliação da intensidade (1-5) com justificativa
                    2. Observações detalhadas em 3-5 bullets
                    
                    Responda APENAS com um JSON no formato:
                    {{"intensidade": 3, "notas": "análise detalhada"}}
                    """
                    
                    response = client.chat.completions.create(
                        model="openai/gpt-oss-20b",
                        messages=[
                            {"role": "system", "content": "Você é um consultor especialista em Porter. Responda APENAS com JSON válido."},
                            {"role": "user", "content": prompt_individual}
                        ],
                        temperature=0.7
                    )
                    
                    sugestao = response.choices[0].message.content
                    
                    try:
                        # Tentar extrair JSON da resposta
                        json_match = re.search(r'\{.*\}', sugestao, re.DOTALL)
                        if json_match:
                            dados = json.loads(json_match.group())
                        else:
                            dados = json.loads(sugestao)
                        
                        nova_intensidade = dados.get("intensidade", 3)
                        novas_notas = dados.get("notas", "")
                        
                        # Validar intensidade
                        if isinstance(nova_intensidade, (int, float)):
                            nova_intensidade = max(1, min(5, int(nova_intensidade)))
                        else:
                            nova_intensidade = 3
                        
                        # CORREÇÃO: Atualizar APENAS esta força
                        if novas_notas:
                            data["porter"][forca]["intensidade"] = nova_intensidade
                            data["porter"][forca]["notas"] = novas_notas
                            st.success(f"✅ Análise atualizada para {forca}!")
                            st.rerun()
                        else:
                            st.warning("Nenhuma observação válida gerada.")
                            
                    except json.JSONDecodeError:
                        st.error("Erro ao processar a resposta da IA. Tente novamente.")
                        
                except Exception as e:
                    st.error(f"❌ Erro: {str(e)}")
    
    # Botão para limpar esta força específica
    with col_btn2:
        if st.button(f"🗑️ Limpar", key=f"limpar_{forca}", use_container_width=True):
            data["porter"][forca]["intensidade"] = 3
            data["porter"][forca]["notas"] = ""
            st.rerun()
    
    st.markdown("---")

# ========== RESUMO VISUAL ==========
st.subheader("📊 Resumo visual")
df_resumo = pd.DataFrame(
    [{"Força": f, "Intensidade": v["intensidade"]} for f, v in data["porter"].items()]
).set_index("Força")
st.bar_chart(df_resumo)

media = df_resumo["Intensidade"].mean()
st.metric("Intensidade competitiva média do setor", f"{media:.1f} / 5")

# ========== ASSISTENTE IA PARA AJUDA ==========
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
            
            # Preparar contexto com as análises atuais
            porter_atual = ""
            for forca, ajuda in AJUDA.items():
                porter_atual += f"\n{forca}:\n"
                porter_atual += f"  Intensidade: {data['porter'][forca].get('intensidade', 3)}/5\n"
                porter_atual += f"  Observações: {data['porter'][forca].get('notas', '(vazio)')}\n"
            
            mensagens = [
                {"role": "system", "content": f"""Você é um assistente especialista em Estratégia e 5 Forças de Porter.

EMPRESA: {empresa_nome}
SETOR: {empresa_setor}
LOCALIZAÇÃO: {empresa_cidade or 'Não informado'}

ANÁLISE ATUAL DAS 5 FORÇAS:
{porter_atual}

Responda em português do Brasil, de forma prática e objetiva.
Ajude o usuário a entender melhor cada força e como elas afetam o negócio."""}
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
