from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAX_LINES_PER_FILE = 300


def run_step(name: str, cmd: list[str]) -> None:
    print(f"[{name}] executando: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=ROOT)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def validate_structure() -> None:
    required_paths = [
        ROOT / ".env.example",
        ROOT / ".python-version",
        ROOT / "pyproject.toml",
        ROOT / ".gitattributes",
        ROOT / ".gitignore",
        ROOT / ".gitleaks.toml",
        ROOT / ".pre-commit-config.yaml",
        ROOT / ".github" / "workflows.md",
        ROOT / ".github" / "workflows" / "ci.yml",
        ROOT / ".github" / "actions" / "ci" / "setup-python" / "action.yml",
        ROOT / ".github" / "actions" / "ci" / "validate-commitlint" / "action.yml",
        ROOT / ".github" / "actions" / "ci" / "validate-python" / "action.yml",
        ROOT / ".github" / "actions" / "ci" / "validate-scripts" / "action.yml",
        ROOT / ".github" / "actions" / "ci" / "validate-github" / "action.yml",
        ROOT / ".github" / "actions" / "ci" / "sync-tags" / "action.yml",
        ROOT / ".github" / "actions" / "ci" / "release" / "action.yml",
        ROOT / ".github" / "actions" / "shared" / "pipeline-summary" / "action.yml",
        ROOT / "config" / "python.json",
        ROOT / "linters" / "commitlint.config.mjs",
        ROOT / "linters" / "releaserc.json",
        ROOT / "linters" / "README.md",
        ROOT / "linters" / "git-hooks" / "install.sh",
        ROOT / "AGENTS.md",
        ROOT / "prompt-model.md",
        ROOT / ".agents" / "README.md",
        ROOT / ".agents" / "rules" / "architecture-hexagonal-ddd.md",
        ROOT / ".agents" / "rules" / "flagship-dtw-policy.md",
        ROOT / ".agents" / "rules" / "revolut-mip-policy.md",
        ROOT / ".agents" / "rules" / "observability-semantic-logging.md",
        ROOT / ".agents" / "rules" / "code-quality-testing.md",
        ROOT / ".agents" / "skills" / "generate-flagship-report" / "SKILL.md",
        ROOT / ".agents" / "skills" / "generate-revolut-report" / "SKILL.md",
        ROOT / ".agents" / "skills" / "quality-gate" / "SKILL.md",
        ROOT / ".agents" / "skills" / "observability-ops" / "SKILL.md",
        ROOT / "docs" / "arquitetura.md",
        ROOT / "docs" / "structure.md",
        ROOT / "docs" / "engineering-python.md",
        ROOT / "docs" / "engineering-logging.md",
        ROOT / "docs" / "devops.md",
        ROOT / "docs" / "CHANGELOG.md",
        ROOT / "docs" / "README.md",
        ROOT / "app" / "README.md",
        ROOT / "scripts" / "README.md",
        ROOT / "app" / "infrastructure" / "logging" / "__init__.py",
        ROOT / "app" / "infrastructure" / "logging" / "events.py",
        ROOT / "app" / "infrastructure" / "logging" / "redact.py",
        ROOT / "app" / "infrastructure" / "logging" / "emit.py",
        ROOT / "app" / "infrastructure" / "logging" / "formatters.py",
        ROOT / "tests" / "conftest.py",
        ROOT / "tests" / "README.md",
        ROOT / "tests" / "unit" / "README.md",
        ROOT / "tests" / "integration" / "README.md",
    ]
    for path in required_paths:
        if not path.exists():
            raise SystemExit(f"[Validate] arquivo obrigatorio ausente: {path}")

    for py_file in sorted((ROOT / "app").rglob("*.py")):
        line_count = len(py_file.read_text(encoding="utf-8").splitlines())
        if line_count > MAX_LINES_PER_FILE:
            raise SystemExit(f"[Validate] arquivo excede {MAX_LINES_PER_FILE} linhas: {py_file} ({line_count})")
    print("[Validate] estrutura e limites de dimensao aprovados.")


def run_stage(stage: str) -> None:
    py = sys.executable
    if stage in {"lint", "all"}:
        run_step("1/5 Lint - Ruff", [py, "-m", "ruff", "check", "app", "tests", "scripts"])
        run_step("1/5 Lint - Ruff Format", [py, "-m", "ruff", "format", "--check", "app", "tests", "scripts"])
        run_step("1/5 Lint - Mypy", [py, "-m", "mypy", "app", "tests"])
        run_step("1/5 Lint - Vulture", [py, "-m", "vulture", "--min-confidence", "80", "app"])
    if stage in {"security", "all"}:
        run_step("2/5 Security - Bandit", [py, "-m", "bandit", "-q", "-r", "app"])
        run_step("2/5 Security - Pip-Audit", [py, "-m", "pip_audit", "-r", "requirements.txt"])
    if stage in {"test", "all"}:
        run_step("3/5 Test - Pytest", [py, "-m", "pytest"])
    if stage in {"validate", "all"}:
        validate_structure()
    if stage in {"build", "all"}:
        run_step("5/5 Build", [py, "-m", "build", "--no-isolation", "--wheel"])


def main() -> int:
    parser = argparse.ArgumentParser(description="Matriz de Qualidade")
    parser.add_argument(
        "--stage",
        choices=["lint", "security", "test", "validate", "build", "all"],
        default="all",
        help="Estagio especifico para execucao",
    )
    args = parser.parse_args()
    run_stage(args.stage)
    if args.stage == "all":
        print("Todos os 5 estagios da Matriz de Qualidade foram aprovados.")
    else:
        print(f"Estagio '{args.stage}' aprovado com sucesso.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
