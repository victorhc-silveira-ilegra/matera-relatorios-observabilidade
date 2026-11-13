# Regra de Negocio: Politica Operacional Revolut (MIP)

Esta regra governa a coleta, comunicacao via proxy e validacao de metricas do cliente Revolut (MIP - Producao AWS).

---

## 1. Conectividade e Proxy HTTP

O cluster de monitoramento da Revolut e acessivel exclusivamente via PrivateLink atraves do proxy HTTP corporativo:
- **URL Base:** `https://grafana-pvtlink.mip.prd.revolut.maas.link`
- **Proxy HTTP:** `http://10.150.8.18:3128` (configurado via `REVOLUT_HTTP_PROXY`)
- **Autenticacao:** Basic Auth via variaveis de ambiente `GRAFANA_REVOLUT_USER` e `GRAFANA_REVOLUT_PASS`.
- **Invariante:** Nenhuma requisicao direta (sem passar pela proxy) tem sucesso para este host. O cliente HTTP deve configurar explicitamente `proxy=settings.revolut_http_proxy`.

---

## 2. Limiares Operacionais de Latencia PIX

Os tempos de processamento das transacoes PIX sao avaliados por percentis (P50 e P95) contra os acordos operacionais:

| Fluxo | Percentil | Teto Operacional | Status Normal | Status Degradado |
| :--- | :--- | :--- | :---: | :---: |
| **Pagador** | P50 | $\le 0.90\text{s}$ ($900\text{ms}$) | ✅ | 🔴 |
| **Pagador** | P95 | $\le 1.50\text{s}$ ($1500\text{ms}$) | ✅ | 🔴 |
| **Recebedor** | P50 | $\le 1.40\text{s}$ ($1400\text{ms}$) | ✅ | 🔴 |
| **Recebedor** | P95 | $\le 2.30\text{s}$ ($2300\text{ms}$) | ✅ | 🔴 |

As latencias abaixo de 1s sao exibidas em milissegundos (`254.02ms`), e valores iguais ou superiores a 1s sao exibidos em segundos (`1.643s`).

---

## 3. Classificacao dos 12 Servicos SPI e Gatilho Progressivo

O cluster MIP monitora 12 servicos de mensageria e processamento SPI:
- `spi-addressing`
- `spi-addressing-jobs`
- `spi-addressing-queues`
- `spi-auto-pix-messenger`
- `spi-dispute`
- `spi-main`
- `spi-messaging`
- `spi-messaging-processor`
- `spi-messaging-secondary`
- `spi-messaging-secondary-processor`
- `spi-qrcodes1`
- `spi-qrcodes2`

### Metrica Coletada
Os valores numericos ao lado de cada servico representam taxas de operacao (requisicoes por segundo ou volume medio de processamento/logs).

### Gatilho Progressivo de Validacao (M15 -> M5 / M1 / Atual)
1. **Janela Inicial (`[15m]`):** Coleta a media dos ultimos 15 minutos que antecedem o fechamento da janela.
2. **Avaliacao de Spike:** Se a taxa registrada em `[15m]` for $\ge 50.0$ (`LOG_SPIKE_TRIGGER_THRESHOLD`), o coletor dispara verificacao progressiva em janelas mais recentes:
   - Consulta `[5m]` imediatamente anterior ao fechamento da janela.
   - Consulta valor pontual mais recente da janela (`[1m]`).
   - Se a execucao ocorrer apos o encerramento da janela (`now > end_brt`), consulta tambem o valor pontual em tempo real (`[1m]` no instante corrente).
3. **Normalizacao:** Se `M5 < 100.0` (`LOG_M5_NORMALIZED_MAX`) e `min(M1_janela, M1_tempo_real) < 25.0` (`LOG_CURR_NORMALIZED_MAX`), o servico e considerado normalizado. O valor adotado no relatorio e o valor efetivo estabilizado, sem tags poluidoras no texto e com classificacao em **✅ Sem Erros**.
4. **Criterio para 🔴 Com Erros:** Apenas servicos com taxa elevada sustentada que nao atendam aos criterios de normalizacao migram para `🔴 Com Erros`.

---

## 4. Volume de PIXs Recebidos e Pagos

As contagens de transacoes sao aproximadas e acumuladas por bloco de horario do dia:
- `08:30 a 10:30`
- `10:30 a 13:30`
- `13:30 a 16:30`

O relatorio acumula os valores historicos do dia ate a janela corrente.

---

## 5. Classificacao do Status Geral do Ambiente

A avaliacao de saude do ambiente Revolut segue o principio de proporcionalidade ao impacto:
1. **Ambiente estavel ✅**: Ausencia de erros nos logs dos 12 servicos SPI, latencias Pagador/Recebedor dentro dos tetos operacionais e sem chamados ativos.
2. **Ambiente em atencao 🟡**: Presenca de servicos com ocorrencias nos logs (`🔴 Com Erros`), desvios pontuais de latencia sem violacao critica ou chamados abertos em acompanhamento.
3. **Ambiente instavel 🔴**: Latencias violando limites criticos (`has_critical_latency`) ou incidentes graves reportados por clientes.
