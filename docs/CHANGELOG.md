# Changelog

## [1.1.2](https://github.com/victorhc-silveira-ilegra/matera-relatorios-observabilidade/compare/v1.1.1...v1.1.2) (2026-11-13)

### Correções de Bugs

* **flagship:** avalia incidentes em tempo real quando emissao ocorre pos janela ([2af9762](https://github.com/victorhc-silveira-ilegra/matera-relatorios-observabilidade/commit/2af976237d823c1965295fb1244aec83e573571b))

## [1.1.1](https://github.com/victorhc-silveira-ilegra/matera-relatorios-observabilidade/compare/v1.1.0...v1.1.1) (2026-11-13)

### Correções de Bugs

* **revolut:** ajusta status para atencao quando houver erros de logs sem degradacao critica de latencia ([a9a52b9](https://github.com/victorhc-silveira-ilegra/matera-relatorios-observabilidade/commit/a9a52b9d98cf694afa2d52aabe6ff0fc36c31538))
* **revolut:** implementa normalizacao progressiva de logs para m5 e atual ([d63272f](https://github.com/victorhc-silveira-ilegra/matera-relatorios-observabilidade/commit/d63272f11d143b8eb9083634f14d5f6a260c6211))

### Documentação

* **docs:** atualiza links dos badges de ci e release para o repositorio correto ([3eedc07](https://github.com/victorhc-silveira-ilegra/matera-relatorios-observabilidade/commit/3eedc07371d44fc65a7f72ffb1cc4149aa0ca5eb))

## [1.1.0](https://github.com/victorhc-silveira-ilegra/matera-relatorios-observabilidade/compare/v1.0.0...v1.1.0) (2026-11-12)

### Novas Funcionalidades

* **makefile:** padroniza alvos de relatorios pelo horario de termino com dois pontos ([1f1f2e6](https://github.com/victorhc-silveira-ilegra/matera-relatorios-observabilidade/commit/1f1f2e670570101a85708a0b6d50d654749a3e92))

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
