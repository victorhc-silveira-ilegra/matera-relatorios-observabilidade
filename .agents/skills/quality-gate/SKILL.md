---
name: quality-gate
description: Protocolo de execucao, diagnostico e resolucao da matriz unificada de qualidade em 5 estagios
---

# Skill: Quality Gate

Esta habilidade rege a execucao e conformidade da matriz de qualidade de 5 estagios deste repositorio.

## Os 5 Estagios Deterministicos

O orquestrador `scripts/quality_gate.py` executa estritamente:

| Ordem | Estagio | Ferramenta | Condicao de Aprovacao |
| :---: | :--- | :--- | :--- |
| **1** | `Lint` | `ruff check` + `mypy --strict` | Zero avisos e tipagem estrita completa em `app/` e `tests/` |
| **2** | `Security` | `bandit -q -r app` | Zero vulnerabilidades de seguranca detectadas |
| **3** | `Test` | `pytest --cov=app --cov-branch --cov-fail-under=100` | 100.00% de cobertura de linhas e ramos |
| **4** | `Validate` | `validate_structure()` | Presenca de arquivos obrigatorios e limite de 300 linhas |
| **5** | `Build` | `python -m build --wheel` | Geracao bem-sucedida do artefato `.whl` |

## Comandos Principais

```bash
# Execucao completa de todos os 5 estagios
make app-quality
# ou
.venv/bin/python scripts/quality_gate.py

# Execucao individual de estagios
make app-lint
make app-security
make app-test
make app-validate
make app-build
```

## Diretrizes de Resolucao de Falhas

1. **Falha de Cobertura (`pytest-cov`)**:
   - Nenhuma linha ou desvio condicional (`branch`) pode ficar sem teste unitario.
   - Proibido o uso de pragmas `# pragma: no cover` sem justificativa formal.
2. **Falha de Seguranca (`bandit`)**:
   - Nao suprimir avisos com `# nosec`. Corrigir a causa raiz na infraestrutura.
3. **Ausencia de Comentarios**:
   - O codigo-fonte Python nao deve conter comentarios nem docstrings em `app/`. O codigo expressa sua intencao atraves de tipagem e nomes semanticos.
4. **Limite de 300 Linhas**:
   - Se um arquivo ultrapassar 300 linhas, quebrar a responsabilidade em modulos coesos antes de submeter ao quality gate.
