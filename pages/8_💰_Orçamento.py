import pandas as pd
import streamlit as st
import json
import re
from utils.data_manager import init_data, get_data, sidebar_data_controls
from openai import OpenAI

st.set_page_config(page_title="Orçamento Estratégico", page_icon="💰", layout="wide")
init_data()
data = get_data()

st.sidebar.title("🧭 Gestor Estratégico")
sidebar_data_controls()

st.title("💰 Orçamento Estratégico")
st.caption(
    "Consolide todos os custos e receitas dos planos departamentais. "
    "Acompanhe o fluxo de caixa, investimentos e indicadores financeiros."
)

# ========== INICIALIZAR DADOS ==========
if "orcamento" not in data:
    data["orcamento"] = {
        "receitas": [],
        "investimentos": [],
        "periodo_inicio": "2026-01",
        "periodo_fim": "2026-12"
    }

# ========== FUNÇÕES DE CONSOLIDAÇÃO ==========
def consolidar_custos_departamentais():
    """Consolida todos os custos dos planos departamentais"""
    custos = []
    if "departamentos" in data:
        for depto, info in data["departamentos"].items():
            for recurso in info.get("recursos", []):
                if recurso.get("Recurso") and recurso.get("Valor estimado"):
                    try:
                        valor = float(str(recurso["Valor estimado"]).replace("R$", "").replace(",", ".").strip())
                    except:
                        valor = 0
                    custos.append({
                        "Departamento": depto,
                        "Recurso": recurso.get("Recurso", ""),
                        "Tipo": recurso.get("Tipo", "Operacional"),
                        "Valor Mensal": valor,
                        "Observações": recurso.get("Observações", "")
                    })
            
            for acao in info.get("acoes", []):
                if acao.get("Ação") and acao.get("Custo estimado"):
                    try:
                        valor = float(str(acao["Custo estimado"]).replace("R$", "").replace(",", ".").strip())
                    except:
                        valor = 0
                    custos.append({
                        "Departamento": depto,
                        "Recurso": acao.get("Ação", ""),
                        "Tipo": "Ação",
                        "Valor Mensal": valor / 12,  # Distribuir ao longo do ano
                        "Observações": acao.get("Origem", "")
                    })
    return custos

def calcular_fluxo_caixa(meses, receitas, custos, investimentos):
    """Calcula o fluxo de caixa mensal"""
    fluxo = []
    saldo_acumulado = 0
    
    for mes in range(meses):
        receita_mes = sum([r.get("Valor", 0) for r in receitas if r.get("Mês", 0) == mes + 1])
        custo_mes = sum([c.get("Valor", 0) for c in custos if c.get("Mês", 0) == mes + 1])
        investimento_mes = sum([i.get("Valor", 0) for i in investimentos if i.get("Mês", 0) == mes + 1])
        
        saldo_mes = receita_mes - custo_mes - investimento_mes
        saldo_acumulado += saldo_mes
        
        fluxo.append({
            "Mês": mes + 1,
            "Receitas": receita_mes,
            "Custos": custo_mes,
            "Investimentos": investimento_mes,
            "Saldo": saldo_mes,
            "Acumulado": saldo_acumulado
        })
    
    return fluxo

# ========== FUNÇÕES DE RENDERIZAÇÃO ==========
def render_tabela_editavel(dados, colunas, titulo, chave, altura=200):
    """Renderiza uma tabela editável genérica"""
    if dados:
        df = pd.DataFrame(dados)
        for col in colunas:
            if col not in df.columns:
                df[col] = ""
    else:
        df = pd.DataFrame(columns=colunas)
    
    df_hash = hash(str(df.to_dict())) if not df.empty else 0
    editor_key = f"orcamento_{chave}_{df_hash}"
    
    edited = st.data_editor(
        df,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        key=editor_key,
        column_config={col: st.column_config.TextColumn(col, width="large") for col in colunas}
    )
    
    if edited is not None:
        edited = edited.fillna("")
        novos_dados = []
        for _, row in edited.iterrows():
            item = {}
            valido = False
            for col in colunas:
                valor = str(row.get(col, "")).strip()
                item[col] = valor
                if valor and not valido:
                    valido = True
            if valido:
                novos_dados.append(item)
        return novos_dados
    return dados

# ========== CONSOLIDAR DADOS ==========
custos_consolidados = consolidar_custos_departamentais()

# ========== EXIBIÇÃO ==========

# ---------- RECEITAS PREVISTAS ----------
with st.expander("📈 Receitas Previstas", expanded=True):
    st.markdown("### Receitas Previstas")
    st.caption("Cadastre as receitas previstas por período")
    
    colunas_receitas = ["Descrição", "Fonte", "Valor", "Mês", "Observações"]
    novos = render_tabela_editavel(
        data["orcamento"].get("receitas", []),
        colunas_receitas,
        "Receitas",
        "receitas"
    )
    if novos != data["orcamento"].get("receitas", []):
        data["orcamento"]["receitas"] = novos

# ---------- CUSTOS CONSOLIDADOS ----------
with st.expander("📊 Custos Consolidados", expanded=True):
    st.markdown("### Custos Consolidados por Departamento")
    st.caption("Custos extraídos automaticamente dos planos departamentais")
    
    if custos_consolidados:
        df_custos = pd.DataFrame(custos_consolidados)
        st.dataframe(
            df_custos,
            use_container_width=True,
            hide_index=True
        )
        
        # Resumo por departamento
        st.markdown("#### Resumo por Departamento")
        resumo_depto = df_custos.groupby("Departamento")["Valor Mensal"].sum().reset_index()
        resumo_depto.columns = ["Departamento", "Custo Total"]
        st.dataframe(resumo_depto, use_container_width=True, hide_index=True)
        
        total_custos = resumo_depto["Custo Total"].sum()
        st.metric("Total de Custos Mensais", f"R$ {total_custos:,.2f}")
    else:
        st.info("Nenhum custo consolidado encontrado. Preencha os planos departamentais primeiro.")

# ---------- INVESTIMENTOS ----------
with st.expander("💼 Investimentos"):
    st.markdown("### Investimentos Previstos")
    st.caption("Cadastre os investimentos planejados")
    
    colunas_invest = ["Descrição", "Tipo", "Valor", "Mês", "Observações"]
    novos = render_tabela_editavel(
        data["orcamento"].get("investimentos", []),
        colunas_invest,
        "Investimentos",
        "investimentos"
    )
    if novos != data["orcamento"].get("investimentos", []):
        data["orcamento"]["investimentos"] = novos

# ---------- FLUXO DE CAIXA ----------
with st.expander("💵 Fluxo de Caixa Previsto"):
    st.markdown("### Fluxo de Caixa Mensal")
    
    # Parâmetros
    col_mes1, col_mes2 = st.columns(2)
    with col_mes1:
        mes_inicio = st.text_input("Mês Início (MM/AAAA)", value=data["orcamento"].get("periodo_inicio", "01/2026"))
        data["orcamento"]["periodo_inicio"] = mes_inicio
    with col_mes2:
        mes_fim = st.text_input("Mês Fim (MM/AAAA)", value=data["orcamento"].get("periodo_fim", "12/2026"))
        data["orcamento"]["periodo_fim"] = mes_fim
    
    # Calcular fluxo
    try:
        meses_total = 12  # Simplificado
        receitas = [{"Mês": i+1, "Valor": float(r.get("Valor", 0))} 
                   for i, r in enumerate(data["orcamento"].get("receitas", [])) for _ in range(1)]
        
        # Consolidar custos mensais
        custos_mensais = []
        if custos_consolidados:
            for custo in custos_consolidados:
                valor = custo.get("Valor Mensal", 0)
                for mes in range(1, meses_total + 1):
                    custos_mensais.append({"Mês": mes, "Valor": valor})
        
        investimentos = [{"Mês": i+1, "Valor": float(i.get("Valor", 0))} 
                        for i, inv in enumerate(data["orcamento"].get("investimentos", [])) for _ in range(1)]
        
        fluxo = calcular_fluxo_caixa(meses_total, receitas, custos_mensais, investimentos)
        
        if fluxo:
            df_fluxo = pd.DataFrame(fluxo)
            st.dataframe(
                df_fluxo.style.format({
                    "Receitas": "R$ {:,.2f}",
                    "Custos": "R$ {:,.2f}",
                    "Investimentos": "R$ {:,.2f}",
                    "Saldo": "R$ {:,.2f}",
                    "Acumulado": "R$ {:,.2f}"
                }),
                use_container_width=True,
                hide_index=True
            )
            
            # Gráfico do fluxo
            st.line_chart(df_fluxo.set_index("Mês")[["Receitas", "Custos", "Acumulado"]])
        else:
            st.info("Cadastre receitas e investimentos para visualizar o fluxo de caixa.")
    except:
        st.warning("Verifique os valores cadastrados. Use apenas números nos campos de valor.")

# ---------- ORÇAMENTO POR DEPARTAMENTO ----------
with st.expander("📊 Orçamento por Departamento"):
    st.markdown("### Orçamento por Departamento")
    
    if custos_consolidados:
        df_custos = pd.DataFrame(custos_consolidados)
        orcamento_depto = df_custos.groupby("Departamento").agg({
            "Valor Mensal": "sum",
            "Recurso": "count"
        }).reset_index()
        orcamento_depto.columns = ["Departamento", "Custo Total", "Qtd Recursos"]
        
        st.dataframe(
            orcamento_depto.style.format({"Custo Total": "R$ {:,.2f}"}),
            use_container_width=True,
            hide_index=True
        )
        
        # Gráfico
        st.bar_chart(orcamento_depto.set_index("Departamento")["Custo Total"])
    else:
        st.info("Nenhum custo consolidado encontrado.")

# ---------- INDICADORES FINANCEIROS ----------
with st.expander("📈 Indicadores Financeiros"):
    st.markdown("### Indicadores Financeiros")
    
    # Calcular indicadores
    total_receitas = sum([float(r.get("Valor", 0)) for r in data["orcamento"].get("receitas", [])])
    total_custos = sum([c.get("Valor Mensal", 0) for c in custos_consolidados])
    total_investimentos = sum([float(i.get("Valor", 0)) for i in data["orcamento"].get("investimentos", [])])
    
    margem = (total_receitas - total_custos) / total_receitas if total_receitas > 0 else 0
    roi = (total_receitas - total_custos - total_investimentos) / total_investimentos if total_investimentos > 0 else 0
    
    col_ind1, col_ind2, col_ind3, col_ind4 = st.columns(4)
    with col_ind1:
        st.metric("Receita Total", f"R$ {total_receitas:,.2f}")
    with col_ind2:
        st.metric("Custo Total", f"R$ {total_custos:,.2f}")
    with col_ind3:
        st.metric("Margem", f"{margem:.1%}")
    with col_ind4:
        st.metric("ROI", f"{roi:.1%}")
    
    col_ind5, col_ind6, col_ind7 = st.columns(3)
    with col_ind5:
        payback = total_investimentos / (total_receitas - total_custos) if (total_receitas - total_custos) > 0 else 0
        st.metric("Payback (meses)", f"{payback:.1f}" if payback > 0 else "—")
    with col_ind6:
        st.metric("Investimento Total", f"R$ {total_investimentos:,.2f}")
    with col_ind7:
        st.metric("Resultado", f"R$ {total_receitas - total_custos - total_investimentos:,.2f}")

# ========== BOTÃO PRÓXIMA ETAPA ==========
col_prox1, col_prox2, col_prox3 = st.columns([1, 2, 1])
with col_prox2:
    if st.button("➡️ Próxima Etapa", width="stretch"):
        st.switch_page("pages/9_🛃_Monitoramento.py")
        
# ========== ASSISTENTE IA ==========
st.divider()
st.subheader("💬 Assistente IA - Ajuda com o Orçamento")

col_chat1, col_chat2 = st.columns([5, 1])
with col_chat2:
    if st.button("🗑️ Limpar Chat", use_container_width=True):
        st.session_state.messages_orcamento = []
        st.rerun()

if "messages_orcamento" not in st.session_state:
    st.session_state.messages_orcamento = []

for msg in st.session_state.messages_orcamento:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if pergunta := st.chat_input("Pergunte ao assistente sobre o orçamento estratégico..."):
    st.session_state.messages_orcamento.append({"role": "user", "content": pergunta})
    
    with st.chat_message("user"):
        st.markdown(pergunta)
    
    with st.spinner("🤔 Pensando..."):
        try:
            client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"], base_url="https://openrouter.ai/api/v1")
            
            contexto = f"""
            ORÇAMENTO ESTRATÉGICO:
            - Receita Total: R$ {total_receitas:,.2f}
            - Custo Total: R$ {total_custos:,.2f}
            - Investimento Total: R$ {total_investimentos:,.2f}
            - Margem: {margem:.1%}
            - ROI: {roi:.1%}
            - Quantidade de Custos Consolidados: {len(custos_consolidados)}
            """
            
            empresa_nome = data.get("empresa", {}).get("nome", "a empresa")
            empresa_setor = data.get("empresa", {}).get("setor", "não informado")
            
            mensagens = [
                {"role": "system", "content": f"""Você é um assistente especialista em Orçamento e Finanças Estratégicas.

EMPRESA: {empresa_nome}
SETOR: {empresa_setor}

{contexto}

Responda em português do Brasil, de forma prática e objetiva."""}
            ] + st.session_state.messages_orcamento[:-1]
            
            response = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=mensagens,
                temperature=0.7
            )
            
            resposta = response.choices[0].message.content
            st.session_state.messages_orcamento.append({"role": "assistant", "content": resposta})
            
            with st.chat_message("assistant"):
                st.markdown(resposta)
                
        except Exception as e:
            st.error(f"❌ Erro ao processar sua pergunta: {str(e)}")
