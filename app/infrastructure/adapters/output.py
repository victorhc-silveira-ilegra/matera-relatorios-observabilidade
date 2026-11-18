from __future__ import annotations

from pathlib import Path


class ConsoleAndFileOutputAdapter:
    def __init__(self, output_path: Path | None = None) -> None:
        self._output_path = output_path

    def write(self, content: str) -> None:
        print(content)
        if self._output_path is not None:
            self._output_path.parent.mkdir(parents=True, exist_ok=True)
            self._output_path.write_text(content + "\n", encoding="utf-8")
