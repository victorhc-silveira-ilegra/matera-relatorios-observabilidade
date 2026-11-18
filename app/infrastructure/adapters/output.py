from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


def copy_html_to_clipboard(html_content: str) -> bool:
    if not os.environ.get("DISPLAY") and not os.environ.get("WAYLAND_DISPLAY"):
        return False
    xclip_bin = shutil.which("xclip")
    if xclip_bin is None:
        return False
    try:
        proc = subprocess.Popen(
            [xclip_bin, "-selection", "clipboard", "-t", "text/html"],
            stdin=subprocess.PIPE,
        )
        proc.communicate(html_content.encode("utf-8"))
        return proc.returncode == 0
    except OSError:
        return False


class ConsoleAndFileOutputAdapter:
    def __init__(
        self,
        output_path: Path | None = None,
        copy_clipboard: bool = True,
    ) -> None:
        self._output_path = output_path
        self._copy_clipboard = copy_clipboard

    def write(self, content: str, html_content: str | None = None) -> None:
        print(content)
        if self._output_path is not None:
            self._output_path.parent.mkdir(parents=True, exist_ok=True)
            self._output_path.write_text(content + "\n", encoding="utf-8")
            if html_content is not None:
                self._output_path.with_suffix(".html").write_text(html_content + "\n", encoding="utf-8")

        if html_content is not None and self._copy_clipboard and copy_html_to_clipboard(html_content):
            print("\n📋 [Clipboard: Relatório copiado em Rich Text/HTML para o Google Docs (Ctrl+V)]")
