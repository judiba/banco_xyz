# 🏦 Banco XYZ AI Advisor

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)]()
[![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-red)]()
[![Docker](https://img.shields.io/badge/Docker-Ready-blue)]()
[![LLM](https://img.shields.io/badge/LLM-Azure%20OpenAI-purple)]()
[![RAG](https://img.shields.io/badge/RAG-FAISS-orange)]()

Plataforma completa de geração de relatórios de investimentos com IA, integrando:

- 🤖 LLM (Azure OpenAI)
- 📚 RAG com documentos internos
- 📊 Benchmarks de mercado (CDI, Selic, Ibovespa)
- 👨‍💼 Aprovação humana (Human-in-the-loop)
- 📄 Geração de PDF
- 📤 Entrega por e-mail e WhatsApp
- 🎨 Interface moderna (Streamlit + tema NTT DATA)

---

# 🚀 Visão geral

O sistema permite:

1. Selecionar cliente
2. Gerar relatório com IA
3. Validar conteúdo
4. Aprovar emissão
5. Gerar PDF
6. Enviar ao cliente

---

# 🧠 Arquitetura

```text
Frontend (Streamlit)
    ↓
Backend (FastAPI)
    ↓
LangGraph Workflow
    ↓
Agents + RAG + LLM
    ↓
PDF + Entrega

## Estrutura

banco_xyz/
|
backend/
├── app/
│   ├── agents/
│   │   └── report_agent.py
│   ├── api/
│   │   └── routes.py
│   ├── core/
|   |   └── config.py
|   |   └── security.py
│   ├── graph/
|   |   └── state.py
│   │   └── workflow.py
|   ├── models/ 
|   |   └── delivery.py
|   |   └── enums.py
|   ├── services/
|   |   └── benchmark_service.py
|   |   └── delivery_policy.py
|   |   └── delivery_service.py
|   |   └── email_provider.py
|   |   └── file_service.py
|   |   └── llm_service.py
|   |   └── market_data.py
|   |   └── notification_service.py
|   |   └── pdf_service.py
|   |   └── rag_service.py
|   |   └── report_service.py
|   |   └── report_versions_service.py
|   |   └── whatsapp_provider.py
│   ├── __init__.py
├── bootstrap_vestore.py
├── main.py
|
data/
├── vector_store/ 
|    └──app_state.db
data/
├── corpus/
├── reports/
├── mock_clients.json
└── vector_store/
│
frontend/
├── components/
│   ├── __init__.py
│   ├── approval_panel.py
│   ├── client_summary.py
│   ├── delivery_panel.py
│   ├── timeline.py
│   ├── charts_panel.py
│   ├── report_tabs.py
│   └── ui.py
│
├── services/
│   ├── __init__.py
│   └── api.py
│
├── utils/
│   ├── __init__.py
│   ├── session.py
│   └── formatters.py
├── app.py
├── Dockerfile
├── requirements.txt
|
├── scripts/
|   ├── bootstrap_vectorstore.py
|   ├── docker_sdk_build.py
|   └── import_excel_to_mock_json.py
|
├── .env
├── .env.example
├── docker-compose.yml
├── Makefile
├── README.md

## Como instalar

🔐 Variáveis de ambiente

Sem isso:

sistema entra em modo demo
embeddings locais
fallback de texto

```bash
cp .env.example .env
```
🐳 Execução com Docker

Build
```bash
docker compose build
```
Run
```bash
docker compose up
```
## 🛠️ Comandos úteis

```bash
make build
make up
make down
make restart
make logs

Acessos

- Frontend: 'http://localhost:8501'
- Backend: 'http://localhost:8000'
- Swagger: 'http://localhost:8000/docs'
- OpenAPI JSON: 'http://localhost:8000/openapi.json'

🔄 Fluxo do sistema
Cliente
→ load_client
→ retrieve_knowledge (RAG + benchmarks)
→ build_prompt
→ draft_report (summary + detailed)
→ approval_gate
→ generate_pdf
→ deliver_report

## Como usar

1. Abra o Streamlit.
2. Selecione um cliente.
3. Clique em **Gerar rascunho**.
4. O backend executa o LangGraph e para antes da emissão final.
5. Aprove ou rejeite o relatório.
6. Se aprovado, o PDF é salvo em `data/reports/`.

⚙️ Funcionalidades
📄 Geração de relatório
IA baseada em perfil do cliente
Uso de RAG (documentos internos)
Integração com dados de mercado
📊 Versões do relatório

O sistema gera automaticamente:

🔹 Resumo executivo
bullets objetivos
leitura rápida
recomendações
🔹 Relatório detalhado
cenário macro
análise da carteira
benchmarks
riscos
📈 Benchmarks e dados externos

Integração com:

📊 brapi → Ibovespa e ativos
🏦 Banco Central → séries econômicas
🇧🇷 Brasil API → taxas (CDI, Selic, IPCA)

Uso:

comparação com carteira
enriquecimento do relatório
visualização gráfica
📊 Visualização (Streamlit)

Gráficos adaptados ao perfil:

Perfil	Gráfico
Conservador	Área (estabilidade)
Moderado	Linha (Carteira x CDI x Ibov)
Arrojado	Performance + risco
👨‍💼 Human-in-the-loop
relatório não é emitido automaticamente
exige aprovação manual
garante compliance e governança
📄 PDF
gerado após aprovação
armazenado em:
data/reports/
📤 Entrega

Após aprovação:

📧 envio por e-mail
💬 envio por WhatsApp
📥 download manual
🔌 API
Clientes
GET /api/clients
Relatórios
POST /api/reports/generate
POST /api/reports/approve
POST /api/reports/deliver
GET  /api/reports/status
GET  /api/reports/file

📈 Roadmap
 Plotly avançado (candlestick)
 Dashboard executivo
 Carteira real integrada
 Deploy em cloud (Azure)
 Monitoramento e logs

 ⚠️ Observações
Dados fictícios para demonstração
Sem promessa de retorno financeiro
Necessária validação humana

👨‍💻 Autor
Judyvinna Dionizio Barbosa
BECA - Projeto de IA aplicada a advisory financeiro.