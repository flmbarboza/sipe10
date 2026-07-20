import streamlit as st
import pandas as pd
import json
import re
from openai import OpenAI
from utils.data_manager import init_data, get_data, sidebar_data_controls
from utils.chat import render_chat

# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================
st.set_page_config(page_title="Business Model Canvas",page_icon="📋",layout="wide")

init_data()
data = get_data()

st.sidebar.title("🧭 Gestor Estratégico")
sidebar_data_controls()

# ============================================================
# TÍTULO
# ============================================================
st.title("📋 Business Model Canvas")
st.caption(
    "Construa seu modelo de negócio passo a passo. "
    "O SIPE irá guiá-lo desde a identificação dos clientes até a estrutura financeira."
)

# ============================================================
# INICIALIZAÇÃO DOS DADOS
# ============================================================
if "bmc" not in data:
    data["bmc"] = {}
if "bmc_etapa" not in st.session_state:
    st.session_state.bmc_etapa = 0

# ============================================================
# ORDEM GUIADA DO CANVAS
# ============================================================
ETAPAS_BMC = [
    {
        "chave": "segmentos_clientes",
        "titulo": "🎯 Segmentos de Clientes",
        "pergunta": "Quem são as pessoas ou organizações que compram sua solução?",
        "explicacao": """
Os clientes são o ponto de partida do modelo de negócio.

Identifique:
- Quem compra seu produto ou serviço?
- Quem utiliza sua solução?
- Existem diferentes grupos de clientes?
""",
        "exemplos": ["Consumidores finais","Pequenas empresas","Indústrias","Órgãos públicos"]
    },

    {
        "chave": "proposta_valor",
        "titulo": "💎 Proposta de Valor",
        "pergunta": "Qual problema você resolve e qual valor entrega ao cliente?",
        "explicacao": """
A proposta de valor explica por que o cliente escolhe sua empresa.

Pense:
- Qual necessidade você atende?
- Que benefício entrega?
- O que diferencia sua solução?
""",
        "exemplos": ["Preço acessível","Maior qualidade","Conveniência","Experiência diferenciada"]
    },

    {
        "chave": "canais",
        "titulo": "📡 Canais",
        "pergunta": "Como o cliente encontra, compra e recebe sua solução?",
        "explicacao": """
Os canais representam os meios utilizados para chegar até o cliente.

Considere:
- Divulgação
- Venda
- Entrega
- Atendimento
""",
        "exemplos": ["Loja física","Instagram","Site","WhatsApp"]
    },

    {
        "chave": "relacionamento_clientes",
        "titulo": "❤️ Relacionamento com Clientes",
        "pergunta": "Como sua empresa conquista e mantém clientes?",
        "explicacao": """
Defina como será a interação com seus clientes.

Exemplos:
- Atendimento personalizado
- Programa de fidelidade
- Comunidade
- Suporte pós-venda
""",
        "exemplos": ["Atendimento personalizado","Programa de fidelidade","Pós-venda"]
    },

    {
        "chave": "fontes_receita",
        "titulo": "💰 Fontes de Receita",
        "pergunta": "Como sua empresa gera receita?",
        "explicacao": """
Aqui descrevemos como o negócio transforma valor entregue em dinheiro.

Considere:
- O que o cliente paga?
- Como paga?
- Qual modelo de cobrança?
""",
        "exemplos": ["Venda direta","Assinatura mensal","Comissão","Licenciamento"]
    },

    {
        "chave": "recursos_chave",
        "titulo": "🧱 Recursos-Chave",
        "pergunta": "Quais recursos são necessários para o negócio funcionar?",
        "explicacao": """
São os recursos indispensáveis para entregar sua proposta de valor.

Podem ser:
- Pessoas
- Equipamentos
- Tecnologia
- Marca
- Capital
""",
        "exemplos": ["Equipe especializada","Máquinas","Sistema de gestão"]
    },

    {
        "chave": "atividades_chave",
        "titulo": "⚙️ Atividades-Chave",
        "pergunta": "Quais atividades precisam ser realizadas?",
        "explicacao": """
São as principais ações que fazem o modelo funcionar.

Exemplos:
- Produção
- Desenvolvimento
- Atendimento
- Logística
""",
        "exemplos": ["Produção","Marketing","Entrega"]
    },

    {
        "chave": "parcerias_chave",
        "titulo": "🤝 Parcerias-Chave",
        "pergunta": "Quem são os parceiros importantes para o negócio?",
        "explicacao": """
Empresas e pessoas que ajudam seu negócio a funcionar melhor.

Exemplos:
- Fornecedores
- Distribuidores
- Parceiros estratégicos
""",
        "exemplos": ["Fornecedores","Representantes","Parceiros comerciales"]
    },
    {
        "chave": "estrutura_custos",
        "titulo": "💸 Estrutura de Custos",
        "pergunta": "Quais são os principais custos do negócio?",
        "explicacao": """
Liste os principais gastos necessários para operar.

Considere:
- Custos fixos
- Custos variáveis
- Investimentos
""",
        "exemplos": ["Salários", "Aluguel", "Matéria-prima"]
    }
]

# ============================================================
# FUNÇÃO PARA GARANTIR ESTRUTURA DOS DADOS
# ============================================================
def garantir_bloco(chave):
    if chave not in data["bmc"]:
        data["bmc"][chave] = []
    if not isinstance(data["bmc"][chave], list):
        data["bmc"][chave] = []

# ============================================================
# ETAPA ATUAL DO CANVAS
# ============================================================
etapa_atual = st.session_state.bmc_etapa
etapa = ETAPAS_BMC[etapa_atual]
chave = etapa["chave"]
garantir_bloco(chave)

# ============================================================
# BARRA DE PROGRESSO
# ============================================================
progresso = (etapa_atual + 1) / len(ETAPAS_BMC)
st.progress(progresso,text=f"Etapa {etapa_atual + 1} de {len(ETAPAS_BMC)}")

st.divider()

# ============================================================
# TÍTULO DA ETAPA
# ============================================================
st.header(etapa["titulo"])
st.markdown(
    f"""
### 🤔 Pergunta principal

**{etapa["pergunta"]}**
"""
)

# ============================================================
# EXPLICAÇÃO DIDÁTICA
# ============================================================
with st.expander("💡 Entenda esta etapa", expanded=True):
    st.markdown(etapa["explicacao"])

with st.expander("📌 Exemplos", expanded=False):
    for exemplo in etapa["exemplos"]:
        st.markdown(f"- {exemplo}")

st.divider()

# ============================================================
# ÁREA DE PREENCHIMENTO
# ============================================================
st.subheader("✍️ Construa sua resposta")
itens_atuais = data["bmc"].get(chave, [])

if not itens_atuais:
    itens_atuais = [""]

novos_itens = []
for i, item in enumerate(itens_atuais):
    valor = st.text_input(f"Item {i+1}", value=item, key=f"bmc_{chave}_{i}")
    if valor.strip():
        novos_itens.append(valor.strip())

if novos_itens != data["bmc"].get(chave, []):
    data["bmc"][chave] = novos_itens

# ============================================================
# ADICIONAR NOVO ITEM
# ============================================================
if st.button("➕ Adicionar outro item",key=f"add_{chave}"):
    data["bmc"][chave].append("")
    st.rerun()

# ============================================================
# AJUDA DA IA - GERAR SUGESTÕES
# ============================================================
st.divider()
col_ia1, col_ia2 = st.columns([3,1])
with col_ia1:
    st.info(
        "💡 Use a IA para gerar sugestões para este bloco. "
        "As sugestões serão inseridas automaticamente para você revisar."
    )
with col_ia2:
    gerar_sugestao = st.button("🤖 Gerar sugestões", width="stretch", key=f"ia_{chave}")

if gerar_sugestao:
    with st.spinner("🤔 Analisando o modelo de negócio..."):
        try:
            client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"], base_url="https://openrouter.ai/api/v1")
            
            empresa = data.get("empresa", {})
            empresa_nome = empresa.get("nome", "").strip()
            empresa_setor = empresa.get("setor", "").strip()
            empresa_cidade = empresa.get("cidade_estado", "").strip()
            
            contexto_empresa = f"""
            EMPRESA: {empresa_nome or "Não informado"}
            SETOR: {empresa_setor or "Não informado"}
            LOCALIZAÇÃO: {empresa_cidade or "Não informado"}
            """
            
            prompt_ia = f"""
            Você é um consultor especialista em Business Model Canvas.
            
            Bloco: {etapa["titulo"]}
            Pergunta orientadora: {etapa["pergunta"]}
            
            Contexto da empresa: {contexto_empresa}
            
            Gere de 3 a 5 sugestões práticas e realistas para este bloco.
            As sugestões devem ser respostas diretas à pergunta orientadora.
            
            Responda APENAS com um JSON no formato:
            {{"sugestoes": ["sugestão 1", "sugestão 2", "sugestão 3"]}}
            
            Responda em português do Brasil.
            """
            
            response = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {"role": "system", "content": "Você é um consultor experiente em estratégia empresarial e Business Model Canvas. Responda APENAS com JSON válido."},
                    {"role": "user", "content": prompt_ia}
                ],
                temperature=0.7
            )
            
            conteudo = response.choices[0].message.content
            json_match = re.search(r'\{.*\}', conteudo, re.DOTALL)
            if json_match:
                dados = json.loads(json_match.group())
                sugestoes = dados.get("sugestoes", [])
                
                if sugestoes:
                    # Inserir sugestões automaticamente
                    data["bmc"][chave] = sugestoes
                    st.success(f"✅ {len(sugestoes)} sugestões inseridas! Revise e edite abaixo.")
                    st.rerun()
                else:
                    st.warning("Nenhuma sugestão gerada. Tente novamente.")
            else:
                st.error("Erro ao processar a resposta da IA.")
                st.code(conteudo)
                
        except Exception as e:
            st.error(f"❌ Erro ao consultar IA: {str(e)}")

# ============================================================
# NAVEGAÇÃO
# ============================================================
st.divider()
col_voltar, col_meio, col_avancar = st.columns([1,2,1])
with col_voltar:
    if etapa_atual > 0:
        if st.button("⬅️ Voltar", width="stretch"):
            st.session_state.bmc_etapa -= 1
            st.rerun()

with col_avancar:
    if etapa_atual < len(ETAPAS_BMC)-1:
        if st.button("Próxima etapa ➡️",width="stretch"):
            st.session_state.bmc_etapa += 1
            st.rerun()
    else:
        if st.button("🎉 Finalizar Canvas", width="stretch"):
            st.session_state.bmc_finalizado = True
            st.rerun()

# ============================================================
# VISUALIZAÇÃO COMPLETA DO CANVAS
# ============================================================
st.divider()
st.header("📊 Visualização Completa do Business Model Canvas")
st.caption("Após construir cada etapa, visualize seu modelo de negócio completo.")

canvas_data = []
for bloco in ETAPAS_BMC:
    chave_bloco = bloco["chave"]
    itens = data["bmc"].get(chave_bloco, [])

    if itens:
        conteudo = "\n".join([f"• {item}" for item in itens if item.strip()])
    else:
        conteudo = "_(não preenchido)_"
    
    canvas_data.append({
        "Bloco": bloco["titulo"],
        "Conteúdo": conteudo
    })

df_canvas = pd.DataFrame(canvas_data)
st.dataframe(
    df_canvas,
    width="stretch",
    height=500,
    hide_index=True,
    column_config={
        "Bloco": st.column_config.TextColumn("Bloco", width="medium"),
        "Conteúdo": st.column_config.TextColumn("Conteúdo", width="large")
    }
)

# ============================================================
# EXPORTAÇÃO
# ============================================================
st.divider()
col_export1, col_export2 = st.columns(2)
with col_export1:
    texto_canvas = "BUSINESS MODEL CANVAS\n"
    texto_canvas += "=" * 40
    texto_canvas += "\n\n"

    for bloco in ETAPAS_BMC:
        titulo = bloco["titulo"]
        itens = data["bmc"].get(bloco["chave"], [])
        texto_canvas += f"{titulo}\n"
        if itens:
            for item in itens:
                texto_canvas += f"• {item}\n"
        else:
            texto_canvas += "(não preenchido)\n"
        texto_canvas += "\n"

    if st.button("📋 Mostrar Canvas em Texto", width="stretch"):
        st.code(texto_canvas, language="markdown")

with col_export2:
    json_canvas = json.dumps(data["bmc"], indent=2, ensure_ascii=False)
    st.download_button(
        "⬇️ Baixar Canvas (.json)",
        data=json_canvas,
        file_name="business_model_canvas.json",
        mime="application/json",
        width="stretch"
    )

# ============================================================
# ASSISTENTE IA GERAL DO CANVAS
# ============================================================
st.divider()
st.subheader("💬 Tem dúvidas? Consulte nosso Assistente IA sobre o Business Model Canvas")

empresa = data.get("empresa", {})
empresa_nome = empresa.get("nome", "").strip()

if not empresa_nome:
    st.warning("⚠️ Cadastre os dados da empresa para utilizar o assistente.")
else:
    contexto_canvas = ""
    for bloco in ETAPAS_BMC:
        itens = data["bmc"].get(bloco["chave"], [])
        contexto_canvas += f"\n{bloco['titulo']}:\n"
        for item in itens:
            contexto_canvas += f"- {item}\n"
    
    contexto = f"""
EMPRESA: {empresa_nome}
SETOR: {empresa.get("setor", "Não informado")}
BUSINESS MODEL CANVAS ATUAL: {contexto_canvas}
"""
    system_prompt = """
Você é um consultor especialista em Business Model Canvas.
Ajude o empreendedor a analisar, melhorar e questionar seu modelo de negócio.
Explique conceitos quando necessário.
Sugira melhorias práticas.
Responda sempre em português do Brasil,
com linguagem simples e objetiva.
"""
    render_chat(
        messages_key="messages_bmc",
        placeholder="Pergunte ao assistente sobre seu Canvas...",
        system_prompt=system_prompt,
        context=contexto
    )

# ========== BOTÃO PRÓXIMA ETAPA ==========
col_prox1, col_prox2, col_prox3 = st.columns([1, 2, 1])
with col_prox2:
    if st.button("➡️ Vamos para a Próxima Etapa? > Análise PESTEL", width="stretch"):
        st.switch_page("pages/2_🌍_Análise_PESTEL.py")
