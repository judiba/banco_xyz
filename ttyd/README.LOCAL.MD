# ☁️ TTYD — Guia do Ambiente LOCAL (AWS Real)

Este guia descreve como rodar o backend do TTYD conectado aos serviços reais da AWS (Bedrock, S3, Redshift) a partir da sua máquina local.

---

## 🛠️ Requisitos para AWS Real

Para que este ambiente funcione, você precisa de:

1. **Credenciais AWS**: Configuradas no seu terminal (geralmente em `~/.aws/credentials`).
2. **AWS Profile**: Por padrão, o projeto utiliza o profile `default`. Você pode ajustar isso no arquivo `security/.env.local`.
3. **Permissões**: Sua conta AWS deve ter permissões para acessar o Amazon Bedrock (modelos Claude 3.5 Sonnet e Titan Embeddings).
4. **IAM Roles (LEVEL 19)**: Certifique-se de que a role utilizada possui as políticas necessárias para validação de identidade híbrida herdadas da segurança corporativa.

---

## 🌊 Fluxo de Promoção (Etapa LOCAL)

### 1. Promoção para Branch `main`

Após validar suas alterações em `develop` (Ambiente DEV), o código deve ser promovido para a branch `main` para validação em contexto de nuvem real.

### 2. Execução Automática (Opção 2 do `make flow`)

Para validar o ambiente local com recursos reais da AWS, utilize o fluxo interativo:

```bash
make flow
```

Escolha a **opção 2**. Isso executará automaticamente:
1.`make local`: Sobe a stack Docker usando as configurações do `.env.local`.
2.`make test-local`: Executa testes de integração diretamente contra o Amazon Bedrock e S3.

---

## 🔍 Diferenças do Ambiente DEV

* **LLM**: Em vez de mocks, as chamadas vão para o Amazon Bedrock.
* **Vectores**: O RAG utiliza embeddings reais gerados pelo Amazon Titan.
* **Logs**: Você pode acompanhar os logs reais da interação com os modelos AWS.

---

## 🛡️ Arquitetura e Pilares de Maturidade — LEVEL 19

O ambiente **LOCAL** opera sob o padrão de maturidade **LEVEL 19 (Observability & Tracing)** do TTYD, focando em segurança avançada, isolamento físico de repositórios, conformidade com a infraestrutura corporativa de nuvem e rastreabilidade total de execução.

Abaixo estão detalhados os pilares técnicos que sustentam esta entrega de engenharia:

### 1. Governança e Desacoplamento Físico

* **Exclusividade do Backend**: O repositório foi segregado fisicamente de qualquer código Streamlit (Interface) e dos portais de autenticação unificada (`Entra ID` / `IAM` externo), garantindo que esta base gerencie exclusivamente APIs FastAPI rápidas, Text-to-SQL estruturado e ingestão inteligente.
* **Redução de Superfície de Ataque**: Toda e qualquer infraestrutura local de produção (`prod`) foi purgada deste ciclo de testes locais para evitar vazamentos acidentais ou comandos destrutivos.

### 2. Segurança Híbrida e Injeção Dinâmica (Secrets Manager)

* **Zero Credenciais Estáticas**: Chaves sensíveis em ambiente integrado local (como conexões a bancos e arns) não ficam salvas em arquivos `.env` estáticos sob controle de versão.
* **Secrets Injetados em Memória**: Em tempo de execução, a Session ativa da AWS faz a busca dinâmica do secret `ttyd/local/config` no AWS Secrets Manager e popula em memória as variáveis para consumo pelo FastAPI e Bedrock, garantindo confidencialidade absoluta.

### 3. Automação e Resiliência de Pipelines

* **Automação Híbrida (`test-local`)**: O target `make test-local` injeta dinamicamente `APP_ENV=local` e roda as verificações integradas de qualidade semântica sobre os metadados do LLM (`validate_yaml_quality.py`).
* **Tratamento Híbrido Resiliente**: O validador cruza o dicionário de dados (`desc_colunas.yaml`) com a estrutura física de esquemas do **AWS Glue Data Catalog**. O teste de integração possui bypass amigável (`pytest.skip`) caso o catálogo físico na nuvem esteja offline ou em manutenção.

### 4. Provedores de IA Robustos e Conformidade Pydantic v2

* **Bypass de Limitações Pydantic**: Compatibilidade total do modelo `ChatBedrock` do ecossistema Amazon Bedrock acoplado com injeção direta de baixo nível via `object.__setattr__(self._bedrock_model, "stateful", True)` para evitar quebras por regras estritas de campos extras Pydantic v2.

### 5. Observabilidade e Rastreamento Correlacionado (LEVEL 19)

* **Tracing de Requisições Fim-a-Fim**: Através de um middleware FastAPI de alta performance, todas as requisições geram ou propagam um `X-Correlation-Id` único e expõem a latência exata do ciclo de vida HTTP.
* **Logs Assíncronos Correlacionados**: O uso de `contextvars` em conjunto com um `CorrelationIdFilter` customizado garante que qualquer log emitido durante a jornada assíncrona dos agentes carregue o mesmo ID de transação, permitindo a consolidação imediata de execuções concorrentes em ferramentas de análise de logs (Datadog, Splunk, CloudWatch).

---

## 🛑 Encerrando

Para parar os containers e liberar os recursos:

```bash
make down
```
