from datetime import date, datetime

import pytest
from app.domain.time_window import (
    BRT,
    build_time_window,
    detect_current_window,
    parse_hhmm,
    windows_up_to,
)


def test_build_time_window_brt_to_utc() -> None:
    w = build_time_window(date(2026, 11, 11), "08:30-10:30")
    assert w.label == "08:30–10:30"
    assert w.date_label == "11/11"
    assert w.end_hour_label == "10:30h"
    assert w.duration_minutes == 120
    assert w.duration_promql == "120m"
    assert w.start_utc_iso == "2026-11-11T11:30:00.000Z"
    assert w.end_utc_iso == "2026-11-11T13:30:00.999Z"
    assert w.end_ms - w.start_ms == 2 * 3600 * 1000


def test_windows_up_to() -> None:
    ws = windows_up_to(date(2026, 11, 11), "13:30-16:30")
    assert [w.key for w in ws] == ["08:30-10:30", "10:30-13:30", "13:30-16:30"]


def test_invalid_window_and_time_raise() -> None:
    with pytest.raises(ValueError):
        build_time_window(date(2026, 11, 11), "09:00-10:00")
    with pytest.raises(ValueError):
        windows_up_to(date(2026, 11, 11), "09:00-10:00")
    with pytest.raises(ValueError):
        parse_hhmm("0900")


def test_detect_current_window() -> None:
    assert detect_current_window(datetime(2026, 11, 12, 11, 0, tzinfo=BRT)) == "08:30-10:30"
    assert detect_current_window(datetime(2026, 11, 12, 14, 0, tzinfo=BRT)) == "10:30-13:30"
    assert detect_current_window(datetime(2026, 11, 12, 17, 0, tzinfo=BRT)) == "13:30-16:30"
