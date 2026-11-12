from __future__ import annotations

from pathlib import Path

import pytest
from app.infrastructure.adapters.output import ConsoleAndFileOutputAdapter
from app.infrastructure.settings import load_settings


def test_settings_and_output_adapter(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "KIBANA_HML_USER=a\nKIBANA_HML_PASS=b\n"
        "KIBANA_PRD_USER=c\nKIBANA_PRD_PASS=d\n"
        "GRAFANA_DEFAULT_USER=e\nGRAFANA_DEFAULT_PASS=f\n",
        encoding="utf-8",
    )
    s = load_settings(str(env_file))
    assert s.kibana_hml_user == "a"

    monkeypatch.delenv("KIBANA_HML_USER", raising=False)
    empty_env = tmp_path / ".empty"
    empty_env.write_text("", encoding="utf-8")
    with pytest.raises(ValueError):
        load_settings(str(empty_env))

    out_path = tmp_path / "out" / "rep.md"
    ConsoleAndFileOutputAdapter(out_path).write("hello")
    assert out_path.read_text(encoding="utf-8") == "hello\n"
    ConsoleAndFileOutputAdapter(None).write("stdout-only")
