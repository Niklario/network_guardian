
class Notifier:

    def __init__(self, database):
        self.db = database

    def alert(self, client, event_type,
              severity, message):

        saved = self.db.save_event(
            client,
            event_type,
            severity,
            message
        )

        if not saved:
            return

        print("=" * 50)
        print("[SECURITY EVENT]")
        print(f"Severity: {severity.upper()}")
        print(f"Device:   {client}")
        print(f"Type:     {event_type}")
        print(f"Details:  {message}")
        print("=" * 50)
