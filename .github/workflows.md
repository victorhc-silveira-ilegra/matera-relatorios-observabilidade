# Workflows de Integracao Continua e Release (GitHub Actions)

Especificacao tecnica dos workflows de automacao, composite actions e gatilhos de execucao configurados no GitHub Actions para o repositorio **Relatorios de Observabilidade (Flagship DTW / Revolut MIP)**.

## 1. Mapeamento de Workflows

| Arquivo de Workflow | Gatilhos de Disparo | Responsabilidade Principal |
| :--- | :--- | :--- |
| [ci.yml](workflows/ci.yml) | Push em `main`, Pull Requests para `main`, `workflow_dispatch` | Execucao paralela da matriz de qualidade por area e entrega continua (Semantic Release) |

## 2. Catalogo de Composite Actions Reutilizaveis

As automacoes de CI/CD utilizam acoes compostas modulares localizadas em `.github/actions/`:

```text
.github/actions/
├── shared/
│   └── pipeline-summary/          # Consolidacao e publicacao de resumo no GitHub Step Summary
└── ci/
    ├── setup-python/              # Configuracao do interpretador Python e restauracao de caches
    ├── validate-commitlint/       # Validacao de mensagens de commit (Conventional Commits)
    ├── validate-python/           # Execucao dos quality gates de Python (Lint, Sec, Test, Val, Build)
    ├── validate-scripts/          # Analise de scripts shell, permissoes e syntax checks
    ├── validate-github/           # Validacao estrutural de workflows, actions e gitleaks
    ├── sync-tags/                 # Sincronizacao de tags Git e remocao de orfas
    └── release/                   # Execucao do semantic-release e publicacao de artefatos
```

## 3. Comportamento Operacional e Filtros

- **Push na Branch `main`**: Dispara a execucao paralela de todas as areas (`commitlint`, `python`, `scripts`, `github`). Quando todas as etapas concluem com sucesso, aciona o job de `release`, exceto se houver indicacao de `[skip-cd]` na mensagem de commit.
- **Pull Requests**: Dispara a validacao de todas as 4 areas para assegurar que nenhum codigo seja integrado sem 100% de conformidade com os quality gates.
- **Disparo Manual (`workflow_dispatch`)**: Permite acionamento sob demanda via interface web do GitHub ou CLI `gh`, suportando o parametro booleano `skip_cd` para controlar a publicacao de releases.

Para detalhes completos sobre a esteira de entrega, consulte [docs/devops.md](../docs/devops.md).
