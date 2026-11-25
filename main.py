import json
import time
import traceback
from datetime import datetime

from adguard import AdGuard
from database import Database
from collector import Collector
from devices import Devices
from analyzer import Analyzer
from notifier import Notifier
from dashboard import start_dashboard


with open("/data/options.json") as file:
    config = json.load(file)

POLL_INTERVAL = config.get("poll_interval", 10)
RETENTION_DAYS = config.get("retention_days", 30)
LEARNING_DAYS = config.get("learning_days", 7)

adguard = AdGuard(config.get(
    "adguard_url",
    "http://127.0.0.1:45158"
))

database = Database()
collector = Collector(adguard, database)
devices = Devices(database)
analyzer = Analyzer(database, LEARNING_DAYS)
notifier = Notifier(database)

print("=" * 50)
print("Network Guardian v0.2.0")
print("Local Network Security Monitor")
print("=" * 50)
print(f"[CONFIG] Poll interval: {POLL_INTERVAL}s")
print(f"[CONFIG] Retention: {RETENTION_DAYS} days")
print(f"[CONFIG] Learning: {LEARNING_DAYS} days")
print("[CONFIG] AI: Disabled")
print("[CONFIG] Automatic blocking: Disabled")
print("[DATABASE] SQLite initialized")
start_dashboard()

last_summary = 0
last_cleanup = 0
last_analysis_hour = -1
connected = False

while True:
    try:
        if not connected:
            status = adguard.status()

            print(
                "[ADGUARD] Connected:",
                status.get("version")
            )

            connected = True

        inserted, pages = collector.collect()
        total = database.total_queries()

        print(
            f"[{datetime.now().isoformat(timespec='seconds')}] "
            f"New queries: {inserted} | "
            f"Database: {total} | "
            f"Pages: {pages}"
        )

        now = time.time()

        if now - last_summary >= 300:
            devices.print_summary()
            last_summary = now

        current_hour = int(now // 3600)

        if current_hour != last_analysis_hour:
            for event in analyzer.analyze():
                notifier.alert(*event)

            last_analysis_hour = current_hour

        if now - last_cleanup >= 3600:
            database.cleanup(RETENTION_DAYS)
            last_cleanup = now

            print("[DATABASE] Retention cleanup completed")

    except Exception as error:
        connected = False
        print(f"[ERROR] {error}")
        traceback.print_exc()

    time.sleep(POLL_INTERVAL)
