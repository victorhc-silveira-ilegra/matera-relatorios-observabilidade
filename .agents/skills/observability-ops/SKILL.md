---
name: observability-ops
description: Procedimentos de diagnostico de conectividade de rede, proxy HTTP, headless browser e ambiente
---

# Skill: Observability Ops

Esta habilidade orienta o diagnostico operacional de conectividade de rede, configuracao de proxies corporativos e navegadores headless para o sistema de relatorios.

## Diagnostico de Conectividade de Rede

### 1. Clusters OpenSearch e Grafana Flagship
Para testar conectividade com os endpoints da Flagship:
```bash
curl -s -k -u "${KIBANA_PRD_USER}:${KIBANA_PRD_PASS}" "${OPENSEARCH_PRD_BASE}/_cluster/health"
curl -s -u "${GRAFANA_USER}:${GRAFANA_PASS}" "${GRAFANA_PRD_BASE}/api/health"
```
Se houver falha de resolucao de DNS ou timeout, certifique-se de que a VPN Matera esteja ativa.

### 2. Grafana Revolut via Proxy HTTP
O endpoint `grafana-pvtlink.mip.prd.revolut.maas.link` so responde se a requisicao trafegar atraves da proxy corporativa `10.150.8.18:3128`:
```bash
curl -x "http://10.150.8.18:3128" -s -u "${GRAFANA_REVOLUT_USER}:${GRAFANA_REVOLUT_PASS}" "https://grafana-pvtlink.mip.prd.revolut.maas.link/api/health"
```
Se o curl retornar `HTTP 200 {"commit":"...","database":"ok"}`, a conectividade via proxy esta validada.

### 3. AWS CloudWatch Public Dashboard (Playwright)
O scraping de metricas do RDS utiliza o Playwright em modo headless para renderizar os graficos do dashboard publico AWS:
- Se os navegadores do Playwright nao estiverem instalados no ambiente:
  ```bash
  .venv/bin/playwright install chromium
  ```
- Para execucoes rapidas de desenvolvimento ou homologacao onde nao e necessario aguardar a carga do dashboard da AWS, utilize o parametro `--skip-rds`.

## Higienizacao de Ambiente

```bash
# Limpeza de artefatos de build, cache de pytest e coverage
make clean
```
