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
- **Incidentes (`Grafana HML`, Dashboard `OCgyltPVk`, Painel 6)**: Mede a taxa nos **ultimos 30 minutos** (`[30m]`):
  `sum by (topic) (increase(kafka_server_BrokerTopicMetrics_Count{name="MessagesInPerSec", topic="hml.dtw.event.incident"}[30m]))`
  - `< 50`: `🟢`
  - `>= 50`: `🟡`
- **Lag Kafka (`Grafana HML`)**: Soma de lag de consumidores excluindo grupos canary/backup. Valores `<= 10.0` sao omitidos da impressao na tela. Valores entre `10` e `500` sao impressos com badge verde `🟢`. Valores `>= 500` exibem `🟡` e `>= 1000` exibem `🔴`.
- **Restarts de Pods (`Grafana HML`)**: Coleta no intervalo dinâmico da janela (`duration_promql`, ex.: `[120m]` para 08:30–10:30 e `[180m]` para 10:30–13:30 e 13:30–16:30):
  `increase(kube_pod_container_status_restarts_total{namespace="dtw-hml"}[<duration_promql>])`

### Producao (PRD)
- **Logs (`OpenSearch PRD`)**: Distribuicao percentual e contagem absoluta de `ERROR`.
- **Logs de Erro por Servico (`OpenSearch PRD`)**:
  - `cc-integration-event-routing-entry-producer`: Contagem de logs `ERROR` por janela horaria do dia.
  - `dtw-transaction-api` (API Hits): Contagem de logs com mensagem `Check the difference between the delta and physical balance table on account`.
- **Incidentes (`Grafana PRD`, Dashboard `OCgyltPVk`, Painel 6)**: Mede a taxa nos **ultimos 30 minutos** (`[30m]`) avaliada estritamente no fechamento da janela (`end_brt`):
  `sum by (topic) (increase(kafka_server_BrokerTopicMetrics_Count{name="MessagesInPerSec", topic="prod.dtw.event.incident"}[30m]))`
  - `< 50`: `🟢`
  - `>= 50`: `🟡`
- **Lag Kafka (`Grafana PRD`)**: Valores `<= 10.0` sao omitidos da impressao na tela. Valores entre `10` e `500` exibem `🟢`. Valores entre `500` e `1000` exibem `🟡`, e `>= 1000` exibem `🔴`.
- **Restarts de Pods (`Grafana PRD`)**: Coleta no intervalo dinâmico da janela (`duration_promql`, ex.: `[120m]` para 08:30–10:30 e `[180m]` para 10:30–13:30 e 13:30–16:30):
  `increase(kube_pod_container_status_restarts_total{namespace="dtw-prod"}[<duration_promql>])`.
- **Integracao SAGA (`Grafana PRD`, MySQL `4hs8MXdIz`)**:
  - `Total de integracoes`: `select count(*) from STDIN_CONTROLE_SAGA_INTEGRACAO where integrated = 'N'`.
  - `Integracoes acima de 5 min`: `WHERE integrated = 'N' AND DATE_ADD(created, INTERVAL 3 HOUR) <= NOW() - INTERVAL 5 MINUTE`.
- **Monitoramento de Dados (`Grafana PRD`, MySQL `T2rqmE8Sk`, Painel 4)**:
  - `DTW_TR_POLLING_ENTRY`: `SELECT COUNT(*) FROM DTW_TR_POLLING_ENTRY WHERE PROCESSED IN (0,1)` (PROCESSED com limiares `< 8.5M 🟢`, `8.5M–10.5M 🟡`, `>= 10.5M 🔴`) e `WHERE PROCESSED = 0` (Total pendente).
- **RDS CPUUtilization (`AWS CloudWatch`)**: Scraper headless no dashboard publico `Flagship-BlackFriday`. Consumo atual e deteccao de picos `>= 90%`.

---

## 3. Matriz de Avaliacao de Status

### Producao (PRD)
- **🔴 Instavel**:
  - `ERROR >= 20%` nos logs de producao.
  - `lag >= 1000` no Kafka.
  - Crash loop em pods (`restarts >= 3.0`).
  - SAGA com integracoes estagnadas (`acima de 5 min > 0`) ou fila acumulada critica (`total >= 100`).
  - Tabela Polling com volume critico (`PROCESSED >= 10.500.000` ou `total pendente >= 10.000`).
  - RDS CPU com pico sustentado (`>= 3` pontos `>= 90%` na janela ou consumo atual `>= 90%`).
- **🟡 Atencao**:
  - `5% <= ERROR < 20%` ou `WARN >= 20%`.
  - Erros recorrentes em producer (`routing_errors >= 10`) ou API hits (`api_hits >= 10`).
  - Lag moderado (`500 <= lag < 1000`).
  - Restarts pontuais (`0 < restarts < 3.0`).
  - SAGA acumulado em processamento (`10 <= total < 100` e `acima_5m == 0`).
  - Tabela Polling com volume elevado (`8.500.000 <= PROCESSED < 10.500.000` ou `100 <= total pendente < 10.000`).
  - RDS CPU com pico pontual (`1 <= pontos < 3`).
  - Chamado ativo informado em `--chamados-prd`.
- **🟢 Estavel**: Quando nenhum dos criterios acima e atingido (ex.: `lag < 500`, `SAGA total < 10`, `Polling < 100`, sem picos de CPU).

### Homologacao (HML)
- **🔴 Instavel**: Exclusivamente por Lag massivo no Kafka (`lag >= 1000`). Erros de log e restarts de pods nao caracterizam instabilidade em homologacao.
- **🟡 Atencao**: Lag moderado (`500 <= lag < 1000`), restarts de pods (`restarts > 0`) ou chamados ativos em HML.
- **🟢 Estavel**: Operacao normal.
