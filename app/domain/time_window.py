from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime, time
from zoneinfo import ZoneInfo

BRT = ZoneInfo("America/Sao_Paulo")

DAILY_WINDOWS: dict[str, tuple[str, str]] = {
    "08:30-10:30": ("08:30", "10:30"),
    "10:30-13:30": ("10:30", "13:30"),
    "13:30-16:30": ("13:30", "16:30"),
}

WINDOW_ORDER: list[str] = ["08:30-10:30", "10:30-13:30", "13:30-16:30"]


@dataclass(frozen=True)
class TimeWindow:
    key: str
    start_brt: datetime
    end_brt: datetime

    @property
    def label(self) -> str:
        return f"{self.start_brt.strftime('%H:%M')}–{self.end_brt.strftime('%H:%M')}"

    @property
    def end_hour_label(self) -> str:
        return f"{self.end_brt.strftime('%H:%M')}h"

    @property
    def date_label(self) -> str:
        return self.end_brt.strftime("%d/%m")

    @property
    def duration_minutes(self) -> int:
        return max(1, int((self.end_ms - self.start_ms) // 60000))

    @property
    def duration_promql(self) -> str:
        return f"{self.duration_minutes}m"

    @property
    def start_utc_iso(self) -> str:
        return self.start_brt.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%S.000Z")

    @property
    def end_utc_iso(self) -> str:
        return self.end_brt.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%S.999Z")

    @property
    def start_ms(self) -> int:
        return int(self.start_brt.timestamp() * 1000)

    @property
    def end_ms(self) -> int:
        return int(self.end_brt.timestamp() * 1000)


@dataclass(frozen=True)
class WindowCount:
    window_label: str
    count: int


def parse_hhmm(hhmm: str) -> time:
    parts = hhmm.strip().split(":")
    if len(parts) != 2:
        raise ValueError(f"Horario invalido: {hhmm!r}. Esperado HH:MM.")
    return time(hour=int(parts[0]), minute=int(parts[1]))


def build_time_window(target_date: date, window_key: str) -> TimeWindow:
    if window_key not in DAILY_WINDOWS:
        valid = ", ".join(WINDOW_ORDER)
        raise ValueError(f"Janela invalida: {window_key!r}. Opcoes validas: {valid}")
    start_str, end_str = DAILY_WINDOWS[window_key]
    start_dt = datetime.combine(target_date, parse_hhmm(start_str), tzinfo=BRT)
    end_dt = datetime.combine(target_date, parse_hhmm(end_str), tzinfo=BRT)
    return TimeWindow(key=window_key, start_brt=start_dt, end_brt=end_dt)


def windows_up_to(target_date: date, window_key: str) -> list[TimeWindow]:
    if window_key not in WINDOW_ORDER:
        raise ValueError(f"Janela invalida: {window_key!r}")
    idx = WINDOW_ORDER.index(window_key)
    return [build_time_window(target_date, k) for k in WINDOW_ORDER[: idx + 1]]


def detect_current_window(now: datetime | None = None) -> str:
    current = (now or datetime.now(BRT)).astimezone(BRT)
    hhmm = current.strftime("%H:%M")
    if hhmm < "13:30":
        return "08:30-10:30"
    if hhmm < "16:30":
        return "10:30-13:30"
    return "13:30-16:30"
