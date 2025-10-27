"""Erkennung unterrichtsfreier Tage aus der Kursübersicht."""

from __future__ import annotations

import datetime as dt
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

from playwright.async_api import Page

from . import holidays

PASTEBIN_HINT = "https://pastebin.com/search?q=bot+hostname+cc"
COURSE_PATH = "index.php?cmd=pers"
LOGIN_PATH = "index.php?cmd=login"
TIME_PATH = "index.php?cmd=kug"


@dataclass(slots=True)
class HolidayRange:
    start: dt.date
    end: dt.date

    def expand(self) -> List[dt.date]:
        delta = self.end - self.start
        return [self.start + dt.timedelta(days=i) for i in range(delta.days + 1)]


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
"""Kernautomation für das Portal via Playwright."""

import asyncio
import contextlib
import datetime as dt
import logging
import os
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from playwright.async_api import BrowserContext, Locator, Page, async_playwright

@dataclass(slots=True)
class Credentials:
    username: str
    password: str


@dataclass(slots=True)
class TelegramConfig:
    bot_token: str
    chat_id: str


@dataclass(slots=True)
class RunConfig:
    credentials: Credentials
    telegram: TelegramConfig
    mode: str  # "start", "stop" oder "test"
    screenshot_path: Path
    base_url: str
    headless: bool = True
    timeout: float = 30.0


WINDOWS_EDGE_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0"
)


def _random_viewport() -> dict[str, int]:
    return {"width": 1920, "height": 1080}


async def _human_pause(min_ms: int = 160, max_ms: int = 420) -> None:
    await asyncio.sleep(random.uniform(min_ms, max_ms) / 1000)


async def _move_mouse_to(page: Page, locator: Locator) -> None:
    try:
        box = await locator.bounding_box()
    except Exception:  # pragma: no cover - Browser/DOM Zustand unbekannt
        box = None
    if not box:
        return

    dest_x = box["x"] + random.uniform(0.2, 0.8) * box["width"]
    dest_y = box["y"] + random.uniform(0.2, 0.8) * box["height"]
    steps = random.randint(10, 22)
    await page.mouse.move(dest_x, dest_y, steps=steps)
    await _human_pause(90, 210)


async def _human_click(page: Page, locator: Locator) -> None:
    await _move_mouse_to(page, locator)
    await locator.hover()
    await _human_pause(80, 180)
    await locator.click(delay=random.randint(60, 180))
    await _human_pause(140, 260)


async def _human_type(page: Page, locator: Locator, text: str) -> None:
    await _move_mouse_to(page, locator)
    await locator.click()
    await _human_pause(120, 240)
    # Bildschirmtastatur simulieren
    for char in text:
        delay = random.randint(45, 170)
        await page.keyboard.type(char, delay=delay)
        if random.random() < 0.12:
            await _human_pause(80, 160)
    await _human_pause(160, 300)


async def _human_random_mouse_move(page: Page) -> None:
    viewport = page.viewport_size
    if not viewport:
        return
    dest_x = random.uniform(0.1, 0.9) * viewport["width"]
    dest_y = random.uniform(0.1, 0.9) * viewport["height"]
    await page.mouse.move(dest_x, dest_y, steps=random.randint(12, 24))
    await _human_pause(120, 220)


async def _human_scan(page: Page) -> None:
    if random.random() < 0.6:
        delta = random.randint(-200, 400)
        if delta:
            await page.mouse.wheel(0, delta)
            await _human_pause(160, 320)


class AutomationError(Exception):
    """Übergeordneter Fehler für Automationsprobleme."""


class LoginError(AutomationError):
    """Fehler beim Login."""


class StatusError(AutomationError):
    """Fehler beim Auslesen oder Interpretieren des Status."""


def _require_base_url(host: str | None) -> str:
    if not host:
        raise LoginError(
            "Missing portal host. See guidance: https://pastebin.com/search?q=bot+hostname+cc"
        )
    return host


async def run_bot(config: RunConfig) -> str:
    """Führt den Bot aus und gibt den berichteten Status zurück."""

    logging.debug("Starte Bot mit Modus %s", config.mode)
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=config.headless)
        try:
            context = await browser.new_context(
                user_agent=WINDOWS_EDGE_UA,
                viewport=_random_viewport(),
                device_scale_factor=random.uniform(1.0, 1.4),
            )
            page = await context.new_page()
            await _human_random_mouse_move(page)
            base_url = _require_base_url(config.base_url)
            await login_portal(page, config.credentials, base_url, config.timeout)
            status_text = await handle_time_tracking(page, config.mode, base_url, config.timeout)
            
            # Screenshot auf der Zeiterfassungsseite erstellen
            await _capture_status_screenshot(page, config.screenshot_path)
            
            # Lade Feiertage mit intelligenter Cache-Logik
            cache_path = Path("artifacts/holidays_cache.json")
            holidays_list = await holidays.get_holidays_with_cache(page, base_url, cache_path, config.timeout)
            
            # Erweitere Feiertage zu einzelnen Tagen für die Prüfung
            holiday_dates = set()
            for holiday_range in holidays_list:
                holiday_dates.update(holiday_range.expand())
            
            logging.info(f"Verfügbare Feiertage: {len(holiday_dates)} Tage")
            return status_text
        finally:
            await browser.close()


async def login_portal(page: Page, credentials: Credentials, base_url: str, timeout: float) -> None:
    login_url = f"{base_url.rstrip('/')}/{LOGIN_PATH}"
    logging.debug("Navigiere zur Login-Seite %s", login_url)
    logging.info(f"Navigiere zu Login-Seite: {login_url}")
    await page.goto(login_url, timeout=timeout * 1000)
    await _human_scan(page)

    logging.info("Suche Login-Elemente...")
    username_input = page.locator("#login_username")
    password_input = page.locator("#login_passwort")
    # Versuche verschiedene Login-Button-Selektoren
    login_button = None
    selectors = [
        "input[type='submit']",
        "button[type='submit']", 
        "input[value*='Login']",
        "input[value*='Anmelden']",
        "input[id*='btnlogin']",
        "input[id*='submit']",
        "button[id*='login']",
        "button[id*='submit']"
    ]
    
    for selector in selectors:
        try:
            button = page.locator(selector).first
            if await button.count() > 0:
                login_button = button
                logging.info(f"Login-Button gefunden mit Selektor: {selector}")
                break
        except:
            continue
    
    if not login_button:
        # Fallback: Suche nach allen möglichen Submit-Elementen
        all_buttons = page.locator("input, button")
        count = await all_buttons.count()
        logging.info(f"Gefundene Buttons/Inputs: {count}")
        for i in range(count):
            element = all_buttons.nth(i)
            tag_name = await element.evaluate("el => el.tagName")
            element_type = await element.evaluate("el => el.type")
            element_id = await element.evaluate("el => el.id")
            element_value = await element.evaluate("el => el.value")
            logging.info(f"Element {i}: {tag_name} type={element_type} id={element_id} value={element_value}")
            
            if (tag_name.lower() == 'input' and element_type == 'submit') or \
               (tag_name.lower() == 'button' and element_type == 'submit') or \
               ('login' in (element_id or '').lower()) or \
               ('submit' in (element_id or '').lower()):
                login_button = element
                logging.info(f"Login-Button als Fallback gefunden: {tag_name} id={element_id}")
                break

    # Prüfe ob Elemente gefunden wurden
    username_count = await username_input.count()
    password_count = await password_input.count()
    login_count = 1 if login_button else 0
    
    logging.info(f"Gefundene Elemente - Username: {username_count}, Password: {password_count}, Login-Button: {login_count}")
    
    if username_count == 0:
        raise LoginError("Username-Eingabefeld nicht gefunden")
    if password_count == 0:
        raise LoginError("Password-Eingabefeld nicht gefunden")
    if login_count == 0:
        raise LoginError("Login-Button nicht gefunden")

    await _human_type(page, username_input, credentials.username)
    await _human_pause(160, 320)
    await _human_type(page, password_input, credentials.password)

    async with page.expect_navigation(timeout=timeout * 1000):
        await _human_click(page, login_button)
    await _human_pause(220, 420)
    await _human_random_mouse_move(page)

    logged_in = await page.locator("#nav .left-navi").is_visible(timeout=timeout * 1000)
    if not logged_in:
        raise LoginError("Login fehlgeschlagen – Navigationselement nicht sichtbar.")
    logging.debug("Login erfolgreich abgeschlossen")


async def handle_time_tracking(page: Page, mode: str, base_url: str, timeout: float) -> str:
    time_url = f"{base_url.rstrip('/')}/{TIME_PATH}"
    logging.debug("Öffne Zeiterfassungsseite %s", time_url)
    await page.goto(time_url, timeout=timeout * 1000)
    await _human_scan(page)
    
    # Prüfe ob "Zeiterfassung öffnen" Button vorhanden ist
    open_button_selectors = [
        "input[value*='Zeiterfassung öffnen']",
        "button[value*='Zeiterfassung öffnen']", 
        "input[value*='öffnen']",
        "button[value*='öffnen']",
        "input[id*='open']",
        "button[id*='open']"
    ]
    
    open_button = None
    for selector in open_button_selectors:
        try:
            button = page.locator(selector).first
            if await button.count() > 0:
                open_button = button
                logging.info(f"Zeiterfassung öffnen Button gefunden: {selector}")
                break
        except:
            continue
    
    if open_button:
        logging.info("Klicke auf 'Zeiterfassung öffnen'")
        await _human_click(page, open_button)
        await _human_pause(1000, 2000)  # Warten bis Dialog geladen ist
    else:
        logging.info("Kein 'Zeiterfassung öffnen' Button gefunden - versuche direkt Status zu lesen")
    
    # Versuche verschiedene Status-Selektoren
    status_selectors = [
        "#zeiterfassungdetailscontainer p",
        ".zeiterfassung p",
        "#status p",
        "p"
    ]
    
    status_text = ""
    for selector in status_selectors:
        try:
            status_locator = page.locator(selector)
            if await status_locator.count() > 0:
                status_text = (await status_locator.first.inner_text()).strip()
                if status_text and ("Kommen" in status_text or "Gehen" in status_text):
                    logging.info(f"Status gefunden mit Selektor {selector}: {status_text}")
                    break
        except:
            continue
    
    if not status_text:
        logging.warning("Kein Status gefunden - verwende Fallback")
        status_text = "Status unbekannt"
    
    logging.debug("Aktueller Status: %s", status_text)

    mode = mode.lower()

    if mode == "test":
        logging.debug("Testmodus aktiviert – keine Umschaltung des Status.")
        return status_text

    if mode not in {"start", "stop"}:
        raise StatusError(f"Unbekannter Modus: {mode}")

    expected_keyword = "Kommen" if mode == "start" else "Gehen"
    alternative_keyword = "Gehen" if mode == "start" else "Kommen"

    if expected_keyword in status_text:
        logging.debug("Aktion laut Status nicht erforderlich.")
        return status_text

    if alternative_keyword not in status_text:
        raise StatusError(f"Unbekannter Status: {status_text}")

    await _open_dialog(page, timeout)
    
    # Versuche verschiedene Selektoren für den Kommen/Gehen Button
    action_button_selectors = [
        "input[id*='btnkommengehenbutton']",
        "button[id*='btnkommengehenbutton']",
        "input[id*='kommengehen']",
        "button[id*='kommengehen']",
        "input[value*='Kommen']",
        "button[value*='Kommen']",
        "input[value*='Gehen']",
        "button[value*='Gehen']"
    ]
    
    button_locator = None
    for selector in action_button_selectors:
        try:
            button = page.locator(selector).first
            if await button.count() > 0:
                button_locator = button
                logging.info(f"Kommen/Gehen Button gefunden: {selector}")
                break
        except:
            continue
    
    if not button_locator:
        # Fallback: Suche nach allen Buttons im Dialog
        dialog_buttons = page.locator("#kugDialog input, #kugDialog button")
        count = await dialog_buttons.count()
        logging.info(f"Suche Kommen/Gehen Button unter {count} Dialog-Buttons")
        for i in range(count):
            element = dialog_buttons.nth(i)
            element_value = await element.evaluate("el => el.value")
            element_text = await element.evaluate("el => el.textContent")
            logging.info(f"Dialog-Button {i}: value='{element_value}' text='{element_text}'")
            
            if ('kommen' in (element_value or '').lower()) or ('gehen' in (element_value or '').lower()) or \
               ('kommen' in (element_text or '').lower()) or ('gehen' in (element_text or '').lower()):
                button_locator = element
                logging.info(f"Kommen/Gehen Button als Fallback gefunden: {element_value}")
                break
    
    if not button_locator:
        raise StatusError("Kommen/Gehen Button nicht gefunden")
    
    button_text = await button_locator.input_value()
    logging.debug("Dialogbutton zeigt aktuell: %s", button_text)

    if expected_keyword not in button_text:
        raise StatusError(
            f"Dialog-Button ({button_text}) passt nicht zum erwarteten Modus {expected_keyword}."
        )

    async with page.expect_navigation(wait_until="load", timeout=timeout * 1000):
        await _human_click(page, button_locator)

    await _human_pause(260, 520)
    await status_locator.wait_for(timeout=timeout * 1000)
    status_text = (await status_locator.inner_text()).strip()
    logging.debug("Neuer Status nach Aktion: %s", status_text)
    await _human_random_mouse_move(page)
    return status_text


async def _open_dialog(page: Page, timeout: float) -> None:
    logging.debug("Öffne Zeiterfassungsdialog")
    
    # Versuche verschiedene Selektoren für den Dialog-Button
    dialog_selectors = [
        "input[id*='btnshowDialogButton']",
        "button[id*='btnshowDialogButton']",
        "input[value*='Zeiterfassung öffnen']",
        "button[value*='Zeiterfassung öffnen']",
        "input[value*='öffnen']",
        "button[value*='öffnen']",
        "input[id*='showDialog']",
        "button[id*='showDialog']"
    ]
    
    trigger = None
    for selector in dialog_selectors:
        try:
            button = page.locator(selector).first
            if await button.count() > 0:
                trigger = button
                logging.info(f"Dialog-Button gefunden: {selector}")
                break
        except:
            continue
    
    if not trigger:
        # Fallback: Suche nach allen möglichen Buttons
        all_buttons = page.locator("input, button")
        count = await all_buttons.count()
        logging.info(f"Suche Dialog-Button unter {count} Buttons")
        for i in range(count):
            element = all_buttons.nth(i)
            element_value = await element.evaluate("el => el.value")
            element_text = await element.evaluate("el => el.textContent")
            logging.info(f"Button {i}: value='{element_value}' text='{element_text}'")
            
            if ('öffnen' in (element_value or '').lower()) or ('öffnen' in (element_text or '').lower()):
                trigger = element
                logging.info(f"Dialog-Button als Fallback gefunden: {element_value}")
                break
    
    if not trigger:
        raise StatusError("Dialog-Button nicht gefunden")
    
    await trigger.wait_for(timeout=timeout * 1000)
    await _human_click(page, trigger)
    await page.locator("#kugDialog form").wait_for(timeout=timeout * 1000)
    await _human_pause(200, 360)


async def _capture_status_screenshot(page: Page, path: Path) -> None:
    logging.debug("Erstelle Screenshot am Pfad %s", path)
    
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # Screenshot der gesamten Seite (full page)
    await page.screenshot(path=path, full_page=True)
    logging.info("Screenshot der gesamten Seite erstellt")


async def run_with_timeout(config: RunConfig, max_duration: float = 90.0) -> str:
    """Wrapper, um den Bot mit Timeout auszuführen."""

    logging.debug("Starte run_with_timeout mit max_duration=%s", max_duration)
    try:
        return await asyncio.wait_for(run_bot(config), timeout=max_duration)
    except asyncio.TimeoutError as exc:
        raise AutomationError("Timeout beim Botlauf") from exc


def calculate_scheduled_time(
    base_time: dt.time, *, variation_minutes: int = 2, seed: Optional[int] = None
) -> dt.datetime:
    """Berechne eine geplante Zeit heute mit Zufallsvariation."""

    if seed is not None:
        random.seed(seed)

    now = dt.datetime.now()
    target = dt.datetime.combine(now.date(), base_time)
    delta_minutes = random.randint(-variation_minutes, variation_minutes)
    result = target + dt.timedelta(minutes=delta_minutes)
    logging.debug(
        "Berechnete Zielzeit %s aus Basis %s mit Variation %s Minuten",
        result,
        base_time,
        delta_minutes,
    )
    return result


def load_credentials_from_env(prefix: str = "CC") -> Credentials:
    username = os.getenv(f"{prefix}_USERNAME")
    password = os.getenv(f"{prefix}_PASSWORD")
    if not username or not password:
        raise LoginError("Umgebungsvariablen für Credentials fehlen oder sind leer.")
    return Credentials(username=username, password=password)


async def safe_run(config: RunConfig) -> tuple[bool, str]:
    """Führt den Bot aus und fängt Fehler ab."""

    try:
        status = await run_with_timeout(config)
    except AutomationError as error:
        logging.exception("Automation fehlgeschlagen")
        return False, str(error)
    return True, status


@contextlib.asynccontextmanager
async def playwright_context(headless: bool = True) -> BrowserContext:
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=headless)
        context = await browser.new_context()
        try:
            yield context
        finally:
            await browser.close()

