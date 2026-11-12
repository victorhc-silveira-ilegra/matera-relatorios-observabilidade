# Linters, Git Hooks, QA e Governanca de Releases

Especificacao dos padroes de qualidade de codigo, analise estatica, hooks locais e automacao de releases do projeto **Relatorios de Observabilidade**.

---

## 1. Pre-commit e Paridade com Qualidade

A configuracao de hooks em `.pre-commit-config.yaml` opera sob o principio de interrupcao imediata na primeira falha (`fail_fast: true`) e executa:

1. **Commitlint**: Validacao da mensagem de commit no hook `commit-msg` local com base na especificacao Conventional Commits via `.pre-commit-config.yaml` e `linters/git-hooks/commitlint.sh`.
2. **Estagio 1 (Lint)**: Ruff Check (estilo e boas praticas), Ruff Format Check, Mypy Strict (tipagem estrita) e Vulture (deteccao de codigo morto).
3. **Estagio 2 (Seguranca)**: Bandit (SAST contra vulnerabilidades de codigo Python) e Pip-Audit (auditoria de CVEs em dependencias).
4. **Estagio 3 (Testes)**: Pytest com exigencia inegociavel de 100% de cobertura de linhas e ramos (`--cov-branch --cov-fail-under=100`).
5. **Estagio 4 (Validate)**: Validacao de integridade estrutural da arvore de arquivos e limite maximo de 300 linhas por arquivo em `app/`.
6. **Estagio 5 (Build)**: Compilacao e empacotamento wheel isolado (`python -m build`).

---

## 2. Instalacao e Execucao de Hooks

```bash
# Instalacao dos hooks no repositorio git local
make app-pre-commit

# Execucao manual dos hooks sobre toda a arvore de arquivos
make app-pre-commit-run
```

---

## 3. Especificacao do Commitlint

A governanca de mensagens exige aderencia estrita a convencao Conventional Commits com **escopo semantico obrigatorio** (`linters/commitlint.config.mjs`):

- **Tipos Permitidos**: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`.
- **Idioma**: Portugues brasileiro.
- **Estrutura**: `<tipo>(<escopo>): <descricao em letras minusculas>` (o escopo e obrigatorio e deve estar em letras minusculas).
- **Escopos Permitidos**:
  - `app`: Nucleo da aplicacao, entrypoint CLI e configuracoes compartilhadas.
  - `application`: Casos de uso e portas hexagonais.
  - `ci`: Workflows GitHub Actions e composite actions.
  - `deps`: Gestao de dependencias em `requirements*.txt` e `pyproject.toml`.
  - `docs`: Documentacao tecnica em `docs/` e `README.md`.
  - `domain`: Entidades e regras de negocio puras.
  - `flagship`: Coletores, regras e formatacao do cliente Flagship DTW.
  - `harness`: Regras arquiteturais e skills em `.agents/` e `AGENTS.md`.
  - `hooks`: Git hooks e orquestracao do pre-commit.
  - `infra`: Adaptadores de infraestrutura (CloudWatch, Grafana, OpenSearch, Logging).
  - `linters`: Configuracoes de linters, formatadores e commitlint.
  - `makefile`: Alvos operacionais e automacoes no Makefile.
  - `presentation`: Camada CLI e adaptadores de saida.
  - `release`: Automacao de versionamento semantico e geracao de changelog.
  - `reports`: Orquestracao consolidada dos relatorios.
  - `revolut`: Coletores, regras e formatacao do cliente Revolut MIP.
  - `scripts`: Scripts utilitarios e quality gate.
  - `tests`: Suite de testes unitarios e de integracao.
- **Exemplos Validos**:
  - `feat(flagship): adiciona suporte ao coletor de logs`
  - `fix(revolut): corrige consulta progressiva de metricas nos servicos spi`
  - `chore(release): 0.2.0 [skip ci]`

---

## 4. Analise Estatica e Ferramentas de QA

- **Ruff**: Linter e formatador de altissima performance, configurado com tamanho de linha de 120 caracteres (`pyproject.toml`).
- **Mypy**: Verificacao estatica de tipos com `strict = true` em todas as camadas.
- **Vulture**: Deteccao automatizada de codigo morto ou variaveis nao utilizadas com confianca minima de 80%.
- **Bandit**: Varredura SAST de seguranca em codigo-fonte Python.
- **Pip-Audit**: Auditoria de seguranca contra vulnerabilidades conhecidas (CVEs) no inventario de dependencias.
- **Gitleaks**: Auditoria de credenciais acidentalmente versionadas via `.gitleaks.toml`.

---

## 5. Semantic Release

O arquivo `linters/releaserc.json` rege a automacao de versionamento continuo na branch `main`:
1. Analisa as mensagens de commit desde a ultima release (`@semantic-release/commit-analyzer`).
2. Determina a versao semantica subsequente (Patch, Minor ou Major).
3. Atualiza o arquivo `docs/CHANGELOG.md` com as notas estruturadas da release.
4. Atualiza a variavel `version = "..."` no arquivo `pyproject.toml`.
5. Cria commit e tag Git assinada no repositorio.
