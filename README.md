# Git Hands-On Repo (Beca GenAI)

Repositório modelo para as atividades práticas da disciplina **Git na Prática**.

# Beca GenAI 2026 — NTT DATA

Repositório oficial do programa de formação **Beca GenAI 2026**, trilha de desenvolvimento e deploy de aplicações com Large Language Models (LLMs).

---

## Sobre o Programa

Programa intensivo de **4 semanas** que leva os participantes desde os fundamentos de IA/ML até a construção e deploy de aplicações GenAI em produção, com projeto incremental desenvolvido ao longo de toda a trilha.

**Formato:** 8h/dia — Teoria + Hands-on + Projeto Incremental  
**Stack principal:** Python · OpenAI SDK · LangChain · Azure · Docker  
**Período:** 04/03/2026 a 27/03/2026

---

## Grade do Programa

### Semana 1 — Fundamentos & Setup

| Data | Manhã (9h–12h) | Tarde (14h–18h) | Facilitadores |
|------|----------------|-----------------|---------------|
| 03/03 Ter | Boas-vindas institucional, apresentações | Setup de Ambiente (Python, Git, VSCode, Azure CLI) | RH / Giovanni / Otávio / Andre Yuji |
| 04/03 Qua | Git na Prática (branching, PRs, code review) | Fundamentos de Dados, Python Aplicado à IA (APIs, JSON, Pandas, NumPy) | Cleidiane / Carlos / Mickael / Camila |
| 05/03 Qui | Fundamentos de LLM (Transformer, tokenização, embeddings) | Python para LLMs (manipulação de texto, embeddings, OpenAI SDK) | Cleidiane / Andre Yuji / Thiago |
| 06/03 Sex | Python para LLMs (continuação) | Prompt Engineering na Prática (CoT, few-shot, system prompts) | Giovanni / Gabriel / Leticia / Thiago |

### Semana 2 — Construindo Aplicações LLM

| Data | Manhã (9h–12h) | Tarde (14h–18h) | Facilitadores |
|------|----------------|-----------------|---------------|
| 09/03 Seg | Arquitetura de Apps LLM | Hands-on: Primeiro App LLM do Zero | Alessandro / Giovanni / Arthur |
| 10/03 Ter | RAG — Pipeline Completo (chunking, embeddings, indexação) | Hands-on: RAG do Zero (ingestão, vector store, retrieval) | Giovanni / Cleidiane / Alessandro / Vanessa / Arthur |
| 11/03 Qua | LangChain Fundamentos (chains, prompts, output parsers) | Hands-on: Construindo Chains (sequencial, condicional, com memória) | Deborah / Alessandro / Gabriel |
| 12/03 Qui | RAG Avançado (re-ranking, hybrid search, avaliação) | Hands-on: Métricas e Qualidade de RAG | Deborah |
| 13/03 Sex | Tool Use & Function Calling | Hands-on: Agente com Ferramentas | Giovanni / Gabriel |

### Semana 3 — Agentes, Deploy & Operação

| Data | Manhã (9h–12h) | Tarde (14h–18h) | Facilitadores |
|------|----------------|-----------------|---------------|
| 16/03 Seg | Agentes Especialistas (planejamento, execução, self-reflection) | Hands-on: Construindo Agente Completo | Alessandro / Gabriel |
| 17/03 Ter | Multi-Agent & MCP (Model Context Protocol, A2A) | Hands-on: Orquestração Multi-Agente | Giovanni / Gabriel Nader |
| 18/03 Qua | Docker & Containers para GenAI | Hands-on: Containerizando o Projeto | Alessandro / Mickael |
| 19/03 Qui | Deploy na Azure (App Service, Container Apps, Azure OpenAI) | Hands-on: Deploy do Projeto na Cloud | Alessandro / Mickael |
| 20/03 Sex | LLMOps & Observabilidade (métricas, traces, custo) | Hands-on: Instrumentando o Projeto + Plataforma AgeNTTic | Thiago / Gabriel Nader |

### Semana 4 — Projeto Integrado & Encerramento

| Data | Atividade | Facilitadores |
|------|-----------|---------------|
| 23/03 Seg | Briefing + Planejamento — Sprint 1 | Carlos / Time |
| 24/03 Ter | Desenvolvimento — Sprint 2 | Time de Instrutores |
| 25/03 Qua | Desenvolvimento — Sprint 3 + Code Review | Time de Instrutores |
| 26/03 Qui | Finalização, deploy e preparação das apresentações | Time de Instrutores |
| 27/03 Sex | Apresentações para banca + Retrospectiva + Encerramento | Carlos / Banca / Time Completo |

---

## Estrutura do Repositório

```
beca-2026/
│
├── README.md
│
├── semana-01-fundamentos/
├── semana-02-aplicacoes-llm/
├── semana-03-agentes-deploy/
├── semana-04-projeto-final/
│
└── projeto/                    # app incremental — cresce ao longo das 4 semanas
    ├── app/
    ├── data/
    ├── docs/
    └── tests/
```

Cada pasta de semana segue a estrutura:

```
semana-XX/
├── README.md
├── exercicios/     # notebooks para os becários
├── solucoes/       # gabarito
└── slides/         # material das aulas
```

---

## Fluxo de Branches

```
main                        # material oficial e estável
└── dev                     # integração antes de ir para main
    └── conteudo/semana-XX  # cada instrutor trabalha aqui
```

| Branch | Quem faz push | Como entra na próxima |
|--------|---------------|-----------------------|
| `main` | Ninguém diretamente | Somente via Merge Request aprovado a partir de `dev` |
| `dev` | Ninguém diretamente | Somente via Merge Request da branch de conteúdo |
| `conteudo/semana-XX` | Instrutor responsável | Livre |

### Comandos para instrutores

```bash
# Clonar o repositório
git clone https://oauth2:SEU_TOKEN@umane.xxxxx.xxxxxxx.xxx/git/DATASCIENC/beca-2026.git

# Criar branch de trabalho a partir de dev
git checkout dev
git pull origin dev
git checkout -b conteudo/semana-01

# Enviar alterações
git add .
git commit -m "feat: adiciona exercícios dia 3 - python aplicado ia"
git push origin conteudo/semana-01
```

---

## Setup do Ambiente

```bash
# Criar ambiente virtual
python -m venv .venv

# Ativar (Windows)
# source .venv/Scripts/activate
.venv\Scripts\activate

# Ativar (Mac/Linux)
source .venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

Crie um arquivo `.env` na raiz do projeto com suas credenciais:

```
OPENAI_API_KEY=sua_chave_aqui
AZURE_OPENAI_ENDPOINT=seu_endpoint
AZURE_OPENAI_KEY=sua_chave_azure
```

> O arquivo `.env` está no `.gitignore` e nunca deve ser commitado.

---

## Convenção de Commits

```
feat:      novo conteúdo ou exercício
fix:       correção em material existente
docs:      atualização de README ou documentação
refactor:  reorganização de arquivos
```

---

## Time de Instrutores

| Nome | Semanas |
|------|---------|
| Cleidiane Silva Prates | Semana 1 (Qua/Qui), Semana 2 (Ter) |
| Carlos Porto | Semana 1, Semana 4 |
| Mickael Carneiro Figueredo | Semana 1, Semana 3 |
| Andre Yuji Oku | Semana 1 |
| Thiago Nogueira | Semana 1, Semana 3 |
| Giovanni Almeida Marazzi | Semana 1, Semana 2, Semana 3 |
| Deborah Mesquita | Semana 2 |
| Alessandro Calixto | Semana 2, Semana 3 |
| Gabriel Pancia | Semana 2, Semana 3 |
| Gabriel Nader | Semana 3 |

---

*Beca GenAI 2026 — NTT DATA*
