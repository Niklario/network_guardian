import time
from datetime import datetime


class Collector:

    def __init__(self, adguard, database):
        self.adguard = adguard
        self.db = database

    @staticmethod
    def epoch(timestamp):
        return datetime.fromisoformat(
            timestamp.replace("Z", "+00:00")
        ).timestamp()

    def collect(self):
        started = time.time()

        last_poll = float(self.db.get_meta(
            "last_successful_poll",
            started - 3600
        ))

        cutoff = last_poll - 60
        cursor = None
        seen_cursors = set()
        inserted = 0
        pages = 0

        while True:
            result = self.adguard.querylog(
                limit=500,
                older_than=cursor
            )

            entries = result.get("data", [])

            if not entries:
                break

            pages += 1

            relevant = [
                entry for entry in entries
                if self.epoch(entry["time"]) >= cutoff
            ]

            inserted += self.db.save_queries(relevant)

            oldest = min(
                self.epoch(entry["time"])
                for entry in entries
            )

            if oldest < cutoff:
                break

            next_cursor = (
                result.get("oldest")
                or entries[-1]["time"]
            )

            if next_cursor in seen_cursors:
                raise RuntimeError(
                    "AdGuard pagination cursor repeated"
                )

            seen_cursors.add(next_cursor)
            cursor = next_cursor

            if pages >= 1000:
                raise RuntimeError(
                    "Pagination safety limit reached"
                )

        self.db.set_meta(
            "last_successful_poll", started
        )

        return inserted, pages
