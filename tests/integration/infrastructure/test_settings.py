from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from app.infrastructure.adapters.output import (
    ConsoleAndFileOutputAdapter,
    copy_html_to_clipboard,
)
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


def test_output_adapter_clipboard_and_html(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DISPLAY", raising=False)
    monkeypatch.delenv("WAYLAND_DISPLAY", raising=False)
    assert not copy_html_to_clipboard("<b>test</b>")

    monkeypatch.setenv("DISPLAY", ":0")
    monkeypatch.setattr("shutil.which", lambda _: None)
    assert not copy_html_to_clipboard("<b>test</b>")

    monkeypatch.setattr("shutil.which", lambda _: "/usr/bin/xclip")

    def fake_popen_err(*args: Any, **kwargs: Any) -> Any:
        raise OSError("spawn failed")

    monkeypatch.setattr("subprocess.Popen", fake_popen_err)
    assert not copy_html_to_clipboard("<b>test</b>")

    class FakeProc:
        returncode = 0

        def communicate(self, *args: Any, **kwargs: Any) -> tuple[bytes, bytes]:
            return (b"", b"")

    monkeypatch.setattr("subprocess.Popen", lambda *args, **kwargs: FakeProc())
    assert copy_html_to_clipboard("<b>test</b>")

    out_path = tmp_path / "reports" / "rev.md"
    adapter = ConsoleAndFileOutputAdapter(out_path, copy_clipboard=True)
    adapter.write("md_text", html_content="<html>html_text</html>")
    assert out_path.read_text(encoding="utf-8") == "md_text\n"
    assert (tmp_path / "reports" / "rev.html").read_text(encoding="utf-8") == "<html>html_text</html>\n"

    adapter_no_clip = ConsoleAndFileOutputAdapter(None, copy_clipboard=False)
    adapter_no_clip.write("stdout_only", html_content=None)

    monkeypatch.setattr("shutil.which", lambda _: None)
    adapter_fail_clip = ConsoleAndFileOutputAdapter(None, copy_clipboard=True)
    adapter_fail_clip.write("md", html_content="<b>no-xclip</b>")
