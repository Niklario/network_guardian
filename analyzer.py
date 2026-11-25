import time
import statistics


class Analyzer:

    def __init__(self, database, learning_days=7):
        self.db = database
        self.learning_days = learning_days

    def analyze(self):
        now = time.time()
        hour = int(now // 3600) * 3600
        start = hour - 3600

        events = []

        devices = self.db.conn.execute("""
            SELECT DISTINCT client
            FROM dns_queries
            WHERE epoch >= ? AND epoch < ?
        """, (start, hour)).fetchall()

        for device in devices:
            client = device["client"]

            first_seen = self.db.conn.execute("""
                SELECT MIN(epoch)
                FROM dns_queries
                WHERE client = ?
            """, (client,)).fetchone()[0]

            age = (now - first_seen) / 86400

            if age < self.learning_days:
                continue

            current = self.db.conn.execute("""
                SELECT
                    COUNT(*) AS total,
                    SUM(blocked) AS blocked,
                    SUM(
                        CASE WHEN status = 'NXDOMAIN'
                        THEN 1 ELSE 0 END
                    ) AS nxdomain
                FROM dns_queries
                WHERE client = ?
                  AND epoch >= ?
                  AND epoch < ?
            """, (
                client, start, hour
            )).fetchone()

            total = current["total"]

            if total == 0:
                continue

            history = self.db.conn.execute("""
                SELECT COUNT(*) AS count
                FROM dns_queries
                WHERE client = ?
                  AND epoch >= ?
                  AND epoch < ?
                GROUP BY CAST(epoch / 3600 AS INTEGER)
            """, (
                client,
                start - self.learning_days * 86400,
                start
            )).fetchall()

            counts = [row["count"] for row in history]

            if len(counts) >= 24:
                average = statistics.mean(counts)
                deviation = statistics.pstdev(counts)

                threshold = max(
                    100,
                    average * 3,
                    average + 4 * deviation
                )

                if total > threshold:
                    events.append((
                        client,
                        "DNS_TRAFFIC_SPIKE",
                        "medium",
                        f"{total} queries/hour; "
                        f"baseline {average:.1f}/hour"
                    ))

            new_domains = self.db.conn.execute("""
                SELECT COUNT(DISTINCT q.domain)
                FROM dns_queries q
                WHERE q.client = ?
                  AND q.epoch >= ?
                  AND q.epoch < ?
                  AND NOT EXISTS (
                      SELECT 1 FROM dns_queries h
                      WHERE h.client = q.client
                        AND h.domain = q.domain
                        AND h.epoch < ?
                  )
            """, (
                client, start, hour, start
            )).fetchone()[0]

            if new_domains >= 30:
                events.append((
                    client,
                    "NEW_DOMAIN_BURST",
                    "medium",
                    f"{new_domains} new domains "
                    "during one hour"
                ))

            blocked = current["blocked"] or 0

            if total >= 100 and blocked / total >= 0.8:
                events.append((
                    client,
                    "HIGH_BLOCK_RATE",
                    "low",
                    f"{blocked}/{total} queries blocked"
                ))

            nxdomain = current["nxdomain"] or 0

            if nxdomain >= 30 and nxdomain / total >= 0.3:
                events.append((
                    client,
                    "NXDOMAIN_BURST",
                    "medium",
                    f"{nxdomain} NXDOMAIN responses"
                ))

        return events
