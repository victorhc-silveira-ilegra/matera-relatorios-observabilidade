# Harness de Agentes Inteligentes

Harness universal de engenharia para orientar modelos de linguagem (LLMs), agentes autonomos e assistentes inteligentes no projeto de Relatorios de Observabilidade.

---

## 1. Principios de Design do Harness

1. **Agnostico a Plataforma**: Formato 100% Markdown padronizado com frontmatter YAML padrao, compativel com Antigravity, Cursor, Claude Code, Copilot e execucoes CLI.
2. **Arquitetura Senior Inegociavel**: Respeito estrito aos padroes Domain-Driven Design (DDD), Arquitetura Hexagonal (Ports & Adapters) e Test-Driven Development (TDD).
3. **Determinismo Operacional**: Todas as decisoes de metricas, calculo de janelas horarias, limiares de estabilidade e formatacao possuem regras matematicas e contratuais bem definidas.
4. **Zero Codigo Morto ou Ruido**: Codigo autodescritivo sem comentarios, tipagem estrita com Python 3.11+ (`mypy --strict`), limites de 300 linhas por arquivo e cobertura total de testes (100% de branch coverage).

---

## 2. Estrutura do Diretorio

```text
.agents/
├── README.md                                 # Manifesto e governanca do harness
├── rules/                                    # Regras arquiteturais e invariantes
│   ├── architecture-hexagonal-ddd.md         # Isolamento de camadas e regras de dependencia
│   ├── flagship-dtw-policy.md                # Regras de negocio e limiares do cliente Flagship
│   ├── revolut-mip-policy.md                 # Regras de negocio e limiares do cliente Revolut
│   ├── observability-semantic-logging.md     # Logging estruturado, eventos e separacao de sinks
│   └── code-quality-testing.md               # Padroes TDD, cobertura 100% e quality gates
└── skills/                                   # Habilidades operacionais especializadas
    ├── generate-flagship-report/SKILL.md     # Geracao e inspecao do relatorio Flagship (DTW)
    ├── generate-revolut-report/SKILL.md      # Geracao e inspecao do relatorio Revolut (MIP)
    ├── quality-gate/SKILL.md                 # Execucao e resolucao da Matriz de 5 Estagios
    └── observability-ops/SKILL.md            # Diagnostico de rede, proxy HTTP e scrapers
```

---

## 3. Como os Agentes Devem Consumir este Harness

- **Ponto de Entrada Mestre**: O arquivo [`AGENTS.md`](../AGENTS.md) na raiz do repositorio e o contrato principal carregado automaticamente no inicio de qualquer sessao.
- **Regras Gerais (`rules/`)**: Devem ser aplicadas de forma continua durante qualquer ciclo de leitura, refatoracao, implementacao ou depuracao.
- **Habilidades (`skills/`)**: Devem ser consultadas sob demanda quando o agente estiver atuando especificamente na area descrita pelo `description` do frontmatter YAML da skill correspondente.
