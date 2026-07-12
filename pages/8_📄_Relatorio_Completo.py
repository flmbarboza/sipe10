import streamlit as st
from utils.data_manager import init_data, get_data, sidebar_data_controls
from utils.ai_helper import sidebar_api_key_input, ai_assist_widget, ask_claude
from utils.pdf_export import markdown_to_pdf_bytes

st.set_page_config(page_title="Relatório Completo", page_icon="📄", layout="wide")
init_data()
data = get_data()

st.sidebar.title("🧭 Gestor Estratégico")
#sidebar_api_key_input()
sidebar_data_controls()

st.title("📄 Relatório Completo")
st.caption("Compilação de todas as seções preenchidas, pronta para revisão, download e apresentação.")


def linha(label, valor):
    return f"- **{label}:** {valor}\n" if valor else ""


def build_markdown():
    empresa = data["empresa"]
    md = f"# Planejamento Estratégico — {empresa.get('nome') or '(empresa sem nome)'}\n\n"
    md += linha("Setor", empresa.get("setor"))
    md += linha("Cidade/Estado", empresa.get("cidade_estado"))
    md += linha("Responsável", empresa.get("responsavel"))

    md += "\n## 1. Business Model Canvas\n\n"
    nomes_bmc = {
        "parcerias_chave": "Parcerias-Chave", 
        "atividades_chave": "Atividades-Chave",
        "recursos_chave": "Recursos-Chave", 
        "proposta_valor": "Proposta de Valor",
        "relacionamento_clientes": "Relacionamento com Clientes", 
        "canais": "Canais",
        "segmentos_clientes": "Segmentos de Clientes", 
        "estrutura_custos": "Estrutura de Custos",
        "fontes_receita": "Fontes de Receita",
    }
    
    # CORREÇÃO: Verificar se data["bmc"] existe e é um dicionário
    if "bmc" in data and isinstance(data["bmc"], dict):
        for chave, nome in nomes_bmc.items():
            conteudo = data["bmc"].get(chave, "")
            # Verificar se é string, se for lista, juntar os itens
            if isinstance(conteudo, list):
                conteudo = "\n".join([f"- {item}" for item in conteudo if item])
            elif isinstance(conteudo, str):
                conteudo = conteudo.strip()
            else:
                conteudo = ""
            
            if conteudo:
                md += f"### {nome}\n{conteudo}\n\n"

    md += "## 2. Análises de Contexto\n\n### 2.1 Análise PESTEL\n\n"
    if "pestel" in data and isinstance(data["pestel"], dict):
        for cat, itens in data["pestel"].items():
            if isinstance(itens, list):
                itens_validos = [i for i in itens if isinstance(i, dict) and i.get("descricao")]
                if itens_validos:
                    md += f"**{cat}**\n"
                    for i in itens_validos:
                        md += f"- ({i.get('tipo', '')}, impacto {i.get('impacto', '')}) {i.get('descricao', '')}\n"
                    md += "\n"

    md += "### 2.2 Cinco Forças de Porter\n\n"
    # CORREÇÃO: Verificar se porter_analise existe
    if "porter_analise" in data and isinstance(data["porter_analise"], dict):
        for forca_id, info in data["porter_analise"].items():
            if isinstance(info, dict):
                md += f"- **{info.get('nome', forca_id)}**: intensidade {info.get('intensidade', 0)}/5"
                if info.get("notas"):
                    md += f" — {info['notas']}"
                md += "\n"
    elif "porter" in data and isinstance(data["porter"], dict):
        for forca, info in data["porter"].items():
            if isinstance(info, dict):
                md += f"- **{forca}**: intensidade {info.get('intensidade', 0)}/5"
                if info.get("notas"):
                    md += f" — {info['notas']}"
                md += "\n"

    md += "\n### 2.3 Análise SWOT\n\n"
    nomes_swot = {"forcas": "Forças", "fraquezas": "Fraquezas", "oportunidades": "Oportunidades", "ameacas": "Ameaças"}
    if "swot" in data and isinstance(data["swot"], dict):
        for chave, nome in nomes_swot.items():
            itens = data["swot"].get(chave, [])
            if isinstance(itens, list):
                itens_validos = [i.get("descricao", "") for i in itens if isinstance(i, dict) and i.get("descricao")]
                if itens_validos:
                    md += f"**{nome}**\n"
                    for i in itens_validos:
                        md += f"- {i}\n"
                    md += "\n"

    md += "## 5. Planejamento Estratégico\n\n### 5.1 Missão, Visão e Valores\n\n"
    if "mvv" in data and isinstance(data["mvv"], dict):
        if data["mvv"].get("missao"):
            md += f"**Missão:** {data['mvv']['missao']}\n\n"
        if data["mvv"].get("visao"):
            md += f"**Visão:** {data['mvv']['visao']}\n\n"
        if data["mvv"].get("valores"):
            md += "**Valores:**\n"
            for v in data["mvv"]["valores"]:
                if v:
                    md += f"- {v}\n"
            md += "\n"

    md += "### 5.2 SWOT Cruzada\n\n"
    nomes_cruz = {
        "SO": "Estratégias SO (Forças + Oportunidades)", 
        "ST": "Estratégias ST (Forças + Ameaças)",
        "WO": "Estratégias WO (Fraquezas + Oportunidades)", 
        "WT": "Estratégias WT (Fraquezas + Ameaças)"
    }
    if "swot_cruzada" in data and isinstance(data["swot_cruzada"], dict):
        for chave, nome in nomes_cruz.items():
            itens = data["swot_cruzada"].get(chave, [])
            if isinstance(itens, list):
                itens_validos = [i.get("estrategia", "") for i in itens if isinstance(i, dict) and i.get("estrategia")]
                if itens_validos:
                    md += f"**{nome}**\n"
                    for i in itens_validos:
                        md += f"- {i}\n"
                    md += "\n"

    md += "### 5.3 Objetivos Estratégicos, KPIs e Metas\n\n"
    if "objetivos" in data and isinstance(data["objetivos"], list):
        for obj in data["objetivos"]:
            if isinstance(obj, dict) and obj.get("objetivo"):
                md += (
                    f"- **{obj.get('objetivo')}** ({obj.get('perspectiva', '')}) — "
                    f"KPI: {obj.get('kpi', '')} | Meta: {obj.get('meta', '')} | Prazo: {obj.get('prazo', '')}\n"
                )
        md += "\n"

    md += "## 6. Plano Financeiro\n\n"
    if "financeiro" in data and isinstance(data["financeiro"], dict):
        fin = data["financeiro"]
        md += f"- Investimento inicial: R$ {fin.get('investimento_inicial', 0):.2f}\n"
        md += f"- Horizonte de projeção: {fin.get('horizonte_meses', 0)} meses\n\n"
        
        if fin.get("receitas") and isinstance(fin["receitas"], list):
            md += "**Receitas mensais**\n"
            for r in fin["receitas"]:
                if isinstance(r, dict) and r.get("descricao"):
                    md += f"- {r.get('descricao')}: R$ {float(r.get('valor_mensal', 0) or 0):.2f}\n"
            md += "\n"
        
        if fin.get("custos") and isinstance(fin["custos"], list):
            md += "**Custos e despesas mensais**\n"
            for c in fin["custos"]:
                if isinstance(c, dict) and c.get("descricao"):
                    md += f"- ({c.get('tipo', '')}) {c.get('descricao')}: R$ {float(c.get('valor_mensal', 0) or 0):.2f}\n"
            md += "\n"

    md += "## 7. Plano de Ação (5W2H)\n\n"
    if "acao_5w2h" in data and isinstance(data["acao_5w2h"], list):
        for a in data["acao_5w2h"]:
            if isinstance(a, dict) and a.get("what"):
                md += (
                    f"- **O quê:** {a.get('what')} | **Por quê:** {a.get('why', '')} | "
                    f"**Onde:** {a.get('where', '')} | **Quando:** {a.get('when', '')} | "
                    f"**Quem:** {a.get('who', '')} | **Como:** {a.get('how', '')} | "
                    f"**Quanto custa:** {a.get('how_much', '')} | **Status:** {a.get('status', '')}\n"
                )

    return md


markdown_texto = build_markdown()

st.subheader("👁️ Pré-visualização")
with st.container(border=True):
    st.markdown(markdown_texto)

st.divider()
st.subheader("⬇️ Exportar relatório")

col1, col2 = st.columns(2)
with col1:
    st.download_button(
        "⬇️ Baixar em Markdown (.md)",
        data=markdown_texto.encode("utf-8"),
        file_name="relatorio_planejamento_estrategico.md",
        mime="text/markdown",
        use_container_width=True,
    )
with col2:
    if st.button("📄 Gerar PDF", use_container_width=True):
        pdf_bytes = markdown_to_pdf_bytes(markdown_texto)
        st.session_state["relatorio_pdf_bytes"] = pdf_bytes

    if "relatorio_pdf_bytes" in st.session_state:
        st.download_button(
            "⬇️ Baixar em PDF (.pdf)",
            data=st.session_state["relatorio_pdf_bytes"],
            file_name="relatorio_planejamento_estrategico.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

st.divider()
st.subheader("🤖 Validação final com a IA")
st.caption(
    "Peça uma revisão geral do planejamento: consistência entre as seções, lacunas e sugestões de melhoria."
)

if st.button("Consultar IA — revisar relatório completo"):
    system = (
        "Você é um consultor sênior de estratégia empresarial revisando um planejamento estratégico completo. "
        "Responda em português do Brasil. Aponte, de forma objetiva: (1) inconsistências entre as seções, "
        "(2) lacunas importantes não preenchidas, (3) até 5 recomendações de melhoria."
    )
    prompt = (
        "Revise o planejamento estratégico abaixo (em Markdown) e dê um feedback estruturado:\n\n"
        + markdown_texto[:12000]
    )
    with st.spinner("Analisando o planejamento completo..."):
        resposta = ask_claude(system, prompt, max_tokens=1200)
    st.session_state["revisao_ia"] = resposta

if "revisao_ia" in st.session_state:
    st.markdown(st.session_state["revisao_ia"])
