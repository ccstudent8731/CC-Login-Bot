"""Cron-orientierte Ablaufsteuerung für den Docker-Container."""

from __future__ import annotations

import argparse
import logging
import shlex
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path


DEFAULT_START_TIME = "13:20"
DEFAULT_END_TIME = "17:30"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Scheduler Entrypoint")
    parser.add_argument("--cron-file", default="/etc/cron.d/cc-bot")
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--bot-token", required=True)
    parser.add_argument("--chat-id", required=True)
    parser.add_argument("--host", required=True)
    parser.add_argument("--start-time", default=DEFAULT_START_TIME)
    parser.add_argument("--end-time", default=DEFAULT_END_TIME)
    parser.add_argument("--variation-minutes", type=int, default=2)
    parser.add_argument("--workdays", default="1-5", help="Cron Wochentage")
    parser.add_argument("--python-bin", default="python")
    parser.add_argument("--script", default="-m src.cli")
    parser.add_argument(
        "--log-file",
        default="/var/log/cc-bot.log",
        help="Pfad für Cron-Logausgaben",
    )
    parser.add_argument(
        "--disable-variation",
        action="store_true",
        help="Deaktiviert Zufallsverzögerung innerhalb des CLI",
    )
    return parser


def write_cron_file(
    cron_path: Path,
    python_bin: str,
    script: str,
    cred_args: dict[str, str],
    start_time: str,
    end_time: str,
    variation_minutes: int,
    workdays: str,
    log_file: str,
    enable_variation: bool,
) -> None:
    cron_path.parent.mkdir(parents=True, exist_ok=True)

    cron_lines = [
        "SHELL=/bin/sh",
        "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
    ]

    start_trigger = _calculate_trigger_time(start_time, variation_minutes)
    end_trigger = _calculate_trigger_time(end_time, variation_minutes)

    start_cmd = _build_cron_command(
        python_bin,
        script,
        "start",
        start_time,
        variation_minutes,
        workdays,
        cred_args,
        log_file,
        enable_variation,
        start_trigger,
    )
    stop_cmd = _build_cron_command(
        python_bin,
        script,
        "stop",
        end_time,
        variation_minutes,
        workdays,
        cred_args,
        log_file,
        enable_variation,
        end_trigger,
    )

    cron_lines.extend([start_cmd, stop_cmd, ""])
    cron_path.write_text("\n".join(cron_lines), encoding="utf-8")
    try:
        cron_path.chmod(0o644)
    except PermissionError:
        logging.warning("Konnte Berechtigungen für %s nicht setzen", cron_path)


def _build_cron_command(
    python_bin: str,
    script: str,
    mode: str,
    time_str: str,
    variation: int,
    workdays: str,
    cred_args: dict[str, str],
    log_file: str,
    enable_variation: bool,
    trigger_time: str,
) -> str:
    hour, minute = trigger_time.split(":")
    cron_schedule = f"{minute} {hour} * * {workdays}"
    cli_parts = [python_bin] + script.split()

    cli_parts.extend([
        "--mode",
        mode,
        "--username",
        cred_args["username"],
        "--password",
        cred_args["password"],
        "--bot-token",
        cred_args["bot_token"],
        "--chat-id",
        cred_args["chat_id"],
        "--host",
        cred_args["host"],
        "--start-time",
        cred_args["start_time"],
        "--end-time",
        cred_args["end_time"],
        "--variation-minutes",
        str(variation),
    ])

    if enable_variation:
        cli_parts.append("--apply-variation")

    command = shlex.join(cli_parts)
    return f"{cron_schedule} root {command} >> {shlex.quote(log_file)} 2>&1"


def _calculate_trigger_time(time_str: str, variation: int) -> str:
    base_time = datetime.strptime(time_str, "%H:%M")
    delta = timedelta(minutes=max(0, variation))
    total_minutes = base_time.hour * 60 + base_time.minute
    trigger_total = max(0, total_minutes - int(delta.total_seconds() // 60))
    trigger_hour = trigger_total // 60
    trigger_minute = trigger_total % 60
    return f"{trigger_hour:02d}:{trigger_minute:02d}"


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

    cron_path = Path(args.cron_file)
    cred_args = {
        "username": args.username,
        "password": args.password,
        "bot_token": args.bot_token,
        "chat_id": args.chat_id,
        "host": args.host,
        "start_time": args.start_time,
        "end_time": args.end_time,
    }

    write_cron_file(
        cron_path,
        args.python_bin,
        args.script,
        cred_args,
        args.start_time,
        args.end_time,
        args.variation_minutes,
        args.workdays,
        args.log_file,
        not args.disable_variation,
    )

    logging.info("Starte Cron im Vordergrund")
    subprocess.run(["cron", "-f"], check=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())

