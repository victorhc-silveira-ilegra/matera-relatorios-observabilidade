# Estrutura do Repositorio

Mapeamento canonico dos diretorios e arquivos do projeto de Relatorios de Observabilidade.

```text
.
├── .gitattributes                            # Normalizacao LF, CRLF e definicao de binarios
├── .gitignore                                # Exclusoes de caches, venv, secrets e logs
├── .gitleaks.toml                            # Configuracao de deteccao de segredos e allowlist
├── .pre-commit-config.yaml                   # Orquestracao de hooks locais pre-commit e commit-msg
├── .python-version                           # Fixacao da versao do interpretador Python (3.13)
├── AGENTS.md                                 # Ponto de entrada mestre e governanca para agentes e IAs
├── prompt-model.md                           # Contrato de engenharia reutilizavel e prompt de bootstrap
├── pyproject.toml                            # Configuracao unificada de ferramentas (ruff, mypy, bandit, vulture, pytest, build)
├── requirements.txt                          # Dependencias de producao (httpx, playwright, python-dotenv)
├── requirements-dev.txt                      # Dependencias de desenvolvimento, testes e QA
├── Makefile                                  # Alvos operacionais de build, testes, gates, tools e relatorios
├── README.md                                 # Portal executivo mestre com badges, diagramas e instrucoes
├── .env.example                              # Modelo de variaveis de ambiente obrigatorias
│
├── .github/                                  # Workflows e Composite Actions de CI/CD
│   ├── workflows.md                          # Documentacao tecnica de workflows e automacoes
│   ├── workflows/
│   │   └── ci.yml                            # Pipeline principal de CI/CD (Push, PR, Dispatch)
│   └── actions/
│       ├── shared/
│       │   └── pipeline-summary/action.yml   # Consolidacao visual no GitHub Step Summary
│       └── ci/
│           ├── setup-python/action.yml       # Setup Python 3.13 e pip cache
│           ├── validate-commitlint/action.yml# Validacao de Conventional Commits
│           ├── validate-python/action.yml    # Execucao dos 5 estagios Python
│           ├── validate-scripts/action.yml   # Validacao sintatica de shell scripts e Makefile
│           ├── validate-github/action.yml    # Validacao de actions e gitleaks
│           ├── sync-tags/action.yml          # Sincronizacao de tags Git orfas
│           └── release/action.yml            # Semantic Release e geracao de changelog
│
├── .agents/                                  # Harness universal para LLMs e agentes autonomos
│   ├── README.md                             # Manifesto e diretrizes de consumo do harness
│   ├── rules/                                # Regras arquiteturais e politicas invariantes
│   │   ├── architecture-hexagonal-ddd.md     # Isolamento de camadas e regras de dependencia
│   │   ├── flagship-dtw-policy.md            # Politica operacional do cliente Flagship (DTW)
│   │   ├── revolut-mip-policy.md             # Politica operacional do cliente Revolut (MIP)
│   │   ├── observability-semantic-logging.md # Padroes de logging estruturado e sinks
│   │   └── code-quality-testing.md           # Padroes TDD, cobertura 100% e CI/CD
│   └── skills/                               # Habilidades operacionais especializadas
│       ├── generate-flagship-report/SKILL.md # Procedimento de geracao do relatorio Flagship
│       ├── generate-revolut-report/SKILL.md  # Procedimento de geracao do relatorio Revolut
│       ├── quality-gate/SKILL.md             # Execucao e diagnostico da Matriz de 5 Estagios
│       └── observability-ops/SKILL.md        # Operacoes de rede, proxy HTTP e scrapers
│
├── app/                                      # Codigo-fonte da aplicacao (Hexagonal / DDD)
│   ├── README.md                             # Especificacao tecnica dos modulos e regra de dependencia
│   ├── domain/                               # Nucleo puro de dominio
│   │   ├── time_window.py                    # Value Object TimeWindow e janelas oficiais BRT
│   │   ├── flagship/                         # Dominio Flagship (models, status, formatter)
│   │   └── revolut/                          # Dominio Revolut (models, formatter)
│   ├── application/                          # Casos de uso e portas abstratas
│   │   ├── ports.py                          # Protocolos typing.Protocol
│   │   └── use_cases.py                      # GenerateFlagshipReport e GenerateRevolutReport
│   ├── infrastructure/                       # Adaptadores de I/O, configuracoes e logging
│   │   ├── settings.py                       # Validacao de variaveis de ambiente
│   │   ├── logging/                          # Pacote modular de logging semantico
│   │   │   ├── __init__.py                   # Fachada reexportando log_event e configure_logging
│   │   │   ├── events.py                     # Catalogo canonico de eventos
│   │   │   ├── redact.py                     # Higienizacao e redacao de URLs e segredos
│   │   │   ├── emit.py                       # Emissao estruturada de eventos semanticos
│   │   │   └── formatters.py                 # Formatadores JsonSemanticFormatter e TextSemanticFormatter
│   │   └── adapters/                         # OpenSearch, Grafana, CloudWatch e Readers
│   └── presentation/                         # Ponto de entrada e composition root
│       └── cli.py                            # CLI unificada (--client flagship|revolut)
│
├── config/                                   # Configuracoes de ambiente e ferramentas
│   └── python.json                           # Mapeamento do interpretador e venv do projeto
│
├── docs/                                     # Documentacao viva do projeto
│   ├── README.md                             # Indice mestre e catalogo da documentacao tecnica
│   ├── arquitetura.md                        # Manual detalhado de arquitetura e topologia
│   ├── structure.md                          # Arvore completa do repositorio (este arquivo)
│   ├── engineering-python.md                 # Convencoes de desenvolvimento Python e estilo
│   ├── engineering-logging.md                # Padroes de observabilidade e catalogo de eventos
│   ├── devops.md                             # Matriz de qualidade, automacao e esteira CI
│   └── CHANGELOG.md                          # Historico padronizado de releases semanticas
│
├── linters/                                  # Configuracao de commitlint, releases e wrappers de git-hooks
│   ├── README.md                             # Manual tecnico de linters, commitlint e release
│   ├── commitlint.config.mjs                 # Regras Conventional Commits (type-enum, subject-case)
│   ├── releaserc.json                        # Pipeline de Semantic Release automatizado
│   └── git-hooks/                            # Scripts de integracao e wrappers do pre-commit
│       ├── bin/                              # Resolucao de interpretador Python do .venv
│       ├── commitlint.sh                     # Runner de commitlint via npx
│       ├── commit-msg                        # Hook do estagio commit-msg
│       ├── pre-commit                        # Hook do estagio pre-commit
│       └── install.sh                        # Instalador automatizado dos hooks
│
├── scripts/                                  # Scripts operacionais e esteira de automacao
│   ├── README.md                             # Guia do orquestrador de qualidade e scripts
│   └── quality_gate.py                       # Orquestrador dos 5 estagios (--stage lint|security|test|...)
│
└── tests/                                    # Suite de testes com 100% de branch coverage
    ├── conftest.py                           # Fixtures compartilhadas e isolamento de ambiente
    ├── README.md                             # Manifesto e diretrizes da suite de testes
    ├── unit/                                 # Testes unitarios isolados por camada
    │   ├── README.md                         # Diretrizes de testes unitarios
    │   ├── domain/                           # Testes de regras de negocio e formatacao de dominio
    │   │   ├── test_flagship_formatter.py    # Formatacao do relatorio Flagship
    │   │   ├── test_flagship_status.py       # Motor de status Flagship
    │   │   ├── test_revolut_domain.py        # Dominio e formatacao Revolut
    │   │   └── test_time_window.py           # Janelas oficiais BRT e TimeWindow
    │   ├── application/                      # Testes dos casos de uso com fakes
    │   │   └── test_use_cases.py             # GenerateFlagshipReport e GenerateRevolutReport
    │   └── presentation/                     # Testes de pontos de entrada
    │       └── test_cli.py                   # Testes da CLI e argv
    └── integration/                          # Testes de integracao e infraestrutura
        ├── README.md                         # Diretrizes de testes de integracao
        └── infrastructure/                   # Testes de adaptadores reais e emulados
            ├── test_adapters.py              # Adaptadores com mock HTTP e Playwright
            ├── test_collectors.py            # Parsing de metricas, frames e URLs
            ├── test_logging.py               # Redacao, formatadores e logging semantico
            └── test_settings.py              # Configuracoes e adaptador de saida de arquivo
```
