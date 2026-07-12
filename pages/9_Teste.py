import streamlit as st
from openai import OpenAI

#client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
client = OpenAI(api_key=st.secrets["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"])
st.title("Meu Sistema")

# Formulário principal
empresa = st.text_input("Nome da empresa")
segmento = st.text_input("Segmento")

st.divider()

st.subheader("💬 Assistente IA")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if pergunta := st.chat_input("Pergunte ao assistente..."):

    st.session_state.messages.append(
        {"role":"user","content":pergunta}
    )

    with st.chat_message("user"):
        st.markdown(pergunta)

    resposta = client.chat.completions.create(
        model="gpt-5.5",
        messages=st.session_state.messages
    )

    texto = resposta.choices[0].message.content

    st.session_state.messages.append(
        {"role":"assistant","content":texto}
    )

    with st.chat_message("assistant"):
        st.markdown(texto)
