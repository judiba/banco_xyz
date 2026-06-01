# TTYD — DEVOS LEVEL 19
############################################

PROJECT := ttyd
PYTHON ?= poetry run python
POETRY ?= poetry
ENV ?= local

ENV_DEV=security/.env.dev
ENV_LOCAL=security/.env.local
ENV_PROD=security/.env.prod

COMPOSE_DEV=deploy/docker-compose.dev.yml
COMPOSE_LOCAL=deploy/docker-compose.local.yml
COMPOSE_PROD=deploy/docker-compose.prod.yml

MAKEFLAGS += --no-print-directory

.DEFAULT_GOAL := help
.PHONY: help flow env-dev env-local env-prod env-check install-all install-dev install-local install-prod install-aws-cli test test-dev test-local test-prod lint format docker-dev-up docker-dev-start docker-dev-stop docker-dev-restart docker-dev-logs docker-dev-shell docker-dev-test up down stop-local dev-full local-full prod-full dev local prod restart restart-backend logs tf-init tf-plan tf-up tf-down infra-up infra-down infra-up-local infra-down-local secrets-check-local push-secrets-local agents health swagger docs doctor clean reset
############################################
# HELP
############################################

help:
	@echo ""
	@echo "  \033[1;36mTTYD - Operações e Deploy\033[0m"
	@echo "  ──────────────────────────────────────────"
	@echo "  \033[1;33m💡 Dica:\033[0m Use 'make <target>' para executar um comando."
	@echo ""
	@echo "  \033[1;32mGERAL:\033[0m"
	@echo "  make help               	📖 Ajuda"
	@echo "  make flow               	🌊 Fluxo de Promoção Interativo"
	@echo "  make docs               	📄 Gerar documentação (README)"
	@echo ""
	@echo "  \033[1;32mINSTALAÇÃO:\033[0m"
	@echo "  make install-all          	🧪 Instalação completa (Todos os grupos)"
	@echo "  make install-dev        	📦 Instalação DEV (Backend + Mock)"
	@echo "  make install-local      	☁️ Instalação LOCAL (AWS Real Services)"
	@echo ""
	@echo "  \033[1;32mAMBIENTES:\033[0m"
	@echo "  make dev-full           	📦 Ambiente DEV (Backend + Mock + Test) via tmux"
	@echo "  make dev               	📦 Ambiente DEV (Backend local)"
	@echo "  make docker-dev-up     	🐳 Stack DEV Docker (Background)"
	@echo "  make docker-dev-stop   	🐳 Stack DEV Docker (Parar)"
	@echo "  make docker-dev-restart	🐳 Stack DEV Docker (Reiniciar)"
	@echo "  make docker-dev-logs   	🐳 Stack DEV Docker (Logs)"
	@echo "  make local-full         	☁️ Stack LOCAL (AWS Real Services + Mock + Test) via tmux"
	@echo "  make local             	☁️ Stack LOCAL (AWS Real Services)"
	@echo "  make prod-full          	🏭 Stack PROD (AWS Real Services + Mock + Test) via tmux"
	@echo "  make prod               	🏭 Stack PROD (AWS Real Services)"
	@echo ""
	@echo "  \033[1;32mINFRAESTRUTURA:\033[0m"
	@echo "  make infra-up          	🏗️ Terraform Apply (LOCAL por padrão)"
	@echo "  make infra-down        	🗑️ Terraform Destroy (LOCAL por padrão)"
	@echo ""
	@echo "  \033[1;32mMANUTENÇÃO:\033[0m"
	@echo "  make down              	🛑 Parar todos os containers"
	@echo "  make clean             	🧹 Limpeza de caches e volumes"
	@echo "  make reset             	🔥 Hard Reset do ambiente"
	@echo ""
	@echo "  \033[1;32mQUALIDADE:\033[0m"
	@echo "  make test               	✅ Todos os testes"
	@echo "  make test-dev          	📦 Testes DEV (Mock)"
	@echo "  make test-local        	☁️ Testes LOCAL (AWS Real)"
	@echo "  make lint              	🔎 Análise (Ruff)"
	@echo "  make format            	🎨 Formatação"
	@echo ""
	@echo "  ──────────────────────────────────────────"
	@echo "  \033[1;34mBy: @jdionizb\033[0m"
	@echo "  ──────────────────────────────────────────"

############################################
# FLUXO DE PROMOÇÃO
############################################

flow:
	@echo ""
	@echo "\033[1;36m🌊 Fluxo de Promoção TTYD\033[0m"
	@echo "\033[1;34m==========================\033[0m"
	@echo "\033[1;32m1. [DEV]\033[0m   Instalar, Iniciar (tmux) e Testar"
	@echo "          \033[0;90m(make install-dev -> make dev-full -> make test-dev)\033[0m"
	@echo ""
	@echo "\033[1;33m2. [LOCAL]\033[0m Subir Stack Local e Testar AWS Real"
	@echo "          \033[0;90m(make install-local -> make local-full -> make test-local)\033[0m"
	@echo ""
	@echo "\033[1;35m3. [PROD]\033[0m Instalar e Subir Stack PROD (AWS Real + Mock)"
	@echo "          \033[0;90m(make install-prod)\033[0m"
	@echo "\033[1;34m==========================\033[0m"
	@read -p "Escolha a etapa para execução automática (1-3) ou 'q' para sair: " choice; \
	case "$$choice" in \
		1) echo "🚀 Iniciando Ciclo DEV..."; make install-dev && make dev-full && make test-dev ;; \
		2) echo "☁️ Iniciando Ciclo LOCAL..."; make install-local && make local-full ;; \
		3) echo "🏭 Iniciando Ciclo PROD..."; make install-prod && make prod-full ;; \
		q) echo "Saindo..."; exit 0 ;; \
		*) echo "\033[1;31mOpção inválida.\033[0m"; exit 1 ;; \
	esac

env-dev:
	@$(PYTHON) scripts/generate_environments.py --env dev

env-local:
	@$(PYTHON) scripts/generate_environments.py --env local

env-prod:
	@$(PYTHON) scripts/generate_environments.py --env prod

# Verifica se os .env já existem e NÃO os sobrescreve se tiverem conteúdo.
# Use 'make env-dev/local/prod' explicitamente para forçar regeneração.
env-check:
	@missing=0; \
	for f in $(ENV_DEV) $(ENV_LOCAL) $(ENV_PROD); do \
		if [ ! -s "$$f" ]; then \
			echo "⚠️  $$f não encontrado ou vazio — gerando a partir do template..."; \
			missing=1; \
		else \
			echo "🔒 $$f já existe e está preservado."; \
		fi; \
	done; \
	if [ "$$missing" = "1" ]; then \
		[ -s "$(ENV_DEV)" ] || $(PYTHON) scripts/generate_environments.py --env dev; \
		[ -s "$(ENV_LOCAL)" ] || $(PYTHON) scripts/generate_environments.py --env local; \
		[ -s "$(ENV_PROD)" ] || $(PYTHON) scripts/generate_environments.py --env prod; \
	fi
	@echo "✅ Verificação concluida."

# Cria tabelas ttyd-* na AWS (não use DYNAMODB_ENDPOINT)
dynamodb-aws:
	@if [ -n "$$DYNAMODB_ENDPOINT" ]; then \
		echo "❌ DYNAMODB_ENDPOINT está definido — para AWS real, deixe vazio."; \
		exit 1; \
	fi
	@$(PYTHON) scripts/create_dynamodb_tables.py
	@echo "✅ Tabelas criadas/verificadas na AWS ($${AWS_REGION:-us-east-1})"

install-dev: env-dev
	@if ! command -v $(POETRY) >/dev/null 2>&1; then \
		echo "❌ Poetry não encontrado. Instale: pip3 install poetry"; \
		echo "   Ou use: make up  (Docker, sem Poetry no host)"; \
		exit 1; \
	fi
	@echo "📦 [DEV] Instalando dependências via Poetry..."
	@$(POETRY) install
	@echo "✅ Instalação concluida."

install-local: env-local
	@if ! command -v $(POETRY) >/dev/null 2>&1; then \
		echo "❌ Poetry não encontrado. Instale: pip3 install poetry"; \
		exit 1; \
	fi
	@echo "☁️ [LOCAL] Instalando dependências via Poetry..."
	@$(POETRY) install
	@echo "✅ Instalação LOCAL concluída."

install-prod: env-prod
	@if ! command -v $(POETRY) >/dev/null 2>&1; then \
		echo "❌ Poetry não encontrado. Instale: pip3 install poetry"; \
		exit 1; \
	fi
	@echo "🏭 [PROD] Instalando dependências via Poetry..."
	@$(POETRY) install --only main
	@echo "✅ Instalação PROD concluída."

install-all: env-check
	@if ! command -v $(POETRY) >/dev/null 2>&1; then \
		echo "❌ Poetry não encontrado. Instale: pip3 install poetry"; \
		exit 1; \
	fi
	@echo "🧪 Instalando todos os grupos de dependências..."
	@$(POETRY) install --all-extras
	@echo "✅ Instalação completa concluída."

############################################
# AWS CLI
############################################

install-aws-cli:
	@echo "☁️ Instalando AWS CLI..."
	@if ! command -v aws >/dev/null 2>&1; then \
		sudo snap install aws-cli --channel=v1/stable --classic; \
	else \
		echo "✅ AWS CLI já instalado."; \
	fi

############################################
# QUALITY & TESTING
############################################

test: test-dev test-local env-check
	@echo "🏁 Todos os testes foram finalizados."

test-dev: env-check
	@echo "📦 [DEV] Executando testes em modo Mock/Offline..."
	@APP_ENV=dev DEV_OFFLINE=true $(POETRY) run pytest tests/ -v -m "not aws_real" -W ignore::DeprecationWarning
	@echo "✅ Testes finalizados."

# ============================================================================
# TARGET DE TESTES DA PIPELINE LOCAL (LEVEL 19)
# ============================================================================

test-local:
	@echo "🔍 [LEVEL 19] Iniciando suite de testes locais corporativos..."
	@echo "📄 Carregando variáveis de escopo do .env.local..."
	@if [ ! -f security/.env.local ]; then \
		echo "❌ Erro: Arquivo security/.env.local não encontrado!"; \
		exit 1; \
	fi
	@# 1. Executa a validação de qualidade textual e de negócios das tabelas e colunas
	@APP_ENV=local $(POETRY) run python scripts/validate_yaml_quality.py
	@# 2. Executa o teste de integridade sintática e de batimento de esquemas
	@APP_ENV=local $(POETRY) run pytest tests/test_schema_yaml.py -v -W ignore::DeprecationWarning
	@# 3. Executa os demais testes unitários e de integração de todo o ecossistema (LEVEL 19)
	@if [ -d tests ]; then \
		APP_ENV=local $(POETRY) run pytest tests/ -v -W ignore::DeprecationWarning; \
	else \
		echo "⚠️ Pasta tests não encontrada; pulando."; \
	fi
	@echo "✅ Suite de validação concluída com sucesso!"

lint:
	@echo "🔎 Analisando qualidade de código..."
	@$(POETRY) run ruff check .
	@echo "✅ Verificação concluída."

format:
	@echo "🎨 Formatando código automaticamente..."
	@$(POETRY) run ruff format .
	@echo "✅ Código formatado."

############################################
# DOCKER COMPOSE DEV
############################################

docker-dev-up:
	@echo "📦 [DEV] Iniciando stack DEV..."
	@docker compose --env-file $(ENV_DEV) -f $(COMPOSE_DEV) up --build --remove-orphans --force-recreate
	@echo "✅ Stack DEV iniciada."

docker-dev-start: env-dev
	@echo "📦 [DEV] Iniciando stack DEV..."
	@docker compose --env-file $(ENV_DEV) -f $(COMPOSE_DEV) up --build
	@echo "✅ Stack DEV iniciada."

docker-dev-stop:
	@echo "🛑 [DEV] Parando stack DEV..."
	@docker compose --env-file $(ENV_DEV) -f $(COMPOSE_DEV) down

docker-dev-restart: docker-dev-stop docker-dev-start

docker-dev-logs:
	@echo "📝 [DEV] Exibindo logs do stack DEV..."
	@docker compose --env-file $(ENV_DEV) -f $(COMPOSE_DEV) logs -f

docker-dev-shell:
	@echo "🐳 Acessando shell do container backend DEV..."
	@docker compose --env-file $(ENV_DEV) -f $(COMPOSE_DEV) exec backend bash
	@echo "✅ Shell do container DEV finalizado."

docker-dev-test:
	@echo "🧪 Executando testes dentro do container DEV..."
	@docker compose --env-file $(ENV_DEV) -f $(COMPOSE_DEV) run --rm backend $(POETRY) run pytest -v -m "not aws_real" -W ignore::DeprecationWarning
	@echo "✅ Testes no container DEV finalizados."

############################################
# DOCKER COMPOSE LOCAL
############################################
# Docker compose não precisa do wrapper do poetry
up:
	@echo "🐳 Subindo stack DEV (Docker)..."
	@docker compose --env-file $(ENV_DEV) -f $(COMPOSE_DEV) up -d --build
	@echo "✅ Containers DEV ativos."

down: stop-local
	@echo "🛑 Parando containers..."
	@echo "🛑 Parando infraestrutura e containers ativos..."
	@-docker compose --env-file $(ENV_DEV) -f $(COMPOSE_DEV) down --remove-orphans
	@echo "✅ Sistema interrompido."

stop-local:
	@echo "🛑 Parando stack LOCAL (AWS Real)..."
	@-docker compose -f $(COMPOSE_LOCAL) down --remove-orphans >/dev/null 2>&1 || true
	@-fuser -k 8000/tcp >/dev/null 2>&1 || true
	@echo "✅ Infraestrutura parada."

dev: install-dev
	@echo "📦 Iniciando DEV runtime (Offline/Mock)..."
	@$(POETRY) run python3 -m uvicorn backend.main:app --reload --env-file $(ENV_DEV)
	@echo "✅ DEV runtime iniciado."

dev-full:
	@echo "🔄 Reiniciando ambiente completo DEV no tmux..."
	@if ! command -v tmux >/dev/null 2>&1; then \
		echo "❌ tmux não instalado."; \
		echo "👉 Instale com: sudo apt install tmux"; \
		exit 1; \
	fi

	@if tmux has-session -t ttyd_dev 2>/dev/null; then \
		tmux kill-session -t ttyd_dev; \
	fi

	@tmux new-session -d -s ttyd_dev
	@tmux set-option -t ttyd_dev -g mouse on
	@tmux send-keys -t ttyd_dev 'make docker-dev-start' C-m
	@sleep 3
	@tmux split-window -h -t ttyd_dev
	@tmux send-keys -t ttyd_dev:0.1 'make test-dev' C-m
	@tmux split-window -v -t ttyd_dev
	@tmux send-keys -t ttyd_dev:0.2 'make doctor && make docs' C-m
	@tmux select-layout -t ttyd_dev tiled
	@echo "✅ Ambiente DEV iniciado no tmux."

	@tmux attach-session -t ttyd_dev
	@echo "🧪 Ambiente completo iniciado no tmux."
	@echo "📦 Ambiente DEV ativo acesse http://localhost:8000."
	@echo "✅ Ambiente TEST ativo acesse http://localhost:8000/test."
	@echo "💡 Ambiente DOCTOR ativo acesse http://localhost:8000/doctor."
	@echo "📄 Ambiente DOCS ativo acesse http://localhost:8000/docs."
	@echo ""
	@echo "========================================="
	@echo "👷️  By: @jdionizb"
	@echo "========================================="

local: env-local
	@echo "☁️ Subindo stack LOCAL (AWS Real)..."
	@docker compose --env-file $(ENV_LOCAL) -f $(COMPOSE_LOCAL) up -d --build
	@echo "✅ Containers LOCAL ativos em http://localhost:8000"

local-full:
	@echo "🔄 Reiniciando ambiente completo LOCAL no tmux..."
	@if ! command -v tmux >/dev/null 2>&1; then \
		echo "❌ tmux não instalado."; \
		echo "👉 Instale com: sudo apt install tmux"; \
		exit 1; \
	fi

	@if tmux has-session -t ttyd_local 2>/dev/null; then \
		tmux kill-session -t ttyd_local; \
	fi

	@tmux new-session -d -s ttyd_local
	@tmux set-option -t ttyd_local -g mouse on
	@tmux send-keys -t ttyd_local 'make local' C-m
	@sleep 3
	@tmux split-window -h -t ttyd_local
	@tmux send-keys -t ttyd_local:0.1 'make test-local' C-m
	@tmux split-window -v -t ttyd_local
	@tmux send-keys -t ttyd_local:0.2 'make doctor && make docs' C-m
	@tmux select-layout -t ttyd_local tiled
	@tmux attach-session -t ttyd_local
	@echo "📦 Ambiente completo iniciado no tmux."
	@echo "☁️ Ambiente LOCAL ativo. Acesse http://localhost:8000."
	@echo "✅ Ambiente TEST ativo. Acesse http://localhost:8000/test."
	@echo "💡 Ambiente DOCTOR ativo. Acesse http://localhost:8000/doctor."
	@echo "📄 Ambiente DOCS ativo. Acesse http://localhost:8000/docs."
	@echo ""
	@echo "========================================="
	@echo "👷️  By: @jdionizb"
	@echo "========================================="


prod: env-prod
	@echo "🏭 Subindo stack PROD (AWS Real)..."
	@docker compose --env-file $(ENV_PROD) -f $(COMPOSE_PROD) up -d --build
	@echo "✅ Containers PROD ativos em http://localhost:8000"

prod-full:
	@echo "🔄 Reiniciando ambiente completo PROD no tmux..."
	@if ! command -v tmux >/dev/null 2>&1; then \
		echo "❌ tmux não instalado."; \
		echo "👉 Instale com: sudo apt install tmux"; \
		exit 1; \
	fi
	@if tmux has-session -t ttyd_prod 2>/dev/null; then \
		tmux kill-session -t ttyd_prod; \
	fi
	@tmux new-session -d -s ttyd_prod
	@tmux set-option -t ttyd_prod -g mouse on
	@tmux send-keys -t ttyd_prod 'make prod' C-m
	@sleep 3
	@tmux split-window -h -t ttyd_prod
	@tmux send-keys -t ttyd_prod:0.1 'make doctor && make docs' C-m
	@tmux select-layout -t ttyd_prod tiled
	@tmux attach-session -t ttyd_prod

restart:
	@echo "🔄 Reiniciando stack DEV..."
	docker compose --env-file $(ENV_DEV) -f $(COMPOSE_DEV) down
	docker compose --env-file $(ENV_DEV) -f $(COMPOSE_DEV) up -d --build --remove-orphans
	@echo "✅ Stack de DEV reiniciada."

restart-backend:
	docker compose --env-file $(ENV_DEV) -f $(COMPOSE_DEV) up -d --build backend
	@echo "✅ Container backend reiniciado."

logs:
	docker compose --env-file $(ENV_DEV) -f $(COMPOSE_DEV) logs

# ====================================================================
# INFRASTRUCTURE (Terraform)
# ====================================================================

tf-init:
	@echo "🔧 Inicializando Terraform..."
	@cd terraform && terraform init

# make tf-plan ENV=local
tf-plan:
	@echo "📋 Planejando infraestrutura [$(ENV)]..."
	@cd terraform && terraform plan -var-file="$(ENV).tfvars"

# make tf-up ENV=local
tf-up:
	@echo "🏗️  Aplicando infraestrutura [$(ENV)]..."
	@cd terraform && terraform init && terraform apply -var-file="$(ENV).tfvars" -auto-approve

# make tf-down ENV=local
tf-down:
	@cd terraform && terraform destroy -var-file="$(ENV).tfvars" -auto-approve

# Atalhos por ambiente

infra-up: infra-up-local
infra-down: infra-down-local

infra-up-local:
	@$(MAKE) tf-up ENV=local

infra-down-local:
	@$(MAKE) tf-down ENV=local

# ====================================================================
# SECRETS MANAGER
# ====================================================================

# Dry-run: valida sem chamar AWS
secrets-check-local:
	@echo "🔐 Validando secrets LOCAL (dry-run)..."
	@$(POETRY) run python scripts/push_secrets.py --env local --dry-run

# Push real para AWS Secrets Manager (requer confirmação interativa)
push-secrets-local:
	@$(POETRY) run python scripts/push_secrets.py --env local

############################################
# OBSERVABILITY
############################################

agents:
	@echo "🤖 Status dos Agentes no Docker..."
	@docker ps --format "table {{.Names}}\t{{.Status}}"

health:
	@curl http://localhost:8000/health

swagger:
	@xdg-open http://localhost:8000/docs || true

############################################
# DOCUMENTATION
############################################

docs:
	@echo "📄 Gerando README.md atualizado..."
	@$(POETRY) run python scripts/generate_readme.py
	@echo "✅ Documentação pronta."

############################################
# DIAGNOSTICS & CLEANUP
############################################

doctor:
	@echo "🩺 Validando ambiente LEVEL 19..."
	@$(POETRY) check
	@$(POETRY) run python3 scripts/generate_doctor.py
	@docker --version
	@tmux -V
	@terraform -version
	@aws --version || true
	@echo "✅ Ambiente validado."

test-api-v1:
	@echo "🧪 Executando teste de integração da API v1..."
	@$(POETRY) run python3 scripts/test_api_v1.py

# Limpeza segura — preserva TODOS os .env da pasta security/ (incluindo security/.env)
clean:
	@echo "🧹 Limpando caches e containers parados..."
	@-docker compose --env-file $(ENV_DEV) -f $(COMPOSE_DEV) down -v --remove-orphans 2>/dev/null || true
	@-rm -rf .pytest_cache .ruff_cache .mypy_cache
	@-find . -path ./security -prune -o -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@-echo "🧹 Limpeza completa."
	@echo "🔒 Arquivos .env em . PRESERVADOS (nunca removidos automaticamente):"
	@echo "✅ Limpeza concluída."

# Ajustado para garantir que a limpeza ocorra antes da tentativa de instalação
reset: clean
	@echo "🔥 HARD RESET: Fazendo backup dos .env antes de resetar..."
	@BACKUP_DIR="/tmp/ttyd_env_backup_$$(date +%Y%m%d_%H%M%S)"; \
	mkdir -p "$$BACKUP_DIR"; \
	[ -f security/.env ] && cp security/.env "$$BACKUP_DIR/.env" && echo "💾 security/.env salvo." || true; \
	cp security/.env.* "$$BACKUP_DIR/" 2>/dev/null && echo "💾 Backup completo salvo em: $$BACKUP_DIR" || echo "⚠️  Nenhum .env.* para backup."; \
	echo "🗑️  Limpando Docker e Poetry..."; \
	docker system prune -af --volumes; \
	$(POETRY) env remove --all 2>/dev/null || true; \
	echo "🔄 Restaurando .env do backup..."; \
	[ -f "$$BACKUP_DIR/.env" ] && cp "$$BACKUP_DIR/.env" security/.env && echo "✅ security/.env restaurado." || true; \
	cp "$$BACKUP_DIR"/.env.* security/ 2>/dev/null && echo "✅ .env.* restaurados com sucesso." || echo "⚠️  Nenhum .env.* para restaurar."
	@echo "✅ Ambiente resetado. Todos os .env foram preservados."
