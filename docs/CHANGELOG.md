# Changelog

## 1.0.0 (2026-11-12)

### Novas Funcionalidades

* **app:** inicializacao da arquitetura hexagonal, governanca, ci-cd e testes 100% ([cfb3704](https://github.com/victorhc-silveira-ilegra/matera-relatorios-observabilidade/commit/cfb3704c7284b555d5e9a84bfe3fe3110c07a022))

Todas as mudancas notaveis neste projeto serao documentadas neste arquivo.
O formato e baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [0.2.0] - 2026-11-12

### Adicionado
- Arquitetura Hexagonal pura e Domain-Driven Design (DDD) com quatro camadas (`domain`, `application`, `infrastructure`, `presentation`).
- Suporte unificado aos clientes corporativos Flagship (DTW) e Revolut (MIP).
- Consulta headless via Playwright para metricas RDS CloudWatch da Flagship.
- Conexao e consultas seguras ao Grafana da Revolut atraves de proxy HTTP dedicado.
- Gatilho progressivo de validacao dos 12 servicos SPI (`[15m]` -> `[5m]` / `[1m]`).
- Motor deterministico de avaliacao de saude (`evaluate_prd_status` e `evaluate_hml_status`).
- Matriz de Qualidade com 5 estagios automatizados (`scripts/quality_gate.py`) e 100% de branch coverage.
- Harness universal de Engenharia de IA (`.agents/`).
- Infraestrutura de Git Hooks locais com Pre-commit, Commitlint e Semantic Release.
