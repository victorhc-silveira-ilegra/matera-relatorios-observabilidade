from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _isolate_test_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TESTING", "1")
