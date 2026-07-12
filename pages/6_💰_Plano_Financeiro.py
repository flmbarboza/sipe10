import pandas as pd
import streamlit as st
from utils.data_manager import init_data, get_data, sidebar_data_controls
from utils.ai_helper import sidebar_api_key_input, ai_assist_widget

st.set_page_config(page_title="Plano Financeiro", page_icon="💰", layout="wide")
init_data()
data = get_data()

st.sidebar.title("🧭 Gestor Estratégico")
#sidebar_api_key_input()
sidebar_data_controls()

st.title("💰 Plano Financeiro")
st.caption("Estruture o investimento inicial, as receitas e os custos previstos para projetar o resultado do negócio.")

fin = data["financeiro"]

col1, col2 = st.columns(2)
with col1:
    fin["investimento_inicial"] = st.number_input(
        "Investimento inicial (R$)", min_value=0.0, step=100.0,
        value=float(fin.get("investimento_inicial", 0.0)),
    )
with col2:
    fin["horizonte_meses"] = st.number_input(
        "Horizonte da projeção (meses)", min_value=1, max_value=60,
        value=int(fin.get("horizonte_meses", 12)),
    )

st.divider()
st.subheader("📈 Receitas mensais previstas")

# CORREÇÃO: Garantir que descricao seja sempre string
if fin["receitas"]:
    df_rec = pd.DataFrame(fin["receitas"])
    # Garantir colunas existentes
    for col, default in [("descricao", ""), ("valor_mensal", 0.0)]:
        if col not in df_rec.columns:
            df_rec[col] = default
        elif col == "descricao":
            # Forçar conversão para string
            df_rec[col] = df_rec[col].astype(str)
else:
    # DataFrame vazio com coluna descricao como string
    df_rec = pd.DataFrame({
        "descricao": pd.Series(dtype="object"),
        "valor_mensal": pd.Series(dtype="float64")
    })

# Hash para forçar recriação
rec_hash = hash(str(sorted([str(item) for item in fin["receitas"]]))) if fin["receitas"] else 0
editor_key_rec = f"editor_receitas_{rec_hash}"

edited_rec = st.data_editor(
    df_rec, 
    num_rows="dynamic", 
    use_container_width=True, 
    hide_index=True, 
    key=editor_key_rec,
    column_config={
        "descricao": st.column_config.TextColumn("Fonte de receita", width="large"),
        "valor_mensal": st.column_config.NumberColumn("Valor mensal (R$)", format="R$ %.2f"),
    },
)

# Processar dados editados
if edited_rec is not None:
    edited_rec = edited_rec.fillna(0)
    novos_receitas = []
    for _, row in edited_rec.iterrows():
        descricao = str(row.get("descricao", "")).strip()
        if descricao:  # Só adicionar se tiver descrição
            try:
                valor = float(row.get("valor_mensal", 0))
            except (ValueError, TypeError):
                valor = 0.0
            novos_receitas.append({
                "descricao": descricao,
                "valor_mensal": valor
            })
    
    if novos_receitas != fin["receitas"]:
        fin["receitas"] = novos_receitas
        st.rerun()

st.subheader("📉 Custos e despesas mensais")

# CORREÇÃO: Garantir que descricao seja sempre string para custos
if fin["custos"]:
    df_custo = pd.DataFrame(fin["custos"])
    # Garantir colunas existentes
    for col, default in [("descricao", ""), ("tipo", "Fixo"), ("valor_mensal", 0.0)]:
        if col not in df_custo.columns:
            df_custo[col] = default
        elif col == "descricao":
            # Forçar conversão para string
            df_custo[col] = df_custo[col].astype(str)
else:
    # DataFrame vazio com coluna descricao como string
    df_custo = pd.DataFrame({
        "descricao": pd.Series(dtype="object"),
        "tipo": pd.Series(dtype="string"),
        "valor_mensal": pd.Series(dtype="float64")
    })

# Hash para forçar recriação
custo_hash = hash(str(sorted([str(item) for item in fin["custos"]]))) if fin["custos"] else 0
editor_key_custo = f"editor_custos_{custo_hash}"

edited_custo = st.data_editor(
    df_custo, 
    num_rows="dynamic", 
    use_container_width=True, 
    hide_index=True, 
    key=editor_key_custo,
    column_config={
        "descricao": st.column_config.TextColumn("Custo/despesa", width="large"),
        "tipo": st.column_config.SelectboxColumn("Tipo", options=["Fixo", "Variável"]),
        "valor_mensal": st.column_config.NumberColumn("Valor mensal (R$)", format="R$ %.2f"),
    },
)

# Processar dados editados
if edited_custo is not None:
    edited_custo = edited_custo.fillna(0)
    novos_custos = []
    for _, row in edited_custo.iterrows():
        descricao = str(row.get("descricao", "")).strip()
        if descricao:  # Só adicionar se tiver descrição
            try:
                valor = float(row.get("valor_mensal", 0))
            except (ValueError, TypeError):
                valor = 0.0
            tipo = row.get("tipo", "Fixo")
            if tipo not in ["Fixo", "Variável"]:
                tipo = "Fixo"
            novos_custos.append({
                "descricao": descricao,
                "tipo": tipo,
                "valor_mensal": valor
            })
    
    if novos_custos != fin["custos"]:
        fin["custos"] = novos_custos
        st.rerun()

st.divider()

total_receitas = sum(float(r.get("valor_mensal", 0) or 0) for r in fin["receitas"])
total_custos = sum(float(c.get("valor_mensal", 0) or 0) for c in fin["custos"])
resultado_mensal = total_receitas - total_custos
horizonte = int(fin["horizonte_meses"])

st.subheader("📊 Resumo da projeção")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Receita mensal", f"R$ {total_receitas:,.2f}")
m2.metric("Custo mensal", f"R$ {total_custos:,.2f}")
m3.metric("Resultado mensal", f"R$ {resultado_mensal:,.2f}")

if resultado_mensal > 0 and fin["investimento_inicial"] > 0:
    payback = fin["investimento_inicial"] / resultado_mensal
    m4.metric("Payback estimado", f"{payback:.1f} meses")
else:
    m4.metric("Payback estimado", "—")

# Projeção acumulada
meses = list(range(1, horizonte + 1))
acumulado = []
saldo = -fin["investimento_inicial"]
for _ in meses:
    saldo += resultado_mensal
    acumulado.append(saldo)

df_proj = pd.DataFrame({"Mês": meses, "Saldo acumulado (R$)": acumulado}).set_index("Mês")
st.line_chart(df_proj)

st.caption(
    "Este é um modelo simplificado (fluxo de caixa constante), útil para uma visão geral. "
    "Para decisões financeiras críticas, complemente com um contador ou especialista financeiro."
)


def system_prompt():
    return (
        "Você é um consultor financeiro especializado em pequenas e médias empresas no Brasil. "
        "Responda em português, com linguagem simples e prática, sem jargões desnecessários. "
        "Não forneça recomendações de investimento pessoal, apenas apoio ao planejamento do negócio."
    )


def builder(instrucao):
    empresa = data["empresa"].get("nome") or "a empresa"
    setor = data["empresa"].get("setor") or "não informado"
    base = (
        f"Empresa: {empresa}. Setor: {setor}.\n"
        f"Investimento inicial: R$ {fin['investimento_inicial']:.2f}.\n"
        f"Receita mensal total: R$ {total_receitas:.2f}. Custo mensal total: R$ {total_custos:.2f}. "
        f"Resultado mensal: R$ {resultado_mensal:.2f}.\n"
    )
    base += instrucao if instrucao else (
        "Analise brevemente esse cenário financeiro (riscos, pontos de atenção, sugestões de itens de "
        "receita/custo que podem estar faltando) em até 5 bullets.\n"
    )
    return base


ai_assist_widget("financeiro_geral", "Plano Financeiro", system_prompt(), builder)
