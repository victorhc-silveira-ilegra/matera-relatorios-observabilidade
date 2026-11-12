---
name: generate-revolut-report
description: Procedimento operacional para coleta de metricas e geracao do relatorio MIP da Revolut via proxy HTTP
---

# Skill: Geracao de Relatorio Revolut (MIP)

Esta habilidade orienta a execucao, inspecao e depuracao da geracao de relatorios de observabilidade para a Revolut (MIP - Producao AWS).

## Pre-requisitos

1. Conexao com a VPN corporativa Matera (com rota para o proxy `10.150.8.18:3128`).
2. Arquivo `.env` configurado com:
   - `REVOLUT_GRAFANA_BASE=https://grafana-pvtlink.mip.prd.revolut.maas.link`
   - `REVOLUT_HTTP_PROXY=http://10.150.8.18:3128`
   - `GRAFANA_REVOLUT_USER=admin`
   - `GRAFANA_REVOLUT_PASS`

## Comandos de Execucao

```bash
# Execucao padrao para a janela especifica
.venv/bin/python -m app.presentation.cli --client revolut --window 10:30-13:30

# Especificando data e responsavel
.venv/bin/python -m app.presentation.cli --client revolut --date 12/11 --window 10:30-13:30 --responsavel "Victor Silveira"

# Execucao com chamados em acompanhamento
.venv/bin/python -m app.presentation.cli --client revolut --window 10:30-13:30 --chamados "INC-00123"
```

## Checklist de Validacao das Metricas

1. **Latencias PIX**:
   - Pagador: P50 $\le 900\text{ms}$ e P95 $\le 1.5\text{s}$ com selo `✅`.
   - Recebedor: P50 $\le 1.4\text{s}$ e P95 $\le 2.3\text{s}$ com selo `✅`.
2. **Volumes de PIX**:
   - Confirmar se as contagens aproximadas refletem os blocos acumulados do dia (`08:30 a 10:30`, `10:30 a 13:30`, `13:30 a 16:30`).
3. **Servicos SPI (Ultimos 15m)**:
   - Todos os 12 servicos devem ser listados.
   - Servicos que sofreram picos na janela de 15m mas ja normalizaram nos ultimos minutos (`M5 < 50` e `Atual < 10`) devem permanecer em **✅ Sem Erros** com o valor atual limpo.
   - Status Geral do Ambiente deve refletir `Ambiente estavel ✅` quando nao houver ocorrencias ativas.
