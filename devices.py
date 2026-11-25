import time


class Devices:

    def __init__(self, database):
        self.db = database

    def profiles(self):
        rows = self.db.conn.execute("""
            SELECT
                client,
                COUNT(*) AS total_queries,
                COUNT(DISTINCT domain) AS unique_domains,
                SUM(blocked) AS blocked_queries,
                MIN(epoch) AS first_seen,
                MAX(epoch) AS last_seen
            FROM dns_queries
            GROUP BY client
            ORDER BY total_queries DESC
        """).fetchall()

        return [dict(row) for row in rows]

    def active_devices(self, minutes=60):
        rows = self.db.conn.execute("""
            SELECT DISTINCT client
            FROM dns_queries
            WHERE epoch >= ?
        """, (
            time.time() - minutes * 60,
        )).fetchall()

        return [row["client"] for row in rows]

    def print_summary(self):
        profiles = self.profiles()

        print("[DEVICES] Known IP addresses:",
              len(profiles))

        for device in profiles:
            print(
                f"  {device['client']} | "
                f"Queries: {device['total_queries']} | "
                f"Domains: {device['unique_domains']} | "
                f"Blocked: {device['blocked_queries']}"
            )
