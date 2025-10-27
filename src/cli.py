"""CLI-Einstiegspunkt für den CC Login Bot."""

from __future__ import annotations

import argparse
import asyncio
import datetime as dt
import logging
import random
import sys
from pathlib import Path
from typing import Optional

from telegram import Bot, InputFile

from .bot import Credentials, RunConfig, TelegramConfig, safe_run


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="CC Login Bot")
    parser.add_argument("--username", required=True, help="Login-Benutzername")
    parser.add_argument("--password", required=True, help="Login-Passwort")
    parser.add_argument("--bot-token", required=True, help="Telegram Bot Token")
    parser.add_argument("--chat-id", required=True, help="Telegram Chat ID")
    parser.add_argument(
        "--host",
        required=True,
        help="Hostname des Portals",
    )
    parser.add_argument(
        "--mode",
        choices=["start", "stop", "test"],
        required=True,
        help="Modus für Zeiterfassung (start=Kommen, stop=Gehen, test=kein Button)",
    )
    parser.add_argument(
        "--screenshot-path",
        default=None,
        help="Pfad für den Screenshot (optional, sonst Standardpfad)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=45.0,
        help="Timeout in Sekunden für Seitennavigationen",
    )
    parser.add_argument(
        "--headless",
        dest="headless",
        action="store_true",
        default=True,
        help="Playwright im Headless-Modus (Standard)",
    )
    parser.add_argument(
        "--no-headless",
        dest="headless",
        action="store_false",
        help="Playwright im sichtbaren Modus",
    )
    parser.add_argument(
        "--start-time",
        default="13:20",
        help="Planmäßige Startzeit (hh:mm) für Modus start",
    )
    parser.add_argument(
        "--end-time",
        default="17:30",
        help="Planmäßige Endzeit (hh:mm) für Modus stop",
    )
    parser.add_argument(
        "--variation-minutes",
        type=int,
        default=2,
        help="Zufallsvariation in Minuten (+/-)",
    )
    parser.add_argument(
        "--apply-variation",
        action="store_true",
        help="Führt vor dem Start eine zufällige Verzögerung aus",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        help="Logging-Level (z. B. INFO, DEBUG)",
    )
    return parser


def configure_logging(level: str) -> None:
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


async def send_telegram_report(
    telegram_cfg: TelegramConfig,
    mode: str,
    success: bool,
    status_text: str,
    screenshot_path: Path,
) -> None:
    bot = Bot(telegram_cfg.bot_token)
    timestamp = dt.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    headline = "✅ Erfolg" if success else "❌ Fehler"
    message = (
        f"{headline} ({mode.capitalize()})\n"
        f"Zeitpunkt: {timestamp}\n"
        f"Status: {status_text}"
    )

    try:
        if success and screenshot_path.exists():
            with screenshot_path.open("rb") as file:
                await bot.send_photo(
                    chat_id=telegram_cfg.chat_id,
                    photo=InputFile(file, filename=screenshot_path.name),
                    caption=message,
                )
        else:
            await bot.send_message(chat_id=telegram_cfg.chat_id, text=message)
    finally:
        await bot.close()


def _parse_time(timestr: str) -> dt.time:
    return dt.datetime.strptime(timestr, "%H:%M").time()


async def _apply_variation_if_needed(args: argparse.Namespace) -> None:
    if not args.apply_variation:
        return

    scheduled_str = args.start_time if args.mode == "start" else args.end_time
    base_time = _parse_time(scheduled_str)
    variation = max(0, args.variation_minutes)

    wait_minutes = random.randint(0, variation * 2)
    wait_seconds = wait_minutes * 60 + random.randint(0, 59)

    logging.info(
        "Starte Verzögerung für Modus %s: Basis %s, Variation ±%s Minuten, gewartet %s Sekunden",
        args.mode,
        base_time.strftime("%H:%M"),
        variation,
        wait_seconds,
    )
    if wait_seconds > 0:
        await asyncio.sleep(wait_seconds)


async def async_main(args: argparse.Namespace) -> int:
    credentials = Credentials(args.username, args.password)
    telegram_cfg = TelegramConfig(args.bot_token, args.chat_id)

    screenshot_path = (
        Path(args.screenshot_path)
        if args.screenshot_path
        else Path("artifacts")
        / f"status_{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    )

    await _apply_variation_if_needed(args)

    run_config = RunConfig(
        credentials=credentials,
        telegram=telegram_cfg,
        mode=args.mode,
        screenshot_path=screenshot_path,
        base_url=f"https://{args.host}",
        headless=args.headless,
        timeout=args.timeout,
    )

    success, status_text = await safe_run(run_config)
    await send_telegram_report(telegram_cfg, args.mode, success, status_text, screenshot_path)
    return 0 if success else 1


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    configure_logging(args.log_level.upper())
    try:
        return asyncio.run(async_main(args))
    except KeyboardInterrupt:
        logging.warning("Manuell abgebrochen")
        return 2


if __name__ == "__main__":
    sys.exit(main())

