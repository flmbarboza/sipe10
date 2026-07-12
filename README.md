# 🧭 Gestor Estratégico

Aplicação em **Streamlit** para apoiar gestores de empresas na construção do planejamento estratégico completo, do modelo de negócio ao plano de ação.

## 📦 Estrutura do app

1. **Business Model Canvas** — os 9 blocos do modelo de negócio.
2. **Análises de Contexto**
   - **Análise PESTEL** (Político, Econômico, Social, Tecnológico, Ecológico, Legal)
   - **5 Forças de Porter**
   - **Análise SWOT** (alimentada pelas duas análises acima)
3. **Planejamento Estratégico**
   - Missão, Visão e Valores
   - SWOT Cruzada (matriz de estratégias a partir da SWOT)
   - Objetivos Estratégicos, KPIs e Metas
4. **Plano Financeiro** (receitas, custos, investimento e projeção)
5. **Plano de Ação (5W2H)**
6. **Relatório Completo** (compila tudo e gera download em Markdown/PDF)

Todos os campos podem ser **editados, incluídos e excluídos**. Os dados podem ser **importados (upload de JSON)** e **exportados (download de JSON)** a qualquer momento pela barra lateral, e cada seção tem exportação própria em CSV/Markdown quando fizer sentido.

Cada seção conta com o botão **"🤖 Consultar IA"**, que usa a API da Anthropic (Claude) para sugerir preenchimentos, dar exemplos e validar o conteúdo digitado.

## 🚀 Como rodar localmente

```bash
git clone <seu-repositorio>
cd gestor-estrategico
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## 🔑 Configurando a IA (Claude)

Você precisa de uma chave de API da Anthropic (https://console.anthropic.com/).

Opções para informar a chave:

1. **Pela interface**: cole a chave no campo da barra lateral ao abrir o app (fica salva apenas na sessão).
2. **Via secrets do Streamlit** (recomendado para deploy): crie o arquivo `.streamlit/secrets.toml`:

```toml
ANTHROPIC_API_KEY = "sua-chave-aqui"
```

## ☁️ Deploy no Streamlit Community Cloud

1. Suba este repositório no GitHub.
2. Acesse https://share.streamlit.io e conecte o repositório.
3. Defina `app.py` como arquivo principal.
4. Adicione `ANTHROPIC_API_KEY` em **Settings > Secrets**.

## 🗂️ Persistência de dados

O app guarda tudo em `st.session_state` durante o uso. Para não perder o trabalho:

- Use **"⬇️ Baixar dados (.json)"** na barra lateral sempre que quiser salvar.
- Use **"⬆️ Carregar dados (.json)"** para retomar um trabalho salvo anteriormente.

## 📁 Estrutura de pastas

```
gestor-estrategico/
├── app.py
├── requirements.txt
├── pages/
│   ├── 1_📋_Business_Model_Canvas.py
│   ├── 2_🌍_Analise_PESTEL.py
│   ├── 3_⚔️_5_Forcas_de_Porter.py
│   ├── 4_🎯_Analise_SWOT.py
│   ├── 5_🧭_Planejamento_Estrategico.py
│   ├── 6_💰_Plano_Financeiro.py
│   ├── 7_✅_Plano_de_Acao_5W2H.py
│   └── 8_📄_Relatorio_Completo.py
├── utils/
│   ├── data_manager.py
│   ├── ai_helper.py
│   └── pdf_export.py
└── .streamlit/
    └── config.toml
```

## 📝 Licença

Uso livre para fins internos de gestão. Adapte como quiser.
