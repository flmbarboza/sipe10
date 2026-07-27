import streamlit as st
from utils.analytics import UXMonitor
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="UX Dashboard", layout="wide")

# Controle de acesso simples
if 'dev_password' not in st.session_state:
    password = st.text_input("Senha do desenvolvedor:", type="password")
    if password == "admin123":  # Use secrets.toml para isso
        st.session_state.dev_password = True
    else:
        st.warning("Acesso negado.")
        st.stop()

monitor = UXMonitor()
df = pd.DataFrame(st.session_state.analytics['events'])

if df.empty:
    st.info("Ainda não há dados coletados. Use o app para gerar eventos.")
    st.stop()

st.title("🔍 Dashboard de UX - SIPE10")

# Métricas principais
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total de Eventos", len(df))
with col2:
    st.metric("Sessões Únicas", df.session_id.nunique())
with col3:
    ai_calls = len(df[df.event_type == 'ai_call'])
    st.metric("Chamadas IA", ai_calls)
with col4:
    errors = len(df[df.event_type == 'error'])
    st.metric("Erros", errors, delta=f"-{errors/len(df)*100:.1f}%" if len(df)>0 else "0%")

# 1. Mapa de calor de navegação
st.subheader("🗺️ Fluxo de Navegação")
pages_order = df[df.event_type == 'page_view'].page.value_counts().index.tolist()
heatmap_data = pd.crosstab(
    df[df.event_type == 'page_view'].page,
    df[df.event_type == 'page_view'].session_id
)
fig = px.imshow(heatmap_data, 
                title="Mapa de Calor: Páginas vs. Sessões",
                labels=dict(x="Sessão", y="Página", color="Visualizações"))
st.plotly_chart(fig)

# 2. Tempo por página
st.subheader("⏱️ Tempo Médio por Página")
durations = df[df.event_type == 'page_duration']
if not durations.empty:
    durations['seconds'] = durations['metadata'].apply(lambda x: x.get('seconds', 0))
    fig = px.bar(durations, x='page', y='seconds', 
                 title="Tempo Gasto por Página (segundos)")
    st.plotly_chart(fig)

# 3. Eventos por tipo
st.subheader("📊 Distribuição de Eventos")
event_counts = df.event_type.value_counts()
fig = px.pie(values=event_counts.values, names=event_counts.index, 
             title="Tipos de Eventos")
st.plotly_chart(fig)

# 4. Análise de Sequência (Funil)
st.subheader("🔗 Funil de Conversão")
expected_flow = ['Business Model Canvas', 'PESTEL', '5 Forças', 'SWOT', 
                 'Planejamento Estratégico', 'Plano Financeiro', 'Plano de Ação']
# Mostrar % de usuários que chegam em cada etapa
sessions = df[df.event_type == 'page_view'].groupby('session_id')['page'].apply(list)
completion = {}
for page in expected_flow:
    completion[page] = sum(1 for s in sessions if page in s) / len(sessions) * 100

fig = px.line(x=list(completion.keys()), y=list(completion.values()),
              title="% de Usuários que Atingem Cada Página",
              labels={'x': 'Etapa', 'y': '% de Conclusão'})
st.plotly_chart(fig)

# 5. Insights gerados
st.subheader("💡 Insights Automáticos")
insights = monitor.get_insights()
st.markdown(insights)

# 6. Exportar dados brutos
if st.button("📥 Baixar Dados de UX (JSON)"):
    import json
    st.download_button(
        label="Baixar JSON",
        data=json.dumps(st.session_state.analytics, indent=2),
        file_name=f"ux_data_{datetime.now().strftime('%Y%m%d')}.json",
        mime="application/json"
    )
