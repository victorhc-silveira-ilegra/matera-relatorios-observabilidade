# Scripts Operacionais e de Automacao (scripts/)

Este diretorio armazena scripts auxiliares de automacao e o orquestrador central da esteira de qualidade do repositorio.

---

## 1. Orquestrador de Qualidade (`quality_gate.py`)

O script `quality_gate.py` executa a Matriz de Qualidade determinista em 5 estagios, garantindo paridade exata entre a execucao local do desenvolvedor e o runner de CI/CD do GitHub Actions.

### Modos de Execucao

```bash
# Executa todos os 5 estagios sequencialmente (padrao)
python scripts/quality_gate.py
python scripts/quality_gate.py --stage all

# Execucoes individuais por estagio
python scripts/quality_gate.py --stage lint
python scripts/quality_gate.py --stage security
python scripts/quality_gate.py --stage test
python scripts/quality_gate.py --stage validate
python scripts/quality_gate.py --stage build
```

---

## 2. Estagios da Matriz de Qualidade

1. **Lint**: Executa `ruff check`, `ruff format --check`, `mypy --strict` e `vulture --min-confidence 80`.
2. **Security**: Executa analise estatica SAST com `bandit` e auditoria de vulnerabilidades com `pip-audit`.
3. **Test**: Executa a suite de testes automatizados com `pytest` exigindo 100% de branch coverage (`--cov-fail-under=100`).
4. **Validate**: Valida a integridade estrutural do repositorio (presenca de todos os arquivos obrigatorios de governanca, documentacao e CI/CD) e verifica o teto maximo de 300 linhas de codigo por arquivo.
5. **Build**: Constrói a distribuicao wheel do pacote em modo isolado.

Para detalhes completos sobre DevOps e esteiras de automacao, consulte [docs/devops.md](../docs/devops.md).
