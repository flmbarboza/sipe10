import streamlit as st

st.set_page_config(
    page_title="SIPE",
    page_icon="🎯",
    layout="wide"
)

st.switch_page("pages/00_🏠_Início.py")

# ========== BOTÃO PRÓXIMA ETAPA ==========
# Encontrar a próxima etapa não concluída
proxima_etapa = None
for icone, titulo, desc, pagina in etapas:
    if titulo == "Business Model Canvas" and not data.get("bmc") or not any(data["bmc"].values()):
        proxima_etapa = (titulo, pagina)
        break
    elif titulo == "Análise PESTEL" and not data.get("pestel") or not any([any([i.get("descricao") for i in itens]) for itens in data["pestel"].values()]):
        proxima_etapa = (titulo, pagina)
        break
    elif titulo == "5 Forças de Porter" and not data.get("porter_analise") or not any([v.get("notas") for v in data["porter_analise"].values()]):
        proxima_etapa = (titulo, pagina)
        break
    elif titulo == "Análise SWOT" and not data.get("swot") or not any([any([i.get("descricao") for i in itens]) for itens in data["swot"].values()]):
        proxima_etapa = (titulo, pagina)
        break
    elif titulo == "Planejamento Estratégico" and not data.get("objetivos") or not any([o.get("objetivo") for o in data["objetivos"]]):
        proxima_etapa = (titulo, pagina)
        break
    elif titulo == "Plano de Ação (5W2H)" and not data.get("acao_5w2h") or not any([a.get("what") for a in data["acao_5w2h"]]):
        proxima_etapa = (titulo, pagina)
        break
    elif titulo == "Planos por Função" and not data.get("departamentos") or not any([any([v for v in depto.values() if v]) for depto in data["departamentos"].values()]):
        proxima_etapa = (titulo, pagina)
        break
    elif titulo == "Orçamento" and not data.get("orcamento") or not (data["orcamento"].get("receitas") or data["orcamento"].get("investimentos")):
        proxima_etapa = (titulo, pagina)
        break
    elif titulo == "Monitoramento" and not data.get("monitoramento") or not data["monitoramento"].get("alertas"):
        proxima_etapa = (titulo, pagina)
        break
    elif titulo == "Revisão Estratégica":
        proxima_etapa = (titulo, pagina)
        break

if proxima_etapa:
    titulo, pagina = proxima_etapa
    col_prox1, col_prox2, col_prox3 = st.columns([1, 2, 1])
    with col_prox2:
        if st.button(f"🚀 Próxima Etapa: {titulo}", use_container_width=True):
            st.switch_page(f"pages/{pagina}.py")
