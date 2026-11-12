# Regra de Observabilidade: Logging Semantico e Separacao de Sinks

Esta regra define os padroes de emissao de logs estruturados, severidades e separacao categorica entre logs de processo e produtos operacionais entregues.

---

## 1. Separacao Estrita: Produto (Stdout) vs Log

- **Produto Operacional (Relatorio)**: O relatorio formatado emitido no terminal (`stdout`) e o artefato de negocio final consumido pelos operadores.
- **Log (Diagnostico de Execucao)**: Eventos emitidos via `log_event(logger, level, event, **fields)` que informam o inicio, conclusao ou falha de processos.
- **Invariante**: Logs nunca duplicam a carga util dos relatorios. O relatorio pertence exclusivamente ao fluxo de saida de apresentacao (`ReportOutputPort`).

---

## 2. Niveis de Severidade Semantica

| Nivel | Uso Exclusivo | Comportamento Operacional |
| :--- | :--- | :--- |
| **`INFO`** | Apenas no caminho feliz estrutural: inicio de geracao (`report.generation.started`) e conclusao bem-sucedida (`report.generation.completed`). | Evitar logs excessivos ou verbosos em execucoes bem-sucedidas. |
| **`WARNING`** | Falhas parciais onde a execucao continua controlada: timeout no CloudWatch mitigado por `--skip-rds`, falha de metricas secundarias. | Registra diagnostico sem abortar o processo. |
| **`ERROR`** | Falhas fatais que impedem a geracao do relatorio: falha de conexao com OpenSearch/Grafana ou erro de argumentos. | O processo encerra imediatamente com exit code nao-zero. |
| **`DEBUG`** | Detalhes de rastreamento para depuracao local. | Desativado em producao por padrao. |

---

## 3. Catalogo de Eventos Semanticos

| Evento | Nivel | Origem | Descricao |
| :--- | :--- | :--- | :--- |
| `report.generation.started` | `INFO` | CLI | Inicio do ciclo de geracao de relatorio |
| `report.generation.completed` | `INFO` | CLI | Conclusao com sucesso do relatorio |
| `report.generation.failed` | `ERROR` | CLI | Falha critica na geracao |
| `opensearch.fetch.failed` | `WARNING` | OpenSearch Adapter | Falha ao consultar endpoint OpenSearch |
| `grafana.query.failed` | `WARNING` | Grafana Adapter | Falha em expressao PromQL ou MySQL no Grafana |
| `rds.scrape.failed` | `WARNING` | CloudWatch Adapter | Falha ou timeout no Playwright ao coletar RDS |

---

## 4. Seguranca e Redacao de Segredos

- URLs corporativas com credenciais de basic auth sao automaticamente mascaradas.
- Tokens e senhas nunca sao impressos em streams de saida ou arquivos de log.
- O helper `redact_secrets` sanitiza qualquer campo sensivel antes da serializacao JSON dos eventos.
