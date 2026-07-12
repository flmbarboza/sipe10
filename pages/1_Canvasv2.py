import streamlit as st
import json
import re
import pandas as pd
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
    "Preencha os 9 blocos do seu modelo de negócio seguindo a estrutura do Canvas. "
    "Cada bloco pode ter múltiplos itens."
)

# ========== DEFINIÇÃO DOS BLOCOS ==========
# Estrutura: (chave, título, descrição, placeholder)
BLOCOS = [
    # Lado Direito (Cliente)
    ("proposta_valor", "💎 Proposta de Valor", 
     "Que problema você resolve? Que valor entrega ao cliente?",
     "Ex: Produto/serviço que resolve X problema, economia de 30% em custos..."),
    
    ("segmentos_clientes", "🎯 Segmentos de Clientes", 
     "Para quem vocês criam valor? Quem são os clientes mais importantes?",
     "Ex: Pequenas empresas, consumidores finais, indústrias..."),
    
    ("canais", "📡 Canais", 
     "Como a proposta de valor chega até o cliente (comunicação, venda, entrega)?",
     "Ex: Site próprio, loja física, marketplaces, WhatsApp..."),
    
    ("relacionamento_clientes", "❤️ Relacionamento com Clientes", 
     "Como vocês conquistam, mantêm e fazem crescer a base de clientes?",
     "Ex: Atendimento personalizado, programas de fidelidade, suporte 24h..."),
    
    # Lado Esquerdo (Infraestrutura)
    ("parcerias_chave", "🤝 Parcerias-Chave", 
     "Quem são seus principais fornecedores e parceiros? O que vocês trocam?",
     "Ex: Fornecedores de matéria-prima, canais de distribuição, alianças estratégicas..."),
    
    ("atividades_chave", "⚙️ Atividades-Chave", 
     "Quais atividades essenciais sua proposta de valor exige?",
     "Ex: Produção, marketing, vendas, pós-venda, desenvolvimento..."),
    
    ("recursos_chave", "🧱 Recursos-Chave", 
     "Que recursos (físicos, humanos, financeiros, intelectuais) são indispensáveis?",
     "Ex: Equipe especializada, patentes, capital, equipamentos..."),
    
    # Base Financeira
    ("estrutura_custos", "💸 Estrutura de Custos", 
     "Quais são os custos mais importantes do modelo de negócio?",
     "Ex: Custos fixos, variáveis, marketing, pessoal, infraestrutura..."),
    
    ("fontes_receita", "💰 Fontes de Receita", 
     "Por qual valor os clientes estão dispostos a pagar, e como pagam?",
     "Ex: Vendas, assinaturas, comissões, publicidade, licenciamento..."),
]

def system_prompt():
    return (
        "Você é um consultor sênior de estratégia e modelagem de negócios (Business Model Canvas). "
        "Responda em português do Brasil, de forma objetiva, prática e estruturada em tópicos curtos."
    )

# ========== SEÇÃO DE INFORMAÇÕES ADICIONAIS ==========
with st.expander("📋 Informações para o Business Model Canvas", expanded=False):
    st.markdown("**Preencha as informações abaixo para ajudar a IA a gerar sugestões mais precisas:**")
    
    if "bmc_info" not in data:
        data["bmc_info"] = {}
    
    col_info1, col_info2 = st.columns(2)
    
    with col_info1:
        descricao_negocio = st.text_area(
            "📝 Descrição do negócio",
            value=data["bmc_info"].get("descricao", ""),
            placeholder="Descreva brevemente o que sua empresa faz...",
            height=80,
            key="bmc_descricao"
        )
        
        diferenciais = st.text_area(
            "⭐ Diferenciais competitivos",
            value=data["bmc_info"].get("diferenciais", ""),
            placeholder="Ex: Tecnologia proprietária, equipe especializada, parcerias exclusivas...",
            height=80,
            key="bmc_diferenciais"
        )
    
    with col_info2:
        publico_alvo = st.text_area(
            "🎯 Público-alvo",
            value=data["bmc_info"].get("publico_alvo", ""),
            placeholder="Ex: Pequenas empresas, consumidores finais, indústrias...",
            height=80,
            key="bmc_publico_alvo"
        )
        
        observacoes_bmc = st.text_area(
            "📝 Observações adicionais",
            value=data["bmc_info"].get("observacoes", ""),
            placeholder="Qualquer informação adicional relevante...",
            height=80,
            key="bmc_observacoes"
        )
    
    # Salvar automaticamente
    if data["bmc_info"].get("descricao", "") != descricao_negocio:
        data["bmc_info"]["descricao"] = descricao_negocio
    if data["bmc_info"].get("diferenciais", "") != diferenciais:
        data["bmc_info"]["diferenciais"] = diferenciais
    if data["bmc_info"].get("publico_alvo", "") != publico_alvo:
        data["bmc_info"]["publico_alvo"] = publico_alvo
    if data["bmc_info"].get("observacoes", "") != observacoes_bmc:
        data["bmc_info"]["observacoes"] = observacoes_bmc

st.divider()

# ========== INFORMAÇÕES DA EMPRESA ==========
empresa_nome = data.get("empresa", {}).get("nome", "a empresa")
empresa_setor = data.get("empresa", {}).get("setor", "não informado")
empresa_cidade = data.get("empresa", {}).get("cidade_estado", "")
empresa_responsavel = data.get("empresa", {}).get("responsavel", "")

if not empresa_nome or empresa_nome == "a empresa":
    st.info("ℹ️ Cadastre os dados da empresa na página inicial para obter sugestões mais precisas da IA.")

# ========== BOTÕES DE AÇÃO ==========
st.subheader("🚀 Ações com IA")

col_gerar1, col_gerar2, col_gerar3 = st.columns([3, 1, 1])
with col_gerar1:
    st.caption("A IA vai analisar suas informações e gerar conteúdo para todos os 9 blocos do BMC")
with col_gerar2:
    gerar_bmc = st.button("🔄 Gerar BMC Completo", use_container_width=True)
with col_gerar3:
    limpar_bmc = st.button("🗑️ Limpar BMC", use_container_width=True, help="Remove todo o conteúdo do BMC")
    
    if limpar_bmc:
        for chave, _, _, _ in BLOCOS:
            data["bmc"][chave] = []
        if "bmc_info" in data:
            data["bmc_info"] = {}
        st.rerun()

# Processar geração do BMC
if gerar_bmc:
    if not descricao_negocio and not empresa_nome:
        st.warning("⚠️ Por favor, preencha pelo menos a descrição do negócio ou o nome da empresa.")
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
                Cada bloco deve conter uma lista de itens (mínimo 3 itens por bloco).
                
                FORMATO DE SAÍDA (OBRIGATÓRIO): Retorne APENAS um JSON com os seguintes campos:
                {{
                    "proposta_valor": ["item1", "item2", "item3"],
                    "segmentos_clientes": ["item1", "item2", "item3"],
                    "canais": ["item1", "item2", "item3"],
                    "relacionamento_clientes": ["item1", "item2", "item3"],
                    "parcerias_chave": ["item1", "item2", "item3"],
                    "atividades_chave": ["item1", "item2", "item3"],
                    "recursos_chave": ["item1", "item2", "item3"],
                    "estrutura_custos": ["item1", "item2", "item3"],
                    "fontes_receita": ["item1", "item2", "item3"]
                }}
                
                Cada item deve ser uma frase curta e objetiva em português do Brasil.
                Responda APENAS com o JSON, sem texto adicional.
                """
                
                response = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[
                        {"role": "system", "content": "Você é um consultor sênior de estratégia. Responda em português do Brasil. Retorne APENAS JSON válido."},
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
                    
                    blocos_atualizados = 0
                    for chave, _, _, _ in BLOCOS:
                        if chave in dados and dados[chave]:
                            if not data["bmc"].get(chave, []):
                                data["bmc"][chave] = dados[chave]
                                blocos_atualizados += 1
                    
                    if blocos_atualizados > 0:
                        st.success(f"✅ {blocos_atualizados} blocos do BMC foram preenchidos pela IA!")
                        st.rerun()
                    else:
                        st.info("ℹ️ Todos os blocos já estão preenchidos. Use 'Limpar BMC' para recomeçar.")
                        
                except json.JSONDecodeError as e:
                    st.error(f"❌ Erro ao parsear resposta da IA: {str(e)}")
                    st.code(conteudo)
                    
            except Exception as e:
                st.error(f"❌ Erro ao gerar BMC: {str(e)}")

st.divider()

# ========== EXIBIÇÃO DOS BLOCOS COM DATA_EDITOR ==========
st.subheader("📝 Preencha os blocos do Business Model Canvas")

# Agrupar blocos para exibição no layout do Canvas
# Lado Esquerdo (Infraestrutura)
col_esquerda, col_centro, col_direita = st.columns([1, 1.5, 1])

with col_esquerda:
    st.markdown("### 🏗️ Infraestrutura")
    
    for chave, titulo, desc, placeholder in BLOCOS:
        if chave in ["parcerias_chave", "atividades_chave", "recursos_chave"]:
            st.markdown(f"**{titulo}**")
            st.caption(desc)
            
            # Garantir que a chave existe
            if "bmc" not in data:
                data["bmc"] = {}
            if chave not in data["bmc"]:
                data["bmc"][chave] = []
            
            # Criar DataFrame
            itens = data["bmc"].get(chave, [])
            df = pd.DataFrame(itens, columns=["item"]) if itens else pd.DataFrame(columns=["item"])
            
            # Hash para forçar recriação
            df_hash = hash(str(sorted([str(item) for item in itens]))) if itens else 0
            editor_key = f"bmc_editor_{chave}_{df_hash}"
            
            edited = st.data_editor(
                df,
                num_rows="dynamic",
                use_container_width=True,
                hide_index=True,
                key=editor_key,
                column_config={
                    "item": st.column_config.TextColumn("Item", width="large", placeholder=placeholder)
                },
                height=150
            )
            
            # Processar dados editados
            if edited is not None:
                edited = edited.fillna("")
                novos_itens = []
                for _, row in edited.iterrows():
                    item = str(row.get("item", "")).strip()
                    if item:
                        novos_itens.append(item)
                
                if novos_itens != data["bmc"].get(chave, []):
                    data["bmc"][chave] = novos_itens
                    st.rerun()
            
            # Botão para sugerir com IA
            if st.button(f"🤖 Sugerir {titulo.split(' ')[1] if len(titulo.split(' ')) > 1 else ''}", key=f"sugerir_{chave}", use_container_width=True):
                with st.spinner(f"Gerando sugestão para {titulo}..."):
                    try:
                        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"], base_url="https://openrouter.ai/api/v1")
                        
                        prompt_individual = f"""
                        INFORMAÇÕES DA EMPRESA:
                        - Nome: {empresa_nome}
                        - Setor: {empresa_setor}
                        - Descrição: {descricao_negocio or "Não informado"}
                        - Diferenciais: {diferenciais or "Não informado"}
                        - Público-alvo: {publico_alvo or "Não informado"}
                        
                        Bloco do BMC: {titulo}
                        Descrição: {desc}
                        
                        Gere uma lista de 3-5 itens para este bloco.
                        Responda APENAS com um JSON no formato: {{"itens": ["item1", "item2", "item3"]}}
                        """
                        
                        response = client.chat.completions.create(
                            model="openai/gpt-oss-20b",
                            messages=[
                                {"role": "system", "content": "Você é um consultor sênior de estratégia. Responda APENAS com JSON válido."},
                                {"role": "user", "content": prompt_individual}
                            ],
                            temperature=0.7
                        )
                        
                        sugestao = response.choices[0].message.content
                        
                        try:
                            json_match = re.search(r'\{.*\}', sugestao, re.DOTALL)
                            if json_match:
                                dados = json.loads(json_match.group())
                                novos_itens = dados.get("itens", [])
                                if novos_itens:
                                    # Mesclar com itens existentes
                                    existentes = data["bmc"].get(chave, [])
                                    existentes_what = set([str(item).lower().strip() for item in existentes])
                                    for item in novos_itens:
                                        if str(item).lower().strip() not in existentes_what:
                                            existentes.append(item)
                                    data["bmc"][chave] = existentes
                                    st.rerun()
                        except:
                            st.error("Erro ao processar sugestão")
                            
                    except Exception as e:
                        st.error(f"❌ Erro: {str(e)}")
            
            st.markdown("---")

with col_centro:
    st.markdown("### 💎 Proposta de Valor")
    
    for chave, titulo, desc, placeholder in BLOCOS:
        if chave == "proposta_valor":
            st.caption(desc)
            
            if "bmc" not in data:
                data["bmc"] = {}
            if chave not in data["bmc"]:
                data["bmc"][chave] = []
            
            itens = data["bmc"].get(chave, [])
            df = pd.DataFrame(itens, columns=["item"]) if itens else pd.DataFrame(columns=["item"])
            
            df_hash = hash(str(sorted([str(item) for item in itens]))) if itens else 0
            editor_key = f"bmc_editor_{chave}_{df_hash}"
            
            edited = st.data_editor(
                df,
                num_rows="dynamic",
                use_container_width=True,
                hide_index=True,
                key=editor_key,
                column_config={
                    "item": st.column_config.TextColumn("Item", width="large", placeholder=placeholder)
                },
                height=250
            )
            
            if edited is not None:
                edited = edited.fillna("")
                novos_itens = []
                for _, row in edited.iterrows():
                    item = str(row.get("item", "")).strip()
                    if item:
                        novos_itens.append(item)
                
                if novos_itens != data["bmc"].get(chave, []):
                    data["bmc"][chave] = novos_itens
                    st.rerun()
            
            if st.button(f"🤖 Sugerir {titulo.split(' ')[1] if len(titulo.split(' ')) > 1 else ''}", key=f"sugerir_{chave}", use_container_width=True):
                with st.spinner(f"Gerando sugestão..."):
                    try:
                        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"], base_url="https://openrouter.ai/api/v1")
                        
                        prompt_individual = f"""
                        Empresa: {empresa_nome}
                        Setor: {empresa_setor}
                        Descrição: {descricao_negocio or "Não informado"}
                        Diferenciais: {diferenciais or "Não informado"}
                        Público-alvo: {publico_alvo or "Não informado"}
                        
                        Bloco: {titulo}
                        Descrição: {desc}
                        
                        Gere 3-5 itens para a Proposta de Valor.
                        Responda APENAS JSON: {{"itens": ["item1", "item2", "item3"]}}
                        """
                        
                        response = client.chat.completions.create(
                            model="openai/gpt-oss-20b",
                            messages=[
                                {"role": "system", "content": "Responda APENAS com JSON válido."},
                                {"role": "user", "content": prompt_individual}
                            ],
                            temperature=0.7
                        )
                        
                        sugestao = response.choices[0].message.content
                        
                        try:
                            json_match = re.search(r'\{.*\}', sugestao, re.DOTALL)
                            if json_match:
                                dados = json.loads(json_match.group())
                                novos_itens = dados.get("itens", [])
                                if novos_itens:
                                    existentes = data["bmc"].get(chave, [])
                                    existentes_what = set([str(item).lower().strip() for item in existentes])
                                    for item in novos_itens:
                                        if str(item).lower().strip() not in existentes_what:
                                            existentes.append(item)
                                    data["bmc"][chave] = existentes
                                    st.rerun()
                        except:
                            st.error("Erro ao processar sugestão")
                            
                    except Exception as e:
                        st.error(f"❌ Erro: {str(e)}")
            
            st.markdown("---")
    
    st.markdown("### 📡 Canais e Relacionamento")
    
    for chave, titulo, desc, placeholder in BLOCOS:
        if chave in ["canais", "relacionamento_clientes"]:
            st.markdown(f"**{titulo}**")
            st.caption(desc)
            
            if "bmc" not in data:
                data["bmc"] = {}
            if chave not in data["bmc"]:
                data["bmc"][chave] = []
            
            itens = data["bmc"].get(chave, [])
            df = pd.DataFrame(itens, columns=["item"]) if itens else pd.DataFrame(columns=["item"])
            
            df_hash = hash(str(sorted([str(item) for item in itens]))) if itens else 0
            editor_key = f"bmc_editor_{chave}_{df_hash}"
            
            edited = st.data_editor(
                df,
                num_rows="dynamic",
                use_container_width=True,
                hide_index=True,
                key=editor_key,
                column_config={
                    "item": st.column_config.TextColumn("Item", width="large", placeholder=placeholder)
                },
                height=120
            )
            
            if edited is not None:
                edited = edited.fillna("")
                novos_itens = []
                for _, row in edited.iterrows():
                    item = str(row.get("item", "")).strip()
                    if item:
                        novos_itens.append(item)
                
                if novos_itens != data["bmc"].get(chave, []):
                    data["bmc"][chave] = novos_itens
                    st.rerun()
            
            if st.button(f"🤖 Sugerir {titulo.split(' ')[1] if len(titulo.split(' ')) > 1 else ''}", key=f"sugerir_{chave}", use_container_width=True):
                # Similar ao anterior
                pass
            
            st.markdown("---")

with col_direita:
    st.markdown("### 👥 Clientes")
    
    for chave, titulo, desc, placeholder in BLOCOS:
        if chave == "segmentos_clientes":
            st.caption(desc)
            
            if "bmc" not in data:
                data["bmc"] = {}
            if chave not in data["bmc"]:
                data["bmc"][chave] = []
            
            itens = data["bmc"].get(chave, [])
            df = pd.DataFrame(itens, columns=["item"]) if itens else pd.DataFrame(columns=["item"])
            
            df_hash = hash(str(sorted([str(item) for item in itens]))) if itens else 0
            editor_key = f"bmc_editor_{chave}_{df_hash}"
            
            edited = st.data_editor(
                df,
                num_rows="dynamic",
                use_container_width=True,
                hide_index=True,
                key=editor_key,
                column_config={
                    "item": st.column_config.TextColumn("Item", width="large", placeholder=placeholder)
                },
                height=200
            )
            
            if edited is not None:
                edited = edited.fillna("")
                novos_itens = []
                for _, row in edited.iterrows():
                    item = str(row.get("item", "")).strip()
                    if item:
                        novos_itens.append(item)
                
                if novos_itens != data["bmc"].get(chave, []):
                    data["bmc"][chave] = novos_itens
                    st.rerun()
            
            if st.button(f"🤖 Sugerir {titulo.split(' ')[1] if len(titulo.split(' ')) > 1 else ''}", key=f"sugerir_{chave}", use_container_width=True):
                pass
            
            st.markdown("---")
    
    st.markdown("### 💰 Finanças")
    
    for chave, titulo, desc, placeholder in BLOCOS:
        if chave in ["estrutura_custos", "fontes_receita"]:
            st.markdown(f"**{titulo}**")
            st.caption(desc)
            
            if "bmc" not in data:
                data["bmc"] = {}
            if chave not in data["bmc"]:
                data["bmc"][chave] = []
            
            itens = data["bmc"].get(chave, [])
            df = pd.DataFrame(itens, columns=["item"]) if itens else pd.DataFrame(columns=["item"])
            
            df_hash = hash(str(sorted([str(item) for item in itens]))) if itens else 0
            editor_key = f"bmc_editor_{chave}_{df_hash}"
            
            edited = st.data_editor(
                df,
                num_rows="dynamic",
                use_container_width=True,
                hide_index=True,
                key=editor_key,
                column_config={
                    "item": st.column_config.TextColumn("Item", width="large", placeholder=placeholder)
                },
                height=120
            )
            
            if edited is not None:
                edited = edited.fillna("")
                novos_itens = []
                for _, row in edited.iterrows():
                    item = str(row.get("item", "")).strip()
                    if item:
                        novos_itens.append(item)
                
                if novos_itens != data["bmc"].get(chave, []):
                    data["bmc"][chave] = novos_itens
                    st.rerun()
            
            st.markdown("---")

st.divider()

# ========== VISUALIZAÇÃO COMPLETA DO CANVAS ==========
st.subheader("📊 Visualização Completa do Business Model Canvas")

# Criar um DataFrame com todos os blocos
canvas_data = {}
for chave, titulo, desc, placeholder in BLOCOS:
    itens = data["bmc"].get(chave, [])
    canvas_data[titulo] = "\n".join([f"• {item}" for item in itens]) if itens else "_(vazio)_"

df_canvas = pd.DataFrame([canvas_data]).T
df_canvas.columns = ["Conteúdo"]

st.dataframe(
    df_canvas,
    use_container_width=True,
    height=400,
    column_config={
        "Conteúdo": st.column_config.TextColumn("Conteúdo", width="large")
    }
)

# Botão para copiar ou exportar
col_export1, col_export2 = st.columns(2)
with col_export1:
    if st.button("📋 Copiar Canvas (Texto)", use_container_width=True):
        texto = "BUSINESS MODEL CANVAS\n" + "="*50 + "\n\n"
        for chave, titulo, desc, placeholder in BLOCOS:
            itens = data["bmc"].get(chave, [])
            texto += f"{titulo}:\n"
            if itens:
                for item in itens:
                    texto += f"  • {item}\n"
            else:
                texto += "  (vazio)\n"
            texto += "\n"
        st.code(texto, language="markdown")
        
with col_export2:
    if st.button("⬇️ Baixar Canvas (JSON)", use_container_width=True):
        json_str = json.dumps(data["bmc"], indent=2, ensure_ascii=False)
        st.download_button(
            "📥 Baixar JSON",
            data=json_str,
            file_name="business_model_canvas.json",
            mime="application/json",
            use_container_width=True
        )

st.success("✅ Todos os blocos são salvos automaticamente. Use a página 'Relatório Completo' para exportar tudo.")

# ========== ASSISTENTE IA PARA AJUDA ==========
st.divider()
st.subheader("💬 Assistente IA - Ajuda com o Business Model Canvas")

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
            
            bmc_atual = ""
            for chave, titulo, _, _ in BLOCOS:
                itens = data["bmc"].get(chave, [])
                if itens:
                    bmc_atual += f"\n{titulo}:\n"
                    for item in itens:
                        bmc_atual += f"  • {item}\n"
            
            mensagens = [
                {"role": "system", "content": f"""Você é um assistente especializado em Business Model Canvas.

EMPRESA: {empresa_nome}
SETOR: {empresa_setor}
DESCRIÇÃO: {descricao_negocio or 'Não informado'}

BMC ATUAL:
{bmc_atual or 'Nenhum bloco preenchido'}

Responda em português do Brasil, de forma prática e objetiva."""}
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
            st.error(f"❌ Erro: {str(e)}")
