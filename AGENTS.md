# AGENTS.md

Projeto: Relatorios de Observabilidade (DDD / Arquitetura Hexagonal) — coleta automatizada e geracao de relatorios de observabilidade para os clientes Flagship (DTW) e Revolut (MIP).

## Governanca do Repositorio

Todas as IAs, agentes autonomos e desenvolvedores devem seguir estritamente as regras de arquitetura, qualidade e convencoes estabelecidas em `.agents/rules/` e documentadas em `docs/`.

### Prioridades Absolutas

1. **Arquitetura Hexagonal Estrita**: O codigo reside exclusivamente em `app/` dividido em `domain`, `application`, `infrastructure` e `presentation`. A regra de dependencia flui apenas para dentro (detalhes dependem de abstracoes; o dominio e isolado e puro).
2. **Qualidade e Cobertura 100%**: Toda modificacao de codigo deve ser acompanhada de testes unitarios e de integracao em `tests/`, mantendo 100% de cobertura de desvios (`branch coverage`). Nenhuma regressao e tolerada.
3. **Ausencia de Comentarios no Codigo**: Nao escrever comentarios explicativos nem docstrings desnecessarias nos arquivos Python (`app/` e `tests/`). O codigo deve ser autoexplicativo por meio de nomes semanticos, funcoes coesas e tipagem rigorosa (`mypy --strict`).
4. **Conventional Commits com Escopo Obrigatorio**: Todo commit deve aderir estritamente ao padrao Conventional Commits em portugues brasileiro com escopo obrigatorio no formato `<tipo>(<escopo>): <descricao>` (ex.: `feat(flagship): ...`, `fix(revolut): ...`, `refactor(domain): ...`, `chore(release): ...`). Mensagens sem escopo sao bloqueadas pelo commitlint.
5. **Configuracao Unificada via Ambiente**: Parametros de execucao sao injetados exclusivamente via variaveis de ambiente carregadas de `.env` pela infraestrutura (`Settings`). Credenciais reais e tokens pertencem apenas ao `.env` local e nunca sao versionados.
6. **Sincronizacao de Documentacao**: Qualquer alteracao arquitetural, contratual ou comportamental deve ser imediatamente refletida na documentacao correspondente em `docs/`.
7. **Observabilidade e Logs Semanticos**:
   - `INFO`: Apenas eventos de ciclo chave (`report.generation.started`, `report.generation.completed`).
   - `WARNING`: Falhas parciais que admitem continuidade controlada (timeout tolerado, scrapers opcionais).
   - `ERROR`: Falhas criticas que impedem a execucao da CLI.
   - O dominio e a aplicacao nao realizam chamadas de logging nem acessam bibliotecas de infraestrutura.
   - Separacao estrita entre produto final (relatorio entregue em stdout) e logs operacionais.
8. **Regras de Negocio Deterministicas**:
   - **Flagship (DTW)**: PRD e HML incidentes em janela pontual `[30m]` (Painel 6 de `OCgyltPVk`). Restarts filtrados por pods em execucao (`kube_pod_container_status_running > 0`). SAGA (`0lekC7CVk`): `total < 2000` (`🟢`), `2000–9999` (`🟡`), `>= 10000` (`🔴`); `acima_5m`: `0` (`🟢`), `1–99` (`🟡`), `>= 100` (`🔴`). Polling (`BKo_kE8Sz`): `PROCESSED < 8.5M` (`🟢`), `8.5M–10.5M` (`🟡`), `>= 10.5M` (`🔴`); `PROCESSED = 0` (`total < 80` `🟢`, `>= 80` `🔴`).
   - **Revolut (MIP)**: Acesso obrigatorio via proxy HTTP (`REVOLUT_HTTP_PROXY`). Latencias PIX Pagador (P50: < 0.6s verde, 0.6s–0.9s amarelo, >= 0.9s vermelho; P95: < 1.2s verde, 1.2s–1.5s amarelo, >= 1.5s vermelho) e Recebedor (P50: < 1.0s verde, 1.0s–1.3s amarelo, >= 1.3s vermelho; P95: < 2.0s verde, 2.0s–2.4s amarelo, >= 2.4s vermelho). Gatilho progressivo para 12 servicos SPI: janela `[15m]`, refinando para `[5m]` e `[1m]` em caso de spike para detectar normalizacao recente.
9. **Formato Canonico dos Relatorios**:
   - O texto dos relatorios gerados no stdout deve seguir estritamente o layout padronizado de negocio com emojis e marcadores oficiais estabelecidos pelos clientes.
10. **Alinhamento Continuo com Grafana**:
   - Toda query PromQL/SQL, filtro, janela de avaliacao e limiar de cor (`✅`/`🟢`, `🟡`, `🔴`) deve espelhar fielmente os paineis reais dos dashboards do Grafana de cada cliente. Antes de criar ou alterar regras de coleta ou thresholds, os agentes devem consultar os dashboards via API (`/api/dashboards/uid/<uid>`) para validar `targets`, `thresholds.steps` e `reduceOptions.calcs`.

## Comandos Operacionais

```bash
# Execucao da Matriz de Qualidade (5 estagios: Lint, Security, Test, Validate, Build)
make app-quality

# Execucoes individuais dos estagios
make app-lint
make app-security
make app-test
make app-validate
make app-build

# Geracao de relatorios operacionais
make report-flagship WINDOW=10:30-13:30
make report-revolut WINDOW=10:30-13:30

# Geracao rapida (ignorando scraping visual do CloudWatch)
.venv/bin/python -m app.presentation.cli --client flagship --window 10:30-13:30 --skip-rds
```

## Regras e Habilidades Detalhadas

- Regras arquiteturais e governanca: `.agents/rules/`
- Habilidades operacionais especializadas: `.agents/skills/`
- Manual de arquitetura do sistema: `docs/arquitetura.md`
- Estrutura completa de diretorios: `docs/structure.md`
- Padroes de desenvolvimento em Python: `docs/engineering-python.md`
- Padroes de logging e observabilidade: `docs/engineering-logging.md`
- Matriz de CI/CD e automacao: `docs/devops.md`

## Escopo e Limitacoes

- Suporte restrito aos clientes homologados: `flagship` e `revolut`.
- Consultas ao cluster Grafana da Revolut exigem presenca do proxy HTTP `10.150.8.18:3128` (rede corporativa / VPN).
- Consultas ao CloudWatch da Flagship utilizam automacao headless via Playwright sobre dashboard publico AWS.
