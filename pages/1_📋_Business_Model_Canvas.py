import streamlit as st
import json
import re
import pandas as pd
from openai import OpenAI

from utils.data_manager import init_data, get_data, sidebar_data_controls
from utils.chat import render_chat

st.set_page_config(
    page_title="Business Model Canvas",
    page_icon="📋",
    layout="wide"
)

init_data()
data = get_data()

# ---------- Barra lateral ----------
st.sidebar.title("🧭 Gestor Estratégico")
sidebar_data_controls()

# ---------- Título ----------
st.title("📋 Business Model Canvas")
st.caption(
    "Preencha os 9 blocos do seu modelo de negócio seguindo a estrutura do Canvas. "
    "Cada bloco pode ter múltiplos itens."
)

# ========== DEFINIÇÃO DOS BLOCOS ==========
BLOCOS = [
    ("proposta_valor", "💎 Proposta de Valor",
     "Que problema você resolve? Que valor entrega ao cliente?"),

    ("segmentos_clientes", "🎯 Segmentos de Clientes",
     "Para quem vocês criam valor? Quem são os clientes mais importantes?"),

    ("canais", "📡 Canais",
     "Como a proposta de valor chega até o cliente (comunicação, venda, entrega)?"),

    ("relacionamento_clientes", "❤️ Relacionamento com Clientes",
     "Como vocês conquistam, mantêm e fazem crescer a base de clientes?"),

    ("parcerias_chave", "🤝 Parcerias-Chave",
     "Quem são seus principais fornecedores e parceiros? O que vocês trocam?"),

    ("atividades_chave", "⚙️ Atividades-Chave",
     "Quais atividades essenciais sua proposta de valor exige?"),

    ("recursos_chave", "🧱 Recursos-Chave",
     "Que recursos (físicos, humanos, financeiros, intelectuais) são indispensáveis?"),

    ("estrutura_custos", "💸 Estrutura de Custos",
     "Quais são os custos mais importantes do modelo de negócio?"),

    ("fontes_receita", "💰 Fontes de Receita",
     "Por qual valor os clientes estão dispostos a pagar, e como pagam?"),
]

# Garantir estrutura inicial
if "bmc" not in data:
    data["bmc"] = {}

for chave, _, _ in BLOCOS:
    if chave not in data["bmc"]:
        data["bmc"][chave] = []


# ========== INFORMAÇÕES ADICIONAIS ==========
with st.expander(
    "📋 Informações para o Business Model Canvas",
    expanded=False
):

    st.markdown(
        "**Preencha as informações abaixo para ajudar a IA "
        "a gerar sugestões mais precisas:**"
    )

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
            placeholder=(
                "Ex: Tecnologia proprietária, equipe especializada, "
                "parcerias exclusivas..."
            ),
            height=80,
            key="bmc_diferenciais"
        )

    with col_info2:
        publico_alvo = st.text_area(
            "🎯 Público-alvo",
            value=data["bmc_info"].get("publico_alvo", ""),
            placeholder=("Ex: Pequenas empresas, consumidores finais, indústrias..."),
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

    # Salvamento automático
    data["bmc_info"]["descricao"] = descricao_negocio
    data["bmc_info"]["diferenciais"] = diferenciais
    data["bmc_info"]["publico_alvo"] = publico_alvo
    data["bmc_info"]["observacoes"] = observacoes_bmc

st.divider()
# ========== INFORMAÇÕES DA EMPRESA ==========
empresa = data.get("empresa", {})
empresa_nome = empresa.get("nome", "").strip()
empresa_setor = empresa.get("setor", "").strip()
empresa_cidade = empresa.get("cidade_estado", "").strip()
empresa_responsavel = empresa.get("responsavel", "").strip()


if not empresa_nome:
    st.warning(
        "⚠️ Cadastre os dados da empresa na página inicial "
        "para obter sugestões mais precisas da IA.",
        icon="⚠️"
    )

# ========== BOTÕES DE AÇÃO COM IA ==========

st.subheader("🚀 Ações com IA")

col_gerar1, col_gerar2, col_gerar3 = st.columns([3, 1, 1])

with col_gerar1:
    st.caption(
        "A IA vai analisar suas informações e gerar conteúdo "
        "para todos os 9 blocos do BMC."
    )

with col_gerar2:
    gerar_bmc = st.button(
        "🔄 Gerar BMC Completo",
        width="stretch"
    )

with col_gerar3:
    limpar_bmc = st.button(
        "🗑️ Limpar BMC",
        width="stretch",
        help="Remove todo o conteúdo do BMC"
    )

if limpar_bmc:
    for chave, _, _ in BLOCOS:
        data["bmc"][chave] = []
    data["bmc_info"] = {}
    st.success("✅ Business Model Canvas limpo!")
    st.rerun()

# ========== GERAR BMC COM IA ==========
if gerar_bmc:
    if not descricao_negocio and not empresa_nome:
        st.warning(
            "⚠️ Informe pelo menos a descrição do negócio "
            "ou o nome da empresa."
        )

    else:
        with st.spinner("🧠 Gerando Business Model Canvas com IA..."):
            try:
                client = OpenAI(
                    api_key=st.secrets["OPENAI_API_KEY"],
                    base_url="https://openrouter.ai/api/v1"
                )
                prompt = f"""

Você é um consultor sênior de estratégia especializado
em Business Model Canvas.

INFORMAÇÕES DA EMPRESA:

Nome: {empresa_nome or "Não informado"}

Setor: {empresa_setor or "Não informado"}

Cidade: {empresa_cidade or "Não informado"}

Responsável: {empresa_responsavel or "Não informado"}

Descrição: {descricao_negocio or "Não informado"}

Diferenciais: {diferenciais or "Não informado"}

Público-alvo: {publico_alvo or "Não informado"}

Observações: {observacoes_bmc or "Não informado"}


Preencha os 9 blocos do Business Model Canvas.

Cada bloco deve possuir pelo menos 3 itens.

Retorne APENAS JSON válido:

{{
"proposta_valor": [],
"segmentos_clientes": [],
"canais": [],
"relacionamento_clientes": [],
"parcerias_chave": [],
"atividades_chave": [],
"recursos_chave": [],
"estrutura_custos": [],
"fontes_receita": []
}}

Cada item deve ser uma frase curta e objetiva.
"""
                response = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[
                        {
                            "role": "system",
                            "content":
                            "Você é um consultor especialista em estratégia. "
                            "Retorne somente JSON válido."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.7
                )

                conteudo = response.choices[0].message.content
                json_match = re.search(
                    r'\{.*\}',
                    conteudo,
                    re.DOTALL
                )

                if json_match:
                    dados = json.loads(
                        json_match.group()
                    )

                else:
                    dados = json.loads(conteudo)

                atualizados = 0

                for chave, _, _ in BLOCOS:
                    if (
                        chave in dados
                        and isinstance(dados[chave], list)
                        and dados[chave]
                    ):
                        data["bmc"][chave] = dados[chave]
                        atualizados += 1

                if atualizados:
                    st.success(f"✅ {atualizados} blocos preenchidos pela IA!")
                    st.rerun()

                else:
                    st.warning("⚠️ A IA não retornou dados válidos.")

            except Exception as e:
                st.error(f"❌ Erro ao gerar BMC: {str(e)}")

st.divider()

# ========== EXIBIÇÃO DOS BLOCOS ==========
st.subheader("📝 Preencha os blocos do Business Model Canvas")

def render_bloco(
    chave,
    titulo,
    descricao,
    altura=150
):
    st.markdown(f"**{titulo}**")
    st.caption(descricao)
    itens = data["bmc"].get(chave,[])


    if itens:
        df = pd.DataFrame({"item": itens})

    else:
        df = pd.DataFrame(columns=["item"])

    df_hash = hash(str(itens))

    edited = st.data_editor(
        df,
        num_rows="dynamic",
        width="stretch",
        hide_index=True,
        height=altura,
        key=f"bmc_editor_{chave}_{df_hash}",

        column_config={
            "item":
            st.column_config.TextColumn(
                "Item",
                width="large"
            )
        }
    )

    if edited is not None:
        novos = []
        for _, row in edited.iterrows():
            item = str(row.get("item", "")).strip()
            if item:
                novos.append(item)
        if novos != data["bmc"].get(chave, []):
            data["bmc"][chave] = novos
            st.rerun()

    if st.button("🤖 Sugerir", key=f"sugerir_{chave}", width="stretch"):
        with st.spinner(f"Gerando sugestão para {titulo}..."):
            try:
                client = OpenAI(
                    api_key=st.secrets["OPENAI_API_KEY"],
                    base_url="https://openrouter.ai/api/v1"
                )
                prompt = f"""

Empresa: {empresa_nome}

Setor: {empresa_setor}

Descrição: {descricao_negocio or "Não informado"}

Bloco: {titulo}

Descrição do bloco: {descricao}

Gere 3 a 5 sugestões práticas.

Responda APENAS JSON:

{{"itens":["item1","item2","item3"]}}
"""

                response = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[
                        {
                            "role":"system",
                            "content":
                            "Retorne somente JSON válido."
                        },
                        {
                            "role":"user",
                            "content":prompt
                        }
                    ],
                    temperature=0.7
                )

                resposta = response.choices[0].message.content
                json_match = re.search(
                    r'\{.*\}',
                    resposta,
                    re.DOTALL
                )

                dados = json.loads(
                    json_match.group()
                    if json_match
                    else resposta
                )

                existentes = data["bmc"][chave]

                adicionados = 0

                for item in dados.get("itens", []):
                    if item not in existentes:
                        existentes.append(item)
                        adicionados += 1

                if adicionados:
                    data["bmc"][chave] = existentes
                    st.success(f"✅ {adicionados} itens adicionados.")
                    st.rerun()

            except Exception as e:
                st.error(f"❌ Erro: {str(e)}")

# ========== LAYOUT DO CANVAS ==========
col_esquerda, col_centro, col_direita = st.columns([1, 1.2, 1])
with col_esquerda:
    st.markdown("### 🏗️ Infraestrutura")
    for chave, titulo, desc in BLOCOS:
        if chave in [
            "parcerias_chave",
            "atividades_chave",
            "recursos_chave"
        ]:
            render_bloco(
                chave,
                titulo,
                desc,
                150
            )

with col_centro:
    st.markdown("### 💎 Proposta de Valor")

    render_bloco(
        "proposta_valor",
        "💎 Proposta de Valor",
        "Que problema você resolve? Que valor entrega ao cliente?",
        250
    )

    st.markdown("### 📡 Canais e Relacionamento")

    for chave, titulo, desc in BLOCOS:
        if chave in [
            "canais",
            "relacionamento_clientes"
        ]:
            render_bloco(
                chave,
                titulo,
                desc,
                150
            )

with col_direita:
    st.markdown("### 👥 Clientes")
    render_bloco(
        "segmentos_clientes",
        "🎯 Segmentos de Clientes",
        "Para quem vocês criam valor?",
        200
    )

    st.markdown("### 💰 Finanças")

    for chave, titulo, desc in BLOCOS:
        if chave in [
            "estrutura_custos",
            "fontes_receita"
        ]:

            render_bloco(
                chave,
                titulo,
                desc,
                150
            )

st.divider()

# ========== VISUALIZAÇÃO COMPLETA ==========
st.subheader("📊 Visualização Completa do Business Model Canvas")
canvas_data = {}

for chave, titulo, desc in BLOCOS:
    itens = data["bmc"].get(chave,[])

    if itens:
        canvas_data[titulo] = "\n".join(
            [
                f"• {item}"
                for item in itens
            ]
        )
    else:
        canvas_data[titulo] = "_(vazio)_"

df_canvas = pd.DataFrame(
    list(canvas_data.items()),
    columns=[
        "Bloco",
        "Conteúdo"
    ]
)

st.dataframe(
    df_canvas,
    width="stretch",
    height=400,
    hide_index=True,
    column_config={
        "Bloco":
        st.column_config.TextColumn(
            "Bloco",
            width="medium"
        ),
        "Conteúdo":
        st.column_config.TextColumn(
            "Conteúdo",
            width="large"
        )
    }
)

# ========== EXPORTAÇÃO ==========
col_export1, col_export2 = st.columns(2)

with col_export1:
    if st.button(
        "📋 Copiar Canvas (Texto)",
        width="stretch"
    ):
        texto = (
            "BUSINESS MODEL CANVAS\n"
            + "=" * 50
            + "\n\n"
        )

        for chave, titulo, desc in BLOCOS:
            texto += f"{titulo}:\n"
            itens = data["bmc"].get(chave,[])
            if itens:
                for item in itens:
                    texto += f"• {item}\n"
            else:
                texto += "(vazio)\n"
            texto += "\n"
        st.code(texto, language="markdown")

with col_export2:
    if st.button(
        "⬇️ Baixar Canvas (JSON)",
        width="stretch"
    ):
        json_str = json.dumps(
            data["bmc"],
            indent=2,
            ensure_ascii=False
        )

        st.download_button(
            "📥 Baixar JSON",
            data=json_str,
            file_name="business_model_canvas.json",
            mime="application/json",
            width="stretch"
        )
st.success("✅ Todos os blocos são salvos automaticamente.")

# ========== ASSISTENTE IA ==========
st.divider()
st.subheader("💬 Tem dúvidas? Consulte nosso Assistente IA")

bmc_atual = ""

for chave, titulo, desc in BLOCOS:
    itens = data["bmc"].get(chave,[])
    bmc_atual += f"\n{titulo}:\n"

    if itens:
        for item in itens:
            bmc_atual += f"• {item}\n"

    else:
        bmc_atual += "(vazio)\n"


contexto_bmc = f"""

SIPE - SISTEMA INTEGRADO DE PLANEJAMENTO ESTRATÉGICO

EMPRESA: {empresa_nome or "Não informada"}

SETOR: {empresa_setor or "Não informado"}

DESCRIÇÃO DO NEGÓCIO: {descricao_negocio or "Não informado"}

DIFERENCIAIS: {diferenciais or "Não informado"}

PÚBLICO-ALVO: {publico_alvo or "Não informado"}

BUSINESS MODEL CANVAS ATUAL: {bmc_atual}
"""

system_prompt_bmc = """

Você é um consultor especialista em Business Model Canvas.

Ajude o usuário a analisar, melhorar e completar seu modelo de negócio.

Considere os 9 blocos:

- Proposta de Valor
- Segmentos de Clientes
- Canais
- Relacionamento com Clientes
- Parcerias-Chave
- Atividades-Chave
- Recursos-Chave
- Estrutura de Custos
- Fontes de Receita


Sempre utilize as informações atuais do Canvas.

Responda em português do Brasil,
de forma prática e objetiva.
"""

render_chat(
    messages_key="messages_bmc",
    placeholder=
    "Pergunte ao assistente sobre seu Business Model Canvas...",
    system_prompt=system_prompt_bmc,
    context=contexto_bmc
)

# ========== PRÓXIMA ETAPA ==========
st.divider()
col_prox1, col_prox2, col_prox3 = st.columns([1, 2, 1])

with col_prox2:
    if st.button(
        "➡️ Vamos para a Próxima Etapa? > Análise PESTEL", width="stretch"):
        st.switch_page("pages/2_🌍_Análise_PESTEL.py")
