# Regra de Negocio: Politica Operacional Flagship (DTW)

Esta regra governa a coleta, processamento de metricas e avaliacao de status para o cliente Flagship (DTW).

---

## 1. Janelas de Tempo Oficiais

As janelas diarias oficiais sao calculadas no fuso `America/Sao_Paulo` (`BRT`):
- `08:30–10:30` (2 horas de duracao)
- `10:30–13:30` (3 horas de duracao)
- `13:30–16:30` (3 horas de duracao)

Janelas cumulativas de erros (`routing_errors`) e chamadas de API (`api_hits`) exibem todas as janelas do dia ate a janela atual selecionada.

---

## 2. Metricas e Painis de Referencia

### Homologacao (HML)
- **Logs (`OpenSearch HML`)**: Distribuicao percentual de `INFO`, `WARN`, `ERROR` e `DEBUG`. Em HML, `ERROR %` elevado e esperado devido a testes de carga e QA, nao devendo por si so degradar o status geral do ambiente.
- **Incidentes (`Grafana HML`)**: Painel de referencia com janela fixa de 5 horas (`[5h]`):
  `sum by (topic) (increase(kafka_server_BrokerTopicMetrics_Count{name="MessagesInPerSec", topic="hml.dtw.event.incident"}[5h]))`
- **Lag Kafka (`Grafana HML`)**: Soma de lag de consumidores excluindo grupos canary/backup. Valores `<= 10.0` sao ignorados como ruido efemero.
- **Restarts de Pods (`Grafana HML`)**: Janela fixa de 6 horas (`[6h]`):
  `increase(kube_pod_container_status_restarts_total{namespace="dtw-hml"}[6h])`

### Producao (PRD)
- **Logs (`OpenSearch PRD`)**: Distribuicao percentual e contagem absoluta de `ERROR`.
- **Logs de Erro por Servico (`OpenSearch PRD`)**:
  - `cc-integration-event-routing-entry-producer`: Contagem de logs `ERROR` por janela horaria do dia.
  - `dtw-transaction-api` (API Hits): Contagem de logs com mensagem `Check the difference between the delta and physical balance table on account`.
- **Incidentes (`Grafana PRD`, Dashboard `OCgyltPVk`, Painel 6)**: Mede a taxa recente nos **ultimos 30 minutos** (`[30m]`):
  `sum by (topic) (increase(kafka_server_BrokerTopicMetrics_Count{name="MessagesInPerSec", topic="prod.dtw.event.incident"}[30m]))`
- **Restarts de Pods (`Grafana PRD`)**: Janela pontual de 1 minuto no fechamento da janela (`[1m]`).
- **Integracao SAGA (`Grafana PRD`, MySQL `4hs8MXdIz`)**:
  - `Total de integracoes`: `select count(*) from STDIN_CONTROLE_SAGA_INTEGRACAO where integrated = 'N'`.
  - `Integracoes acima de 5 min`: `WHERE integrated = 'N' AND DATE_ADD(created, INTERVAL 3 HOUR) <= NOW() - INTERVAL 5 MINUTE`.
- **Monitoramento de Dados (`Grafana PRD`, MySQL `T2rqmE8Sk`)**:
  - `DTW_TR_POLLING_ENTRY`: `SELECT COUNT(*) FROM DTW_TR_POLLING_ENTRY WHERE PROCESSED IN (0,1)` (PROCESSED) e `WHERE PROCESSED = 0` (Total pendente).
- **RDS CPUUtilization (`AWS CloudWatch`)**: Scraper headless no dashboard publico `Flagship-BlackFriday`. Consumo atual e deteccao de picos `>= 90%`.

---

## 3. Matriz de Avaliacao de Status

### Producao (PRD)
- **🔴 Instavel**:
  - `ERROR >= 50%` nos logs de producao.
  - `lag >= 1000` no Kafka.
  - Crash loop em pods (`restarts >= 3.0`).
  - SAGA com integracoes estagnadas (`acima de 5 min > 0`).
  - Tabela Polling com acumulo critico (`total >= 10.000`).
  - RDS CPU com pico sustentado (`>= 3` pontos `>= 90%` na janela ou consumo atual `>= 90%`).
- **🟡 Atencao**:
  - `5% <= ERROR < 50%` ou `WARN >= 20%`.
  - Erros recorrentes em producer (`routing_errors >= 10`) ou API hits (`api_hits >= 10`).
  - Lag moderado (`10 < lag < 1000`).
  - Restarts pontuais (`0 < restarts < 3.0`).
  - SAGA acumulado em processamento (`total >= 10` e `acima_5m == 0`).
  - Tabela Polling acumulada (`100 <= total < 10.000`).
  - RDS CPU com pico pontual (`1 <= pontos < 3`).
  - Chamado ativo informado em `--chamados-prd`.
- **🟢 Estavel**: Quando nenhum dos criterios acima e atingido (ex.: `SAGA total < 10`, `Polling < 100`, sem picos de CPU, sem lag).

### Homologacao (HML)
- **🔴 Instavel**: Lag massivo (`>= 1000`) ou crash loop em pods (`restarts >= 3.0`).
- **🟡 Atencao**: Lag moderado (`10 < lag < 1000`), restarts pontuais (`restarts > 0`) ou chamados ativos em HML.
- **🟢 Estavel**: Operacao normal.
