# Engenharia de Observabilidade e Logging Semantico

Este documento padroniza a emissao de telemetria, eventos estruturados e a protecao de informacoes sensiveis no projeto.

---

## 1. Separacao entre Produto e Telemetria

- **Produto Final**: O texto do relatorio gerado (destinado a operacao e aos canais de comunicacao) e entregue via `ReportOutputPort` (padrao `stdout`). O produto final contem emojis, tabelas e marcadores de status de negocio.
- **Telemetria de Processo**: Mensagens de ciclo de vida e erros emitidas via logger estruturado (`log_event`). Logs sao emitidos em formato JSON sem emojis e sem duplicar o conteudo do relatorio.

---

## 2. API Estruturada `log_event` e Pacote Modular

Toda emissao de log no projeto reside sob `app/infrastructure/logging/` e e mediada pela funcao `log_event`:

```python
from app.infrastructure.logging import (
    REPORT_GENERATION_STARTED,
    configure_logging,
    log_event,
)

logger = configure_logging()
log_event(
    logger,
    logging.INFO,
    REPORT_GENERATION_STARTED,
    client="flagship",
    window="10:30-13:30",
)
```

### Modulos do Pacote

- `events.py`: Constantes imutaveis representando os eventos de ciclo.
- `redact.py`: Higienizacao de campos (`sanitize_value`) e ofuscacao de URLs (`mask_url`).
- `emit.py`: Emissao serializada do payload em JSON seguro.
- `formatters.py`: Formatadores `JsonSemanticFormatter` e `TextSemanticFormatter`.
- `__init__.py`: Fachada de conveniencia e reexportacao.

---

## 3. Catalogo de Eventos

| Constante | Valor | Nivel | Descricao |
| :--- | :--- | :--- | :--- |
| `REPORT_GENERATION_STARTED` | `report.generation.started` | `INFO` | Inicio da geracao de relatorio de um cliente |
| `REPORT_GENERATION_COMPLETED` | `report.generation.completed` | `INFO` | Conclusao bem-sucedida da geracao do relatorio |
| `REPORT_GENERATION_FAILED` | `report.generation.failed` | `ERROR` | Falha fatal durante a geracao |
| `METRICS_FETCH_STARTED` | `metrics.fetch.started` | `INFO` | Inicio da coleta de metricas |
| `METRICS_FETCH_FAILED` | `metrics.fetch.failed` | `WARNING` | Falha na coleta de metricas tolerada |
| `CLOUDWATCH_SCRAPE_STARTED` | `cloudwatch.scrape.started` | `INFO` | Disparo do scraper headless do CloudWatch |
| `CLOUDWATCH_SCRAPE_FAILED` | `cloudwatch.scrape.failed` | `WARNING` | Falha ou timeout no scraping do CloudWatch |
| `CLOUDWATCH_SCRAPE_SKIPPED` | `cloudwatch.scrape.skipped` | `INFO` | Scraping pulado via parametro `--skip-rds` |

---

## 4. Protecao de Dados Sensiveis (Redacao)

- Segredos, tokens e senhas sao automaticamente sanitizados via `sanitize_value`.
- As chaves `password`, `pass`, `token`, `secret`, `auth`, `credential` tem seus valores substituidos por `***REDACTED***`.
- URLs sao ofuscadas via `mask_url`, preservando apenas `scheme://netloc/...`.
