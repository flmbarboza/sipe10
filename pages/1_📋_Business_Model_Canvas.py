import streamlit as st
from utils.data_manager import init_data, get_data, sidebar_data_controls
from utils.ai_helper import sidebar_api_key_input, ai_assist_widget

st.set_page_config(page_title="Business Model Canvas", page_icon="📋", layout="wide")
init_data()
data = get_data()

st.sidebar.title("🧭 Gestor Estratégico")
#sidebar_api_key_input()
sidebar_data_controls()

st.title("📋 Business Model Canvas")
st.caption("Preencha os 9 blocos do seu modelo de negócio. Edite livremente a qualquer momento.")

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

col_a, col_b, col_c = st.columns(3)
cols_map = {0: col_a, 1: col_a, 2: col_a, 3: col_b, 4: col_b, 5: col_b, 6: col_c, 7: col_c, 8: col_c}

for i, (chave, titulo, ajuda) in enumerate(BLOCOS):
    with cols_map[i]:
        st.markdown(f"#### {titulo}")
        valor = st.text_area(
            ajuda, value=data["bmc"].get(chave, ""), key=f"bmc_{chave}", height=140, label_visibility="visible"
        )
        data["bmc"][chave] = valor

        def builder(instrucao, chave=chave, titulo=titulo, ajuda=ajuda):
            empresa = data["empresa"].get("nome") or "a empresa"
            setor = data["empresa"].get("setor") or "não informado"
            atual = data["bmc"].get(chave, "")
            base = (
                f"Empresa: {empresa}. Setor: {setor}.\n"
                f"Bloco do Business Model Canvas: {titulo}.\n"
                f"Pergunta-guia do bloco: {ajuda}\n"
                f"Conteúdo já escrito pelo usuário neste bloco: '{atual or '(vazio)'}'.\n"
            )
            if instrucao:
                base += f"Pedido específico do usuário: {instrucao}\n"
            else:
                base += "Sugira um texto objetivo para este bloco, com 3 a 5 bullets.\n"
            return base

        ai_assist_widget(f"bmc_{chave}", titulo, system_prompt(), builder)
        st.markdown("---")

st.success("As alterações são salvas automaticamente na sessão. Não esqueça de baixar o JSON na barra lateral.")
