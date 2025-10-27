"""Erkennung unterrichtsfreier Tage aus der Kursübersicht."""

from __future__ import annotations

import datetime as dt
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from playwright.async_api import Page

COURSE_PATH = "index.php?cmd=pers"


@dataclass(slots=True)
class HolidayRange:
    start: dt.date
    end: dt.date

    def expand(self) -> list[dt.date]:
        delta = self.end - self.start
        return [self.start + dt.timedelta(days=i) for i in range(delta.days + 1)]


async def fetch_holidays(page: Page, base_url: str, timeout: float = 30.0) -> list[HolidayRange]:
    """Liest unterrichtsfreie Zeiträume von der Kursübersicht."""

    url = f"{base_url.rstrip('/')}/{COURSE_PATH}"
    logging.debug("Öffne Kursübersicht %s", url)
    await page.goto(url, timeout=timeout * 1000)
    rows = page.locator("tr.table-row")

    holiday_ranges: list[HolidayRange] = []
    count = await rows.count()
    logging.debug("Gefundene Kurszeilen: %s", count)

    for index in range(count):
        row = rows.nth(index)
        title_locator = row.locator("td.bold").first
        if not await title_locator.count():
            continue
        title = (await title_locator.inner_text()).strip()
        if "Unterrichtsfreie Zeit" not in title:
            continue

        cols = row.locator("td")
        if await cols.count() < 4:
            continue

        start_raw = (await cols.nth(2).inner_text()).strip()
        end_raw = (await cols.nth(3).inner_text()).strip()

        try:
            start = dt.datetime.strptime(start_raw, "%d.%m.%Y").date()
            end = dt.datetime.strptime(end_raw, "%d.%m.%Y").date()
        except ValueError:
            logging.warning("Konnte Datum nicht parsen: %s - %s", start_raw, end_raw)
            continue

        holiday_ranges.append(HolidayRange(start=start, end=end))

    logging.info("Gefundene freie Zeiträume: %s", holiday_ranges)
    return holiday_ranges


def trim_to_window(
    holidays: Iterable[HolidayRange], window_start: dt.date, window_end: dt.date
) -> list[HolidayRange]:
    trimmed: list[HolidayRange] = []
    for holiday in holidays:
        if holiday.end < window_start or holiday.start > window_end:
            continue
        start = max(holiday.start, window_start)
        end = min(holiday.end, window_end)
        trimmed.append(HolidayRange(start=start, end=end))
    return trimmed


def save_holidays(path: Path, holidays: Iterable[HolidayRange]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = [
        {
            "start": holiday.start.strftime("%Y-%m-%d"),
            "end": holiday.end.strftime("%Y-%m-%d"),
        }
        for holiday in holidays
    ]
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_holiday_dates(path: Path) -> set[dt.date]:
    if not path.exists():
        return set()

    content = json.loads(path.read_text(encoding="utf-8"))
    dates: set[dt.date] = set()
    for entry in content:
        start = dt.datetime.strptime(entry["start"], "%Y-%m-%d").date()
        end = dt.datetime.strptime(entry["end"], "%Y-%m-%d").date()
        delta = end - start
        for offset in range(delta.days + 1):
            dates.add(start + dt.timedelta(days=offset))
    return dates

