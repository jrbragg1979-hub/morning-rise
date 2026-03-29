"""iCloud Calendar integration using CalDAV."""

import os
import datetime

import caldav


def get_todays_events():
    """Fetch today's events from iCloud Calendar."""
    username = os.getenv("ICLOUD_EMAIL")
    password = os.getenv("ICLOUD_APP_PASSWORD")

    if not username or not password:
        return []

    try:
        client = caldav.DAVClient(
            url="https://caldav.icloud.com",
            username=username,
            password=password,
        )

        principal = client.principal()
        calendars = principal.calendars()

        now = datetime.datetime.now()
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=0)

        parsed = []
        for cal in calendars:
            try:
                events = cal.search(
                    start=start_of_day,
                    end=end_of_day,
                    event=True,
                    expand=True,
                )
            except Exception:
                continue

            for event in events:
                vevent = event.vobject_instance.vevent
                summary = str(vevent.summary.value) if hasattr(vevent, "summary") else "Untitled event"
                dtstart = vevent.dtstart.value

                if isinstance(dtstart, datetime.datetime):
                    time_str = dtstart.strftime("%-I:%M %p")
                    parsed.append({"time": time_str, "summary": summary})
                else:
                    # All-day event (date, not datetime)
                    parsed.append({"time": "all day", "summary": summary})

        # Sort by time (all-day events first, then by time)
        parsed.sort(key=lambda e: (e["time"] != "all day", e["time"]))
        return parsed

    except Exception as e:
        print(f"Calendar fetch error: {e}")
        return []


def format_calendar(events):
    """Turn event list into spoken text."""
    if not events:
        return "You have a free day today — no events on the calendar."

    if len(events) == 1:
        e = events[0]
        if e["time"] == "all day":
            return f"You have one thing on your calendar today: {e['summary']}, all day."
        return f"You have one thing on your calendar today: {e['summary']} at {e['time']}."

    lines = [f"You have {len(events)} things on your calendar today."]
    for e in events:
        if e["time"] == "all day":
            lines.append(f"{e['summary']}, all day.")
        else:
            lines.append(f"{e['summary']} at {e['time']}.")

    return " ".join(lines)
