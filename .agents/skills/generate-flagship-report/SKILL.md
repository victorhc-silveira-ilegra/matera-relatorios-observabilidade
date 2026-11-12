---
name: generate-flagship-report
description: Procedimento operacional para coleta de metricas e geracao do relatorio DTW da Flagship (HML e PRD)
---

# Skill: Geracao de Relatorio Flagship (DTW)

Esta habilidade orienta a execucao, inspecao e depuracao da geracao de relatorios de observabilidade para a Flagship (DTW).

## Pre-requisitos

1. Conexao com a VPN corporativa Matera (para acesso aos clusters OpenSearch e Grafana internos).
2. Arquivo `.env` configurado com as variaveis:
   - `OPENSEARCH_HML_BASE`, `KIBANA_HML_USER`, `KIBANA_HML_PASS`
   - `OPENSEARCH_PRD_BASE`, `KIBANA_PRD_USER`, `KIBANA_PRD_PASS`
   - `GRAFANA_HML_BASE`, `GRAFANA_PRD_BASE`, `GRAFANA_USER`, `GRAFANA_PASS`
3. Dependencias do ambiente virtual instaladas via `.venv`.

## Comandos de Execucao

```bash
# Execucao padrao para a janela atual ou especifica
.venv/bin/python -m app.presentation.cli --client flagship --window 10:30-13:30

# Execucao com informacao de chamados ativos
.venv/bin/python -m app.presentation.cli --client flagship --window 10:30-13:30 --chamados-prd "SOL-00357066 em analise"

# Execucao rapida ignorando scraping Playwright de RDS
.venv/bin/python -m app.presentation.cli --client flagship --window 10:30-13:30 --skip-rds

# Gravando saida diretamente em arquivo
.venv/bin/python -m app.presentation.cli --client flagship --window 10:30-13:30 --output relatorio_flagship.txt
```

## Checklist de Validacao das Metricas

1. **Incidentes em PRD**: Verificar se o valor de incidentes reflete a janela dos ultimos 30 minutos (`[30m]`), tipicamente com valores baixos (`~5.1 🟢` ou `~8.1 🟢`). Valores inflados (`> 100`) indicam uso incorreto de janela acumulada.
2. **Incidentes em HML**: Verificar se exibe `Incidentes (últimas 5h): No Data` ou a contagem correta da janela de 5 horas.
3. **Restarts em HML**: Confirmar exibicao de `Restarts de pods (últimas 6h)`.
4. **Integracao SAGA**: Confirmar se `Total de integracoes < 10` e `Integracoes acima de 5 min: 0` mantem o semaforo verde `🟢`.
5. **Status do Ambiente**: PRD so deve ser marcado como `🟡 Atencao` se houver justificativa real (chamado ativo, erro percentual elevado, picos de CPU ou lag).
