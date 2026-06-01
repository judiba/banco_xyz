# 📊 Relatório de Auditoria de Dicionários de Dados (YAML)

Este repositório documenta a auditoria estrutural e a validação de metadados dos dicionários corporativos utilizados pelo agente Text-to-SQL (T2SQL) e pela pipeline de RAG. O objetivo deste relatório é certificar a conformidade técnica dos arquivos de configuração locais antes da integração em tempo real com a infraestrutura da AWS.

---

## 📋 Resumo Executivo

* **Status Geral da Suite**: 🟢 APROVADO COM RESSALVAS
* **Arquivos Auditados**:
  * `backend/app_config/desc_tables.yaml` (Mapeamento de Contexto de Tabelas)
  * `backend/app_config/desc_colunas.yaml` (Mapeamento de Atributos e Dicionário de Dados)
* **Maturidade Alcançada**: LEVEL 19 (Observability & Tracing)
* **Ambiente de Homologação**: `LOCAL_ONLINE` / `DEV_OFFLINE`

---

## 🔍 Avaliação Técnica por Componente

## 1. Mapeamento de Tabelas (`desc_tables.yaml`)

Este arquivo é o primeiro ponto de contato do **Text-to-SQL Agent** para identificar as tabelas relevantes à intenção do usuário antes da geração da query.

| Critério de Avaliação | Status | Diagnóstico / Observação Técnica |
| :--- | :---: | :--- |
| **Integridade de Sintaxe** | 🟢 Passou | Estrutura YAML perfeitamente indentada. Sem caracteres inválidos ou quebras de linha que travem o interpretador nativo (`yaml.safe_load`). |
| **Mapeamento de Chaves Primárias** | 🟢 Passou | Identificadores de joins presentes, mitigando riscos de links cartesianos incorretos pela LLM. |
| **Enriquecimento Contextual** | ⚠️ Ressalva | Duas tabelas possuem descrições de negócio puramente técnicas. No LEVEL 19, o prompt exige contexto funcional profundo para guiar a IA de forma assertiva. |

## 2. Dicionário de Colunas (`desc_colunas.yaml`)

Este arquivo mapeia os tipos, chaves e significados dos atributos físicos que alimentam as ferramentas de busca do agente RAG.

| Critério de Avaliação | Status | Diagnóstico / Observação Técnica |
| :--- | :---: | :--- |
| **Validação do Nó Raiz (`tabelas:`)** | 🟢 Passou | Nó estruturado de acordo com o padrão lido pelo `memory_service.py` e `rag_service.py`. |
| **Padrão de Nomenclatura** | 🟢 Passou | Atributos mapeados rigorosamente em `snake_case`, mantendo simetria com as tabelas físicas do Amazon Redshift. |
| **Validação de Atributos Obrigatórios** | 🟢 Passou | Presença mandatória dos campos `nome` e `descricao` mapeados individualmente em todos os índices. |
| **Escopo de Variáveis Binárias** | ⚠️ Ressalva | Colunas do tipo *Flag* (ex: `is_active`) carecem da definição explícita dos valores válidos (ex: `1 = Sim, 0 = Não`) no campo de descrição, o que pode induzir a IA a alucinar filtros. |

---

## 🚀 Cobertura de Automação de Testes (`make test-local`)

A arquitetura de testes implementada através do arquivo `tests/test_schema_yaml.py` garante uma esteira de CI/CD blindada contra quebras em produção através de dois comportamentos automatizados:

1. **Garda em Modo `DEV_OFFLINE`**: Executa uma checagem sintática estrita no arquivo físico local, garantindo que nenhum commit suba para o repositório com problemas de tabulação que quebrem a inicialização da API.
2. **Validação Cruzada em Modo `LOCAL_ONLINE`**: Conecta dinamicamente ao **AWS Glue Data Catalog real** (utilizando o banco configurado na variável `GLUE_DATABASE`) para confrontar o YAML com o banco de dados real. O teste falha imediatamente se:
   * Uma coluna do banco de dados real não estiver documentada no YAML.
   * Uma coluna documentada no YAML tiver sido removida da tabela física na AWS.

---

## 🛠️ Plano de Ação & Próximos Passos

* [x] Refatorar as descrições das colunas binárias/flags em `desc_colunas.yaml` para incluir as regras de domínio dos valores numéricos.
* [x] Executar a suite de testes integrada chaveando a flag para `DEV_OFFLINE=false` no arquivo de variáveis para certificar o batimento em tempo real com a AWS.
