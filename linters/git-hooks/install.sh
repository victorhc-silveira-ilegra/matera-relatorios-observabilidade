#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${REPO_ROOT}"

chmod +x linters/git-hooks/bin/resolve_venv_python.sh \
  linters/git-hooks/bin/python \
  linters/git-hooks/bin/pre-commit \
  linters/git-hooks/commitlint.sh \
  linters/git-hooks/commit-msg \
  linters/git-hooks/pre-commit || true

PYTHON_BIN="$(bash linters/git-hooks/bin/resolve_venv_python.sh)"
"${PYTHON_BIN}" -m pip install -q pre-commit
"${PYTHON_BIN}" -m pre_commit install -c .pre-commit-config.yaml
"${PYTHON_BIN}" -m pre_commit install --hook-type commit-msg -c .pre-commit-config.yaml

echo "[OK] pre-commit hooks instalados com ${PYTHON_BIN}"
