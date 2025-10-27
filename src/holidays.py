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
        
        # Debug: Zeige alle Zeilen-Inhalte
        try:
            row_text = await row.inner_text()
            logging.debug(f"Zeile {index}: {row_text[:100]}...")
        except:
            logging.debug(f"Zeile {index}: Fehler beim Lesen")
            continue
            
        title_locator = row.locator("td.bold").first
        if not await title_locator.count():
            # Versuche alternative Selektoren
            title_locator = row.locator("td").first
            if not await title_locator.count():
                continue
                
        title = (await title_locator.inner_text()).strip()
        logging.debug(f"Zeile {index} Titel: '{title}'")
        
        if "Unterrichtsfreie Zeit" not in title and "unterrichtsfrei" not in title.lower():
            continue

        cols = row.locator("td")
        col_count = await cols.count()
        logging.debug(f"Zeile {index} hat {col_count} Spalten")
        
        if col_count < 4:
            logging.warning(f"Zeile {index} hat zu wenige Spalten: {col_count}")
            continue

        start_raw = (await cols.nth(2).inner_text()).strip()
        end_raw = (await cols.nth(3).inner_text()).strip()
        
        logging.debug(f"Zeile {index} Daten: '{start_raw}' - '{end_raw}'")

        try:
            start = dt.datetime.strptime(start_raw, "%d.%m.%Y").date()
            end = dt.datetime.strptime(end_raw, "%d.%m.%Y").date()
            logging.info(f"Freier Zeitraum gefunden: {start} - {end}")
        except ValueError as e:
            logging.warning("Konnte Datum nicht parsen: %s - %s (Fehler: %s)", start_raw, end_raw, e)
            continue

        holiday_ranges.append(HolidayRange(start=start, end=end))

    logging.info("Gefundene freie Zeiträume: %s", holiday_ranges)
    return holiday_ranges


def should_refresh_holidays(cache_path: Path) -> bool:
    """Prüft ob die Feiertage-Cache erneuert werden muss (alle 30 Tage)."""
    if not cache_path.exists():
        return True
    
    # Prüfe das Alter der Cache-Datei
    cache_age = dt.datetime.now() - dt.datetime.fromtimestamp(cache_path.stat().st_mtime)
    return cache_age.days >= 30


def filter_future_holidays(holidays: Iterable[HolidayRange]) -> list[HolidayRange]:
    """Filtert nur zukünftige Feiertage heraus."""
    today = dt.date.today()
    future_holidays = []
    
    for holiday in holidays:
        # Nur Feiertage die heute oder in der Zukunft liegen
        if holiday.end >= today:
            future_holidays.append(holiday)
    
    return future_holidays


async def get_holidays_with_cache(page: Page, base_url: str, cache_path: Path, timeout: float = 30.0) -> list[HolidayRange]:
    """Lädt Feiertage mit intelligenter Cache-Logik."""
    
    # Prüfe ob Cache erneuert werden muss
    if not should_refresh_holidays(cache_path):
        logging.info("Verwende gecachte Feiertage (Cache ist noch aktuell)")
        return load_holiday_ranges(cache_path)
    
    logging.info("Cache ist veraltet oder nicht vorhanden - lade Feiertage neu")
    
    # Lade neue Feiertage vom Portal
    all_holidays = await fetch_holidays(page, base_url, timeout)
    
    # Filtere nur zukünftige Feiertage
    future_holidays = filter_future_holidays(all_holidays)
    
    logging.info(f"Gefunden: {len(all_holidays)} Feiertage total, {len(future_holidays)} zukünftige")
    
    # Speichere nur zukünftige Feiertage im Cache
    save_holidays(cache_path, future_holidays)
    
    return future_holidays


def load_holiday_ranges(path: Path) -> list[HolidayRange]:
    """Lädt Feiertage aus der Cache-Datei."""
    if not path.exists():
        return []
    
    content = json.loads(path.read_text(encoding="utf-8"))
    holidays = []
    for entry in content:
        start = dt.datetime.strptime(entry["start"], "%Y-%m-%d").date()
        end = dt.datetime.strptime(entry["end"], "%Y-%m-%d").date()
        holidays.append(HolidayRange(start=start, end=end))
    
    return holidays


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

