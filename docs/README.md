# Documentacao Tecnica e Guias de Engenharia

Indice mestre da documentacao viva, contratos arquiteturais e especificacoes tecnicas do projeto de **Relatorios de Observabilidade (Flagship DTW / Revolut MIP)**.

---

## 1. Documentos Disponiveis

| Documento | Responsabilidade Principal |
| :--- | :--- |
| [arquitetura.md](arquitetura.md) | Visao geral da Arquitetura Hexagonal (Ports & Adapters), Domain-Driven Design (DDD), fluxo do ciclo de vida e diagramas conceituais. |
| [structure.md](structure.md) | Topologia completa e canonica da arvore de diretorios e arquivos do repositorio. |
| [engineering-python.md](engineering-python.md) | Diretrizes de estilo, padroes de codificacao Python 3.13, tipagem estrita com mypy e gestao de dependencias. |
| [engineering-logging.md](engineering-logging.md) | Padroes de telemetria semantica, catalogo de eventos, higienizacao de dados e pacote modular de logging. |
| [devops.md](devops.md) | Matriz de qualidade de 5 estagios deterministas, esteira de CI/CD do GitHub Actions, git-hooks e Makefile. |
| [CHANGELOG.md](CHANGELOG.md) | Historico padronizado de releases semanticas e notas de versao. |

---

## 2. Convencoes e Governanca

- **Sincronizacao Obrigatoria**: Qualquer modificacao contratual, comportamental ou estrutural deve ser refletida de imediato nos documentos correspondentes deste diretorio.
- **Validacao Estrutural**: O script `scripts/quality_gate.py` (executado no estagio `validate`) valida automaticamente a presenca e a integridade de todos os documentos listados acima.
