# 🛠️ TTYD — Guia do Desenvolvedor (NTTData) — LEVEL 19

Este guia contém instruções para configurar o ambiente de desenvolvimento usando **VS Code**, **WSL (Ubuntu)** e **Python**.

---

## 💻 Requisitos de Sistema

1. **WSL2 (Windows Subsystem for Linux)**: Recomendado Ubuntu 22.04 LTS ou superior.
2. **Docker Desktop**: Instalado no Windows e configurado para usar o backend do WSL2.
3. **Python 3.10+ (Recomendado 3.12+)**: Instalado dentro do Ubuntu.
4. **Poetry**: Gerenciador de dependências.

Por motivos de segurança atualize o Docker para a versão abaixo:

```bash
docker pull python:3.12-slim
```

---

## 🔌 Extensões Recomendadas (VS Code)

Para uma melhor experiência de desenvolvimento, instale as seguintes extensões no seu VS Code:

- **WSL**: Essencial para abrir o projeto dentro do ambiente Linux.
- **Python (Microsoft)**: Suporte completo para a linguagem.
- **Ruff**: Linter e formatador ultra-rápido (utilizado no projeto).
- **Docker**: Gerenciamento de containers e imagens.
- **Makefile Tools**: Facilita a execução dos comandos do `Makefile`.

---

## 🚀 Iniciando o Desenvolvimento

## 🛠️ Preparando o Ambiente

1. **Configurar o ambiente**:
   - Entre no diretório: `cd talktoyourdata`
   - Inicialize o ambiente DEV: `make install-dev`

## 🌊 Fluxo de Trabalho (GitFlow & Makefile)

Para garantir a qualidade, o TTYD utiliza um **Fluxo de Promoção** automatizado. Use o comando interativo:

```bash
make flow
```

### 1. Etapa [DEV] (Branch `develop`)

- **Git Strategy**: Trabalhe sempre na branch `develop`.

- **Naming Convention**: Crie branches a partir da `develop` usando os prefixos:
  - `feature/nome-da-feature`
  - `fix/correcao-de-bug`
  - `chore/tarefas-manutencao`
- **Ciclo Automático (Opção 1 do `make flow`)**:
  1. `make install-dev`: Instala dependências e gera `.env.dev`.
  2. `make dev-full`: Inicia Backend e Diagnósticos via `tmux`.
  3. `make test-dev`: Executa a suíte de testes em modo Mock/Offline.

---

## 🧪 Qualidade de Código

Execute estes comandos antes de abrir qualquer Pull Request para a `develop`:

```bash
make lint    # Análise Estática (Ruff)
make format  # Formatação Automática (Ruff)
make test    # Validação Completa
```

---

## 🐳 Execução via Docker (Recomendado)

Para rodar a stack do Backend em container:

```bash
make docker-dev-start
```

Isso iniciará o backend em modo **Offline/Mock**, ideal para desenvolvimento de features sem custo de AWS.

---

## 💡 Dicas de Desenvolvimento

### Conflito de Portas

Se receber erro de `Address already in use`, certifique-se de que não há containers rodando: `make down`.

### tmux (Ambiente Completo)

O comando `make dev-full` abre uma sessão interativa com múltiplos terminais:

- `Ctrl + b` seguido de `d`: Detach (sai sem fechar).
- `tmux attach -t ttyd_dev`: Volta para a sessão.

---

## 🛡️ Arquitetura e Pilares de Maturidade — LEVEL 19 (Ambiente DEV)

O ambiente **DEV** opera sob o padrão de maturidade **LEVEL 19 (Observability & Tracing)** do TTYD em modo **Offline/Mock**:

1. **Isolamento de Nuvem**: Todas as chamadas para IA e integrações de banco de dados (S3/DynamoDB) são mockadas localmente ou redirecionadas para containers offline, garantindo velocidade de desenvolvimento sem faturamento ou dependência da rede corporativa da AWS.
2. **Observabilidade Local**: O tracing de requisições (`X-Correlation-Id`) e a correlação de logs assíncronos via `contextvars` estão ativos e configurados no backend. Você pode inspecionar os logs estruturados gerados nas corrotinas e threads diretamente na saída do terminal (`uvicorn` ou logs do Docker).
3. **Validação de Sintaxe**: A pipeline de testes locais (`make test-dev`) valida a integridade de sintaxe do código e formatos YAML antes da promoção para os ambientes integrados de nuvem.

---

## 🩺 Diagnóstico e Docs

- **Doctor**: `make doctor`
- **Swagger**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Redoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
