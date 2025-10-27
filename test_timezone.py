#!/usr/bin/env python3
"""Test der Zeitzonen-Funktionalität"""

from src.bot import calculate_scheduled_time
import datetime

# Test UTC
result_utc = calculate_scheduled_time(datetime.time(17, 30), timezone="UTC")
print("Geplante Zeit UTC:", result_utc)

# Test CET
result_cet = calculate_scheduled_time(datetime.time(17, 30), timezone="Europe/Berlin")
print("Geplante Zeit CET:", result_cet)

# Test aktuelle Zeit
now_utc = datetime.datetime.now(datetime.timezone.utc)
now_cet = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=1)))
print("Aktuelle Zeit UTC:", now_utc)
print("Aktuelle Zeit CET:", now_cet)
