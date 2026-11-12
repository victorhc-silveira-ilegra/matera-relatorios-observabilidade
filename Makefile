SHELL := /bin/bash

RESOLVE_PY := $(shell bash linters/git-hooks/bin/resolve_venv_python.sh 2>/dev/null || echo .venv/bin/python)
PYTHON := $(RESOLVE_PY)

WINDOW ?= 10:30-13:30
DATE ?=
RESPONSAVEL ?= "Victor Silveira"
CHAMADOS ?= "Sem ocorrências."
CHAMADOS_HML ?= "Sem ocorrências."
CHAMADOS_PRD ?= "Sem ocorrências."
OUTPUT ?=
SKIP_RDS ?= 0

GREEN  := \033[1;32m
YELLOW := \033[1;33m
BLUE   := \033[1;34m
CYAN   := \033[1;36m
RED    := \033[1;31m
RESET  := \033[0m

.DEFAULT_GOAL := help

.PHONY: help app-setup app-install app-clean app-quality app-ci app-lint app-security app-test app-tests \
	app-validate app-build app-format app-dead-code app-audit app-pre-commit app-pre-commit-install app-pre-commit-run \
	quality ci lint security test tests validate build format dead-code audit setup install clean pre-commit-install pre-commit-run git-init \
	report-flagship report-flagship-0830 report-flagship-1030 report-flagship-1330 \
	report-flagship-fast report-flagship-auto report-flagship-all \
	report-revolut report-revolut-0830 report-revolut-1030 report-revolut-1330 \
	report-revolut-auto report-revolut-all report-all

help:
	@echo -e "$(BLUE)========================================================================$(RESET)"
	@echo -e "$(GREEN)       RELATORIOS DE OBSERVABILIDADE - MENU OPERACIONAL                 $(RESET)"
	@echo -e "$(BLUE)========================================================================$(RESET)"
	@echo -e "Uso: $(CYAN)make <comando> [VARIAVEIS]$(RESET)"
	@echo -e ""
	@echo -e "$(YELLOW)Interpretador Python:$(RESET) $(PYTHON)"
	@echo -e ""
	@echo -e "$(YELLOW)Cadeia de Horarios - Flagship (DTW):$(RESET)"
	@echo -e "  $(GREEN)report-flagship$(RESET)         - Gera relatorio Flagship (WINDOW=$(WINDOW))"
	@echo -e "  $(GREEN)report-flagship-0830$(RESET)    - Janela Manha (08:30–10:30)"
	@echo -e "  $(GREEN)report-flagship-1030$(RESET)    - Janela Meio-dia (10:30–13:30)"
	@echo -e "  $(GREEN)report-flagship-1330$(RESET)    - Janela Tarde (13:30–16:30)"
	@echo -e "  $(GREEN)report-flagship-fast$(RESET)    - Execucao rapida (bypass scraping RDS via --skip-rds)"
	@echo -e "  $(GREEN)report-flagship-auto$(RESET)    - Detecta automaticamente a janela pelo relogio"
	@echo -e "  $(GREEN)report-flagship-all$(RESET)     - Executa sequencialmente toda a cadeia do dia"
	@echo -e ""
	@echo -e "$(YELLOW)Cadeia de Horarios - Revolut (MIP):$(RESET)"
	@echo -e "  $(GREEN)report-revolut$(RESET)          - Gera relatorio Revolut (WINDOW=$(WINDOW))"
	@echo -e "  $(GREEN)report-revolut-0830$(RESET)     - Janela Manha (08:30–10:30)"
	@echo -e "  $(GREEN)report-revolut-1030$(RESET)     - Janela Meio-dia (10:30–13:30)"
	@echo -e "  $(GREEN)report-revolut-1330$(RESET)     - Janela Tarde (13:30–16:30)"
	@echo -e "  $(GREEN)report-revolut-auto$(RESET)     - Detecta automaticamente a janela pelo relogio"
	@echo -e "  $(GREEN)report-revolut-all$(RESET)      - Executa sequencialmente toda a cadeia do dia"
	@echo -e ""
	@echo -e "$(YELLOW)Operacoes Consolidadas:$(RESET)"
	@echo -e "  $(GREEN)report-all$(RESET)              - Executa toda a cadeia de Flagship e Revolut"
	@echo -e ""
	@echo -e "$(YELLOW)Matriz de Qualidade & CI/CD:$(RESET)"
	@echo -e "  $(GREEN)app-quality$(RESET)             - Executa todos os 5 estagios da Matriz de Qualidade (ou app-ci)"
	@echo -e "  $(GREEN)app-lint$(RESET)                - Estagio 1: Ruff check, format, Mypy strict e Vulture"
	@echo -e "  $(GREEN)app-security$(RESET)            - Estagio 2: Bandit SAST e Pip-Audit contra CVEs"
	@echo -e "  $(GREEN)app-test$(RESET)                - Estagio 3: Pytest com 100% de branch coverage (ou app-tests)"
	@echo -e "  $(GREEN)app-validate$(RESET)            - Estagio 4: Valida estrutura de arquivos e teto de linhas"
	@echo -e "  $(GREEN)app-build$(RESET)               - Estagio 5: Empacota a distribuicao wheel"
	@echo -e "  $(GREEN)app-format$(RESET)              - Auto-formatacao e organizacao de imports com Ruff"
	@echo -e "  $(GREEN)app-dead-code$(RESET)           - Deteccao de codigo morto com Vulture"
	@echo -e "  $(GREEN)app-audit$(RESET)               - Auditoria de CVEs nas dependencias"
	@echo -e ""
	@echo -e "$(YELLOW)Ambiente & Git Hooks:$(RESET)"
	@echo -e "  $(GREEN)app-setup$(RESET)               - Bootstrap completo: .venv + deps + git-hooks"
	@echo -e "  $(GREEN)app-install$(RESET)             - Instala e atualiza dependencias no .venv"
	@echo -e "  $(GREEN)app-pre-commit$(RESET)          - Instala hooks locais de pre-commit e commit-msg"
	@echo -e "  $(GREEN)app-pre-commit-run$(RESET)      - Executa hooks de pre-commit em todos os arquivos"
	@echo -e "  $(GREEN)app-clean$(RESET)               - Remove caches, artefatos de build e relatorios temporarios"
	@echo -e "$(BLUE)========================================================================$(RESET)"

report-flagship:
	$(PYTHON) -m app.presentation.cli --client flagship --window $(WINDOW) \
		$(if $(DATE),--date $(DATE),) \
		$(if $(filter 1 true TRUE,$(SKIP_RDS)),--skip-rds,) \
		--chamados-hml $(CHAMADOS_HML) \
		--chamados-prd $(CHAMADOS_PRD) \
		$(if $(OUTPUT),--output $(OUTPUT),)

report-flagship-0830:
	$(MAKE) report-flagship WINDOW=08:30-10:30

report-flagship-1030:
	$(MAKE) report-flagship WINDOW=10:30-13:30

report-flagship-1330:
	$(MAKE) report-flagship WINDOW=13:30-16:30

report-flagship-fast:
	$(MAKE) report-flagship SKIP_RDS=1

report-flagship-auto:
	$(PYTHON) -m app.presentation.cli --client flagship \
		$(if $(DATE),--date $(DATE),) \
		$(if $(filter 1 true TRUE,$(SKIP_RDS)),--skip-rds,) \
		--chamados-hml $(CHAMADOS_HML) \
		--chamados-prd $(CHAMADOS_PRD) \
		$(if $(OUTPUT),--output $(OUTPUT),)

report-flagship-all:
	@echo -e "$(CYAN)>>> Executando Cadeia Flagship (08:30-10:30)...$(RESET)"
	$(MAKE) report-flagship-0830
	@echo -e "$(CYAN)>>> Executando Cadeia Flagship (10:30-13:30)...$(RESET)"
	$(MAKE) report-flagship-1030
	@echo -e "$(CYAN)>>> Executando Cadeia Flagship (13:30-16:30)...$(RESET)"
	$(MAKE) report-flagship-1330

report-revolut:
	$(PYTHON) -m app.presentation.cli --client revolut --window $(WINDOW) \
		$(if $(DATE),--date $(DATE),) \
		--responsavel $(RESPONSAVEL) \
		--chamados $(CHAMADOS) \
		$(if $(OUTPUT),--output $(OUTPUT),)

report-revolut-0830:
	$(MAKE) report-revolut WINDOW=08:30-10:30

report-revolut-1030:
	$(MAKE) report-revolut WINDOW=10:30-13:30

report-revolut-1330:
	$(MAKE) report-revolut WINDOW=13:30-16:30

report-revolut-auto:
	$(PYTHON) -m app.presentation.cli --client revolut \
		$(if $(DATE),--date $(DATE),) \
		--responsavel $(RESPONSAVEL) \
		--chamados $(CHAMADOS) \
		$(if $(OUTPUT),--output $(OUTPUT),)

report-revolut-all:
	@echo -e "$(CYAN)>>> Executando Cadeia Revolut (08:30-10:30)...$(RESET)"
	$(MAKE) report-revolut-0830
	@echo -e "$(CYAN)>>> Executando Cadeia Revolut (10:30-13:30)...$(RESET)"
	$(MAKE) report-revolut-1030
	@echo -e "$(CYAN)>>> Executando Cadeia Revolut (13:30-16:30)...$(RESET)"
	$(MAKE) report-revolut-1330

report-all:
	@echo -e "$(YELLOW)========================================================================$(RESET)"
	@echo -e "$(GREEN)               CADEIA COMPLETA DE RELATORIOS DIARIOS                    $(RESET)"
	@echo -e "$(YELLOW)========================================================================$(RESET)"
	$(MAKE) report-flagship-all
	$(MAKE) report-revolut-all

app-quality app-ci:
	$(PYTHON) scripts/quality_gate.py

app-lint:
	$(PYTHON) scripts/quality_gate.py --stage lint

app-security:
	$(PYTHON) scripts/quality_gate.py --stage security

app-test app-tests:
	$(PYTHON) scripts/quality_gate.py --stage test

app-validate:
	$(PYTHON) scripts/quality_gate.py --stage validate

app-build:
	$(PYTHON) scripts/quality_gate.py --stage build

app-format:
	$(PYTHON) -m ruff format app tests scripts
	$(PYTHON) -m ruff check --fix app tests scripts

app-dead-code:
	$(PYTHON) -m vulture --min-confidence 80 app

app-audit:
	$(PYTHON) -m pip_audit -r requirements.txt

app-setup: app-install app-pre-commit
	@echo -e "$(GREEN)Ambiente e git-hooks inicializados com sucesso.$(RESET)"

app-install:
	@test -d .venv || python3 -m venv .venv
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt -r requirements-dev.txt

app-pre-commit app-pre-commit-install: git-init
	bash linters/git-hooks/install.sh
	chmod +x linters/git-hooks/bin/resolve_venv_python.sh linters/git-hooks/bin/python linters/git-hooks/bin/pre-commit \
		linters/git-hooks/commitlint.sh

app-pre-commit-run:
	$(PYTHON) -m pre_commit run --all-files

app-clean:
	rm -rf build dist *.egg-info .pytest_cache .coverage htmlcov .mypy_cache .ruff_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

quality ci: app-quality
lint: app-lint
security: app-security
test tests: app-test
validate: app-validate
build: app-build
format: app-format
dead-code: app-dead-code
audit: app-audit
setup: app-setup
install: app-install
pre-commit-install: app-pre-commit
pre-commit-run: app-pre-commit-run
clean: app-clean

git-init:
	@git rev-parse --is-inside-work-tree >/dev/null 2>&1 || git init -b main
