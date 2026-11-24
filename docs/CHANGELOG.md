# Changelog

## [1.3.1](https://github.com/victorhc-silveira-ilegra/matera-relatorios-observabilidade/compare/v1.3.0...v1.3.1) (2026-11-24)

### Correções de Bugs

* **infra:** usa range com intervalMs em queries timeseries do grafana ([58f1b32](https://github.com/victorhc-silveira-ilegra/matera-relatorios-observabilidade/commit/58f1b32351001a27a43da356300df3a9a29d3377))

## [1.3.0](https://github.com/victorhc-silveira-ilegra/matera-relatorios-observabilidade/compare/v1.2.4...v1.3.0) (2026-11-24)

### Novas Funcionalidades

* **reports:** adiciona fallback rds, particao polling, restarts, 5xx e melhora ux ([8df573d](https://github.com/victorhc-silveira-ilegra/matera-relatorios-observabilidade/commit/8df573dd2630704c0ab9280a479e234f7b1e350f))

### Refatorações

* **domain:** centraliza thresholds da flagship, avalia incidentes e deriva slots da revolut ([5b8056c](https://github.com/victorhc-silveira-ilegra/matera-relatorios-observabilidade/commit/5b8056ca1751bc78c209b6504ccd185afe4c7c02))

## [1.2.4](https://github.com/victorhc-silveira-ilegra/matera-relatorios-observabilidade/compare/v1.2.3...v1.2.4) (2026-11-23)

### Correções de Bugs

* **revolut:** marca ambiente em atencao e exibe metrica nos eventos criticos ([4d3b6c2](https://github.com/victorhc-silveira-ilegra/matera-relatorios-observabilidade/commit/4d3b6c2582f7b0f45f5655d8e3b8bd4f69d82073))

## [1.2.3](https://github.com/victorhc-silveira-ilegra/matera-relatorios-observabilidade/compare/v1.2.2...v1.2.3) (2026-11-23)

### Correções de Bugs

* **reports:** alinha limiares, cores e queries dos relatorios aos paineis reais do grafana ([8c5ea80](https://github.com/victorhc-silveira-ilegra/matera-relatorios-observabilidade/commit/8c5ea8067cfb7e5f472291d1e3f605c2d6a075d3))
* **revolut:** exibe status historico real e detalhes dos eventos criticos por horario ([757494f](https://github.com/victorhc-silveira-ilegra/matera-relatorios-observabilidade/commit/757494fda0b05ad5eaef6b5700db2e53d9f6e484))

### Integração Contínua (CI/CD)

* **linters:** dispara validacao commitlint na main ([3133aba](https://github.com/victorhc-silveira-ilegra/matera-relatorios-observabilidade/commit/3133abacb110139fbaeec74dc7de911c0c308da4))

## [1.2.2](https://github.com/victorhc-silveira-ilegra/matera-relatorios-observabilidade/compare/v1.2.1...v1.2.2) (2026-11-18)

### Correções de Bugs

* **revolut:** reverte formatacao html e clipboard mantendo markdown padrao ([738f1ae](https://github.com/victorhc-silveira-ilegra/matera-relatorios-observabilidade/commit/738f1aef009b31177125ddd7f80d2ce65e62537f))

## [1.2.1](https://github.com/victorhc-silveira-ilegra/matera-relatorios-observabilidade/compare/v1.2.0...v1.2.1) (2026-11-18)

### Correções de Bugs

* **flagship:** restaura formatacao de asterisco duplo para preservar emojis no Google Chat ([bf8c2d3](https://github.com/victorhc-silveira-ilegra/matera-relatorios-observabilidade/commit/bf8c2d3484a2c50084715a6e172d89c2a3bee189))

## [1.2.0](https://github.com/victorhc-silveira-ilegra/matera-relatorios-observabilidade/compare/v1.1.7...v1.2.0) (2026-11-18)

### Novas Funcionalidades

* **reports:** ajusta negrito para Google Chat e adiciona Rich Text HTML para Google Docs ([9e7c305](https://github.com/victorhc-silveira-ilegra/matera-relatorios-observabilidade/commit/9e7c3059f4cf8905cd32bf2c13f01571c9382c37))

## [1.1.7](https://github.com/victorhc-silveira-ilegra/matera-relatorios-observabilidade/compare/v1.1.6...v1.1.7) (2026-11-17)

### Correções de Bugs

* **flagship:** calibra limiar de alerta de lag para 500 e ajusta badges ([293bd85](https://github.com/victorhc-silveira-ilegra/matera-relatorios-observabilidade/commit/293bd85de24021516a5e76cd0740e8953cf552e0))

## [1.1.6](https://github.com/victorhc-silveira-ilegra/matera-relatorios-observabilidade/compare/v1.1.5...v1.1.6) (2026-11-16)

### Correções de Bugs

* **reports:** padroniza subtitulos e titulos em negrito para flagship e revolut ([661f14c](https://github.com/victorhc-silveira-ilegra/matera-relatorios-observabilidade/commit/661f14c192a8d32b60bbad5b7d687768009c5371))

## [1.1.5](https://github.com/victorhc-silveira-ilegra/matera-relatorios-observabilidade/compare/v1.1.4...v1.1.5) (2026-11-16)

### Correções de Bugs

* **flagship:** consolida limiares do grafana, amostragem por janela e formatacao para chat ([c270ffe](https://github.com/victorhc-silveira-ilegra/matera-relatorios-observabilidade/commit/c270ffed2ee034fde4ab72d3778a80f4aac450c9))

## [1.1.4](https://github.com/victorhc-silveira-ilegra/matera-relatorios-observabilidade/compare/v1.1.3...v1.1.4) (2026-11-16)

### Correções de Bugs

* **settings:** forca override de variaveis de ambiente pelo dotenv ([9a899d1](https://github.com/victorhc-silveira-ilegra/matera-relatorios-observabilidade/commit/9a899d155a7dd246c12e987465ad965483ff2a33))

### Integração Contínua (CI/CD)

* **linters:** inclui escopo settings na matriz de validacao do commitlint ([c62f1f3](https://github.com/victorhc-silveira-ilegra/matera-relatorios-observabilidade/commit/c62f1f33cc1ab300dbb34a14aa8b2040f501ecea))

## [1.1.3](https://github.com/victorhc-silveira-ilegra/matera-relatorios-observabilidade/compare/v1.1.2...v1.1.3) (2026-11-13)

### Correções de Bugs

* **app:** remove fallbacks ao vivo e fixa janelas estritas de tempo ([34a1d8b](https://github.com/victorhc-silveira-ilegra/matera-relatorios-observabilidade/commit/34a1d8b17f56c78f1a8a3b1797fde00100ce1325))

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
