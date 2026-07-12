import streamlit as st
import json
import re
from utils.data_manager import init_data, get_data, sidebar_data_controls
from utils.ai_helper import sidebar_api_key_input, ai_assist_widget
from openai import OpenAI

st.set_page_config(page_title="Business Model Canvas", page_icon="📋", layout="wide")
init_data()
data = get_data()

st.sidebar.title("🧭 Gestor Estratégico")
#sidebar_api_key_input()
sidebar_data_controls()

st.title("📋 Business Model Canvas")
st.caption(
    "Preencha os 9 blocos do seu modelo de negócio. Edite livremente a qualquer momento."
)

BLOCOS = [
    ("parcerias_chave", "🤝 Parcerias-Chave", "Quem são seus principais fornecedores e parceiros? O que vocês trocam?"),
    ("atividades_chave", "⚙️ Atividades-Chave", "Quais atividades essenciais sua proposta de valor exige?"),
    ("recursos_chave", "🧱 Recursos-Chave", "Que recursos (físicos, humanos, financeiros, intelectuais) são indispensáveis?"),
    ("proposta_valor", "💎 Proposta de Valor", "Que problema você resolve? Que valor entrega ao cliente?"),
    ("relacionamento_clientes", "❤️ Relacionamento com Clientes", "Como vocês conquistam, mantêm e fazem crescer a base de clientes?"),
    ("canais", "📡 Canais", "Como a proposta de valor chega até o cliente (comunicação, venda, entrega)?"),
    ("segmentos_clientes", "🎯 Segmentos de Clientes", "Para quem vocês criam valor? Quem são os clientes mais importantes?"),
    ("estrutura_custos", "💸 Estrutura de Custos", "Quais são os custos mais importantes do modelo de negócio?"),
    ("fontes_receita", "💰 Fontes de Receita", "Por qual valor os clientes estão dispostos a pagar, e como pagam?"),
]

def system_prompt():
    return (
        "Você é um consultor sênior de estratégia e modelagem de negócios (Business Model Canvas). "
        "Responda em português do Brasil, de forma objetiva, prática e estruturada em tópicos curtos."
    )

# ========== SEÇÃO DE INFORMAÇÕES ADICIONAIS ==========
with st.expander("📋 Informações para o Business Model Canvas", expanded=False):
    st.markdown("**Preencha as informações abaixo para ajudar a IA a gerar sugestões mais precisas:**")
    
    # CORREÇÃO: Garantir que bmc_info existe
    if "bmc_info" not in data:
        data["bmc_info"] = {}
    
    col_info1, col_info2 = st.columns(2)
    
    with col_info1:
        # Descrição do negócio
        descricao_negocio = st.text_area(
            "📝 Descrição do negócio",
            value=data["bmc_info"].get("descricao", ""),
            placeholder="Descreva brevemente o que sua empresa faz...",
            height=80,
            help="Uma visão geral do seu negócio para contextualizar a IA",
            key="bmc_descricao"  # Adicionar key única
        )
        
        # Diferenciais competitivos
        diferenciais = st.text_area(
            "⭐ Diferenciais competitivos",
            value=data["bmc_info"].get("diferenciais", ""),
            placeholder="Ex: Tecnologia proprietária, equipe especializada, parcerias exclusivas...",
            height=80,
            help="O que torna sua empresa única no mercado",
            key="bmc_diferenciais"  # Adicionar key única
        )
    
    with col_info2:
        # Público-alvo
        publico_alvo = st.text_area(
            "🎯 Público-alvo",
            value=data["bmc_info"].get("publico_alvo", ""),
            placeholder="Ex: Pequenas empresas, consumidores finais, indústrias...",
            height=80,
            help="Quem são seus clientes principais",
            key="bmc_publico_alvo"  # Adicionar key única
        )
        
        # Observações adicionais
        observacoes_bmc = st.text_area(
            "📝 Observações adicionais",
            value=data["bmc_info"].get("observacoes", ""),
            placeholder="Qualquer informação adicional relevante para o modelo de negócio...",
            height=80,
            help="Informações extras que podem ajudar a IA",
            key="bmc_observacoes"  # Adicionar key única
        )
    
    # CORREÇÃO: Salvar automaticamente quando o usuário edita
    if data["bmc_info"].get("descricao", "") != descricao_negocio:
        data["bmc_info"]["descricao"] = descricao_negocio
    if data["bmc_info"].get("diferenciais", "") != diferenciais:
        data["bmc_info"]["diferenciais"] = diferenciais
    if data["bmc_info"].get("publico_alvo", "") != publico_alvo:
        data["bmc_info"]["publico_alvo"] = publico_alvo
    if data["bmc_info"].get("observacoes", "") != observacoes_bmc:
        data["bmc_info"]["observacoes"] = observacoes_bmc

st.divider()

# ========== OBTENDO INFORMAÇÕES DA EMPRESA ==========
# CORREÇÃO: Garantir que as informações da empresa estão disponíveis
empresa_nome = data.get("empresa", {}).get("nome", "a empresa")
empresa_setor = data.get("empresa", {}).get("setor", "não informado")
empresa_cidade = data.get("empresa", {}).get("cidade_estado", "")
empresa_responsavel = data.get("empresa", {}).get("responsavel", "")

# Verificar se os dados da empresa existem
if not empresa_nome or empresa_nome == "a empresa":
    st.info("ℹ️ Cadastre os dados da empresa na página inicial para obter sugestões mais precisas da IA.")

# ========== BOTÃO PARA GERAR O BMC COMPLETO ==========
st.subheader("🚀 Gerar Business Model Canvas com IA")

col_gerar1, col_gerar2, col_gerar3 = st.columns([3, 1, 1])
with col_gerar1:
    st.caption("A IA vai analisar suas informações e gerar conteúdo para todos os 9 blocos do BMC")
with col_gerar2:
    gerar_bmc = st.button("🔄 Gerar BMC Completo", use_container_width=True)
with col_gerar3:
    limpar_bmc = st.button("🗑️ Limpar BMC", use_container_width=True, help="Remove todo o conteúdo do BMC")
    
    if limpar_bmc:
        for chave, _, _ in BLOCOS:
            data["bmc"][chave] = ""
        # CORREÇÃO: Também limpar as informações adicionais
        if "bmc_info" in data:
            data["bmc_info"] = {}
        st.rerun()

# Processar geração do BMC
if gerar_bmc:
    if not descricao_negocio and not empresa_nome:
        st.warning("⚠️ Por favor, preencha pelo menos a descrição do negócio ou o nome da empresa para gerar o BMC.")
    else:
        with st.spinner("🧠 Gerando Business Model Canvas com IA..."):
            try:
                client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"], base_url="https://openrouter.ai/api/v1")
                
                prompt = f"""
                Você é um consultor sênior de estratégia e modelagem de negócios especializado em Business Model Canvas.
                
                INFORMAÇÕES DA EMPRESA:
                - Nome: {empresa_nome}
                - Setor: {empresa_setor}
                - Cidade/Estado: {empresa_cidade or "Não informado"}
                - Responsável: {empresa_responsavel or "Não informado"}
                - Descrição do negócio: {descricao_negocio or "Não informado"}
                - Diferenciais competitivos: {diferenciais or "Não informado"}
                - Público-alvo: {publico_alvo or "Não informado"}
                - Observações adicionais: {observacoes_bmc or "Não informado"}
                
                Com base nas informações acima, preencha os 9 blocos do Business Model Canvas.
                
                IMPORTANTE: Use as informações da empresa fornecidas. Se alguma informação não foi fornecida, use seu conhecimento geral de negócios para sugerir conteúdo relevante.
                
                FORMATO DE SAÍDA (OBRIGATÓRIO): Retorne APENAS um JSON com os seguintes campos:
                {{
                    "parcerias_chave": "texto",
                    "atividades_chave": "texto",
                    "recursos_chave": "texto",
                    "proposta_valor": "texto",
                    "relacionamento_clientes": "texto",
                    "canais": "texto",
                    "segmentos_clientes": "texto",
                    "estrutura_custos": "texto",
                    "fontes_receita": "texto"
                }}
                
                Cada texto deve ser objetivo, prático e em português do Brasil. Use bullets ou tópicos curtos quando apropriado.
                Responda APENAS com o JSON, sem texto adicional.
                """
                
                response = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[
                        {"role": "system", "content": "Você é um consultor sênior de estratégia e modelagem de negócios. Responda em português do Brasil. Retorne APENAS JSON válido."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7
                )
                
                conteudo = response.choices[0].message.content
                
                # Tentar extrair JSON da resposta
                try:
                    json_match = re.search(r'\{.*\}', conteudo, re.DOTALL)
                    if json_match:
                        dados = json.loads(json_match.group())
                    else:
                        dados = json.loads(conteudo)
                    
                    # Atualizar cada bloco com o conteúdo gerado
                    blocos_atualizados = 0
                    for chave, _, _ in BLOCOS:
                        if chave in dados and dados[chave]:
                            # Só atualizar se o bloco estiver vazio ou se o usuário confirmar
                            if not data["bmc"].get(chave, ""):
                                data["bmc"][chave] = dados[chave]
                                blocos_atualizados += 1
                    
                    if blocos_atualizados > 0:
                        st.success(f"✅ {blocos_atualizados} blocos do BMC foram preenchidos pela IA!")
                        st.rerun()
                    else:
                        st.info("ℹ️ Todos os blocos já estão preenchidos. Use o botão 'Limpar BMC' para recomeçar.")
                        
                except json.JSONDecodeError as e:
                    st.error(f"❌ Erro ao parsear resposta da IA: {str(e)}")
                    st.code(conteudo)
                    
            except Exception as e:
                st.error(f"❌ Erro ao gerar BMC: {str(e)}")

st.divider()

# ========== EXIBIÇÃO DOS BLOCOS ==========
col_a, col_b, col_c = st.columns(3)
cols_map = {0: col_a, 1: col_a, 2: col_a, 3: col_b, 4: col_b, 5: col_b, 6: col_c, 7: col_c, 8: col_c}

for i, (chave, titulo, ajuda) in enumerate(BLOCOS):
    with cols_map[i]:
        st.markdown(f"#### {titulo}")
        valor = st.text_area(
            ajuda, 
            value=data["bmc"].get(chave, ""), 
            key=f"bmc_{chave}", 
            height=140, 
            label_visibility="visible"
        )
        # Salvar automaticamente quando o usuário edita
        if data["bmc"].get(chave, "") != valor:
            data["bmc"][chave] = valor
        
        # Botão individual para gerar cada bloco
        col_btn1, col_btn2 = st.columns([3, 1])
        with col_btn1:
            if st.button(f"🤖 Sugerir {titulo.split(' ')[0]}", key=f"sugerir_{chave}", use_container_width=True):
                with st.spinner(f"Gerando sugestão para {titulo}..."):
                    try:
                        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"], base_url="https://openrouter.ai/api/v1")
                        
                        prompt_individual = f"""
                        INFORMAÇÕES DA EMPRESA:
                        - Nome: {empresa_nome}
                        - Setor: {empresa_setor}
                        - Cidade/Estado: {empresa_cidade or "Não informado"}
                        - Descrição: {descricao_negocio or "Não informado"}
                        - Diferenciais: {diferenciais or "Não informado"}
                        - Público-alvo: {publico_alvo or "Não informado"}
                        
                        Bloco do BMC: {titulo}
                        Pergunta-guia: {ajuda}
                        Conteúdo atual: {data["bmc"].get(chave, "") or "(vazio)"}
                        
                        Gere um conteúdo objetivo e prático para este bloco do Business Model Canvas.
                        Considere as informações da empresa fornecidas acima.
                        Responda em português do Brasil, com 3-5 tópicos ou bullets.
                        """
                        
                        response = client.chat.completions.create(
                            model="openai/gpt-oss-20b",
                            messages=[
                                {"role": "system", "content": "Você é um consultor sênior de estratégia. Responda em português do Brasil, de forma objetiva e prática."},
                                {"role": "user", "content": prompt_individual}
                            ],
                            temperature=0.7
                        )
                        
                        sugestao = response.choices[0].message.content
                        
                        # Atualizar o campo
                        data["bmc"][chave] = sugestao
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Erro ao gerar sugestão: {str(e)}")
        
        with col_btn2:
            if st.button(f"🗑️", key=f"limpar_{chave}", help=f"Limpar {titulo}"):
                data["bmc"][chave] = ""
                st.rerun()
        
        st.markdown("---")

st.success("As alterações são salvas automaticamente na sessão. Não esqueça de baixar o JSON na barra lateral.")

# ========== ASSISTENTE IA PARA AJUDA ==========
st.divider()
st.subheader("💬 Assistente IA - Ajuda com o Business Model Canvas")

# Botão para limpar chat
col_chat1, col_chat2 = st.columns([5, 1])
with col_chat2:
    if st.button("🗑️ Limpar Chat", use_container_width=True):
        st.session_state.messages_bmc = []
        st.rerun()

if "messages_bmc" not in st.session_state:
    st.session_state.messages_bmc = []

for msg in st.session_state.messages_bmc:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if pergunta := st.chat_input("Pergunte ao assistente sobre seu Business Model Canvas..."):
    st.session_state.messages_bmc.append({"role": "user", "content": pergunta})
    
    with st.chat_message("user"):
        st.markdown(pergunta)
    
    with st.spinner("🤔 Pensando..."):
        try:
            client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"], base_url="https://openrouter.ai/api/v1")
            
            # Preparar contexto com o BMC atual
            bmc_atual = ""
            for chave, titulo, _ in BLOCOS:
                conteudo = data["bmc"].get(chave, "Vazio")
                if conteudo:
                    bmc_atual += f"\n{titulo}:\n{conteudo}\n"
            
            mensagens = [
                {"role": "system", "content": f"""Você é um assistente especializado em Business Model Canvas e modelagem de negócios.

INFORMAÇÕES DA EMPRESA:
- Nome: {empresa_nome}
- Setor: {empresa_setor}
- Cidade/Estado: {empresa_cidade or 'Não informado'}
- Responsável: {empresa_responsavel or 'Não informado'}
- Descrição: {descricao_negocio or 'Não informado'}
- Diferenciais: {diferenciais or 'Não informado'}
- Público-alvo: {publico_alvo or 'Não informado'}

BUSINESS MODEL CANVAS ATUAL:
{bmc_atual or 'Nenhum bloco preenchido ainda'}

INSTRUÇÕES:
1. Responda em português do Brasil
2. Seja prático e objetivo
3. Use as informações da empresa para contextualizar suas respostas
4. Se o usuário pedir para sugerir ou melhorar um bloco específico, forneça sugestões detalhadas
5. Se o usuário pedir para preencher um bloco, responda com o conteúdo sugerido

Responda de forma útil e orientada a ação."""}
            ] + st.session_state.messages_bmc[:-1]
            
            response = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=mensagens,
                temperature=0.7
            )
            
            resposta = response.choices[0].message.content
            
            st.session_state.messages_bmc.append({"role": "assistant", "content": resposta})
            
            with st.chat_message("assistant"):
                st.markdown(resposta)
                
        except Exception as e:
            st.error(f"❌ Erro ao processar sua pergunta: {str(e)}")
