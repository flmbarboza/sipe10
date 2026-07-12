import pandas as pd
import streamlit as st
from utils.data_manager import init_data, get_data, sidebar_data_controls
from utils.ai_helper import sidebar_api_key_input, ai_assist_widget

st.set_page_config(page_title="Planejamento Estratégico", page_icon="🧭", layout="wide")
init_data()
data = get_data()

st.sidebar.title("🧭 Gestor Estratégico")
sidebar_api_key_input()
sidebar_data_controls()

st.title("🧭 Planejamento Estratégico")

def system_prompt():
    return (
        "Você é um consultor sênior de planejamento estratégico empresarial. Responda em "
        "português do Brasil, de forma clara, inspiradora e ao mesmo tempo objetiva."
    )

tab1, tab2, tab3 = st.tabs(["🌟 Missão, Visão e Valores", "🔀 SWOT Cruzada", "🎯 Objetivos, KPIs e Metas"])

# ---------------- Missão, Visão, Valores ----------------
with tab1:
    st.subheader("Missão, Visão e Valores")

    missao = st.text_area("Missão — por que a empresa existe hoje?", value=data["mvv"]["missao"], height=100)
    data["mvv"]["missao"] = missao

    def builder_missao(instrucao):
        empresa = data["empresa"].get("nome") or "a empresa"
        setor = data["empresa"].get("setor") or "não informado"
        base = f"Empresa: {empresa}. Setor: {setor}. Missão atual: '{missao or '(vazio)'}'.\n"
        base += instrucao if instrucao else "Sugira uma missão objetiva, em 1-2 frases.\n"
        return base

    ai_assist_widget("mvv_missao", "Missão", system_prompt(), builder_missao)

    visao = st.text_area("Visão — onde a empresa quer chegar (médio/longo prazo)?", value=data["mvv"]["visao"], height=100)
    data["mvv"]["visao"] = visao

    def builder_visao(instrucao):
        empresa = data["empresa"].get("nome") or "a empresa"
        setor = data["empresa"].get("setor") or "não informado"
        base = f"Empresa: {empresa}. Setor: {setor}. Visão atual: '{visao or '(vazio)'}'.\n"
        base += instrucao if instrucao else "Sugira uma visão inspiradora e mensurável no tempo, em 1-2 frases.\n"
        return base

    ai_assist_widget("mvv_visao", "Visão", system_prompt(), builder_visao)

    st.markdown("**Valores**")
    df_valores = pd.DataFrame(data["mvv"]["valores"], columns=["valor"]) if data["mvv"]["valores"] else pd.DataFrame(columns=["valor"])
    edited_valores = st.data_editor(
        df_valores, num_rows="dynamic", use_container_width=True, hide_index=True,
        column_config={"valor": st.column_config.TextColumn("Valor organizacional", width="large")},
        key="editor_valores",
    )
    data["mvv"]["valores"] = [v for v in edited_valores["valor"].fillna("").tolist() if v]

    def builder_valores(instrucao):
        empresa = data["empresa"].get("nome") or "a empresa"
        atuais = ", ".join(data["mvv"]["valores"]) or "(nenhum ainda)"
        base = f"Empresa: {empresa}. Valores já definidos: {atuais}.\n"
        base += instrucao if instrucao else "Sugira de 4 a 6 valores organizacionais, cada um com uma frase curta explicando.\n"
        return base

    ai_assist_widget("mvv_valores", "Valores", system_prompt(), builder_valores)

# ---------------- SWOT Cruzada ----------------
with tab2:
    st.subheader("Matriz SWOT Cruzada")
    st.caption(
        "Cruze os quadrantes da Análise SWOT para gerar estratégias de ação: "
        "**SO** (usar forças para aproveitar oportunidades), **ST** (usar forças para neutralizar ameaças), "
        "**WO** (superar fraquezas aproveitando oportunidades), **WT** (reduzir fraquezas e evitar ameaças)."
    )

    forcas = [i.get("descricao", "") for i in data["swot"]["forcas"] if i.get("descricao")]
    fraquezas = [i.get("descricao", "") for i in data["swot"]["fraquezas"] if i.get("descricao")]
    oportunidades = [i.get("descricao", "") for i in data["swot"]["oportunidades"] if i.get("descricao")]
    ameacas = [i.get("descricao", "") for i in data["swot"]["ameacas"] if i.get("descricao")]

    if not any([forcas, fraquezas, oportunidades, ameacas]):
        st.warning("Preencha a página **🎯 Análise SWOT** primeiro para poder cruzar os quadrantes aqui.")

    with st.expander("Ver itens da SWOT usados no cruzamento"):
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown("**Forças**\n\n" + "\n".join(f"- {f}" for f in forcas) if forcas else "**Forças**\n\n_(vazio)_")
        c2.markdown("**Fraquezas**\n\n" + "\n".join(f"- {f}" for f in fraquezas) if fraquezas else "**Fraquezas**\n\n_(vazio)_")
        c3.markdown("**Oportunidades**\n\n" + "\n".join(f"- {f}" for f in oportunidades) if oportunidades else "**Oportunidades**\n\n_(vazio)_")
        c4.markdown("**Ameaças**\n\n" + "\n".join(f"- {f}" for f in ameacas) if ameacas else "**Ameaças**\n\n_(vazio)_")

    QUADRANTES_CRUZ = [
        ("SO", "🚀 SO — Forças + Oportunidades", "Estratégias ofensivas: potencializar."),
        ("ST", "🛡️ ST — Forças + Ameaças", "Estratégias defensivas: proteger."),
        ("WO", "🔧 WO — Fraquezas + Oportunidades", "Estratégias de reforço: melhorar para aproveitar."),
        ("WT", "🚧 WT — Fraquezas + Ameaças", "Estratégias de sobrevivência: minimizar riscos."),
    ]

    col_a, col_b = st.columns(2)
    cols_map = {0: col_a, 1: col_b, 2: col_a, 3: col_b}

    for i, (chave, titulo, ajuda) in enumerate(QUADRANTES_CRUZ):
        with cols_map[i]:
            st.markdown(f"#### {titulo}")
            st.caption(ajuda)
            itens = data["swot_cruzada"].get(chave, [])
            df = pd.DataFrame(itens) if itens else pd.DataFrame(columns=["estrategia"])
            if "estrategia" not in df.columns:
                df["estrategia"] = ""
            edited = st.data_editor(
                df, num_rows="dynamic", use_container_width=True, hide_index=True,
                key=f"editor_cruz_{chave}",
                column_config={"estrategia": st.column_config.TextColumn("Estratégia", width="large")},
            )
            data["swot_cruzada"][chave] = edited.fillna("").to_dict("records")

            def builder(instrucao, chave=chave, titulo=titulo):
                base = (
                    f"Forças: {'; '.join(forcas) or '(vazio)'}\n"
                    f"Fraquezas: {'; '.join(fraquezas) or '(vazio)'}\n"
                    f"Oportunidades: {'; '.join(oportunidades) or '(vazio)'}\n"
                    f"Ameaças: {'; '.join(ameacas) or '(vazio)'}\n"
                    f"Quadrante da SWOT cruzada a preencher: {titulo}.\n"
                )
                base += instrucao if instrucao else "Sugira de 3 a 5 estratégias específicas para este quadrante, cruzando os itens acima.\n"
                return base

            ai_assist_widget(f"cruz_{chave}", titulo, system_prompt(), builder)

# ---------------- Objetivos, KPIs, Metas ----------------
with tab3:
    st.subheader("Objetivos Estratégicos, KPIs e Metas")
    st.caption("Defina objetivos concretos, o indicador que vai medi-los e a meta com prazo.")

    itens = data["objetivos"]
    df = pd.DataFrame(itens) if itens else pd.DataFrame(
        columns=["objetivo", "perspectiva", "kpi", "meta", "prazo"]
    )
    for col in ["objetivo", "perspectiva", "kpi", "meta", "prazo"]:
        if col not in df.columns:
            df[col] = ""

    edited = st.data_editor(
        df, num_rows="dynamic", use_container_width=True, hide_index=True,
        key="editor_objetivos",
        column_config={
            "objetivo": st.column_config.TextColumn("Objetivo estratégico", width="large"),
            "perspectiva": st.column_config.SelectboxColumn(
                "Perspectiva", options=["Financeira", "Clientes", "Processos internos", "Aprendizado e crescimento"]
            ),
            "kpi": st.column_config.TextColumn("KPI (indicador)"),
            "meta": st.column_config.TextColumn("Meta"),
            "prazo": st.column_config.TextColumn("Prazo"),
        },
    )
    data["objetivos"] = edited.fillna("").to_dict("records")

    def builder_obj(instrucao):
        empresa = data["empresa"].get("nome") or "a empresa"
        setor = data["empresa"].get("setor") or "não informado"
        estrategias_cruzadas = []
        for q in ["SO", "ST", "WO", "WT"]:
            estrategias_cruzadas += [i.get("estrategia", "") for i in data["swot_cruzada"].get(q, []) if i.get("estrategia")]
        base = (
            f"Empresa: {empresa}. Setor: {setor}.\n"
            f"Estratégias da SWOT cruzada já definidas: {'; '.join(estrategias_cruzadas) or '(nenhuma ainda)'}\n"
        )
        base += instrucao if instrucao else (
            "Sugira de 3 a 5 objetivos estratégicos SMART, cada um com uma sugestão de KPI e meta com prazo, "
            "no formato: Objetivo | Perspectiva (BSC) | KPI | Meta | Prazo.\n"
        )
        return base

    ai_assist_widget("objetivos_geral", "Objetivos, KPIs e Metas", system_prompt(), builder_obj)
