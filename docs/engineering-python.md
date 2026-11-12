# Engenharia e Convencoes Python

Este documento define os padroes de desenvolvimento, analise estatica e formatacao para o ecossistema Python do projeto.

---

## 1. Versao e Interpretador

- Python 3.11+ (homologado em Python 3.13).
- O projeto adota padroes modernos de linguagem:
  - `from __future__ import annotations` em todos os modulos.
  - `StrEnum` nativo do modulo `enum`.
  - `datetime.now(UTC)` e `timezone.utc`.
  - Type hints nativos sem importar `typing.List`, `typing.Dict` ou `typing.Optional` (`list[str]`, `dict[str, Any]`, `T | None`).

---

## 2. Tipagem Estrita (`mypy --strict`)

Todas as camadas do projeto (`app/` e `tests/`) sao validadas no modo estrito do `mypy`.
- Proibido o uso de `Any` implicito.
- Funcoes e metodos devem declarar tipos completos de todos os parametros e do retorno.
- Em caso de bibliotecas externas sem tipagem estrita, isolar o comportamento na camada de infraestrutura com conversores de tipo explicitos.

---

## 3. Linters e Formatacao (`ruff`)

- O projeto utiliza `ruff` para formatacao e linting.
- Limite maximo de linha configurado para 120 caracteres (`line-length = 120` em `pyproject.toml`).
- Ordenacao automatica de imports atraves do plugin `isort` integrado ao ruff.

---

## 4. Ausencia de Comentarios no Codigo

O codigo de aplicacao em `app/` segue a diretriz inegociavel de **zero comentarios**:
- Nao adicionar comentarios explicativos nem docstrings repetitivas.
- As intencoes do codigo devem ser expressas atraves de:
  - Nomes semanticos e especificos para variaveis, metodos e classes.
  - Funcoes pequenas com responsabilidade unica.
  - Assinaturas de tipo expressivas.
- Comentarios sao tolerados exclusivamente na documentacao formal em `docs/` e nos manuais do harness em `.agents/`.

---

## 5. Dimensao de Modulos

- Nenhum arquivo em `app/` deve ultrapassar **300 linhas de codigo**.
- Ao se aproximar deste teto, extraia componentes coesos em novos modulos.
