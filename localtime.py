"""Single source of truth for "now".

The server does not necessarily run in the listener's timezone — Railway runs in
UTC — so every date and clock decision in the briefing goes through here.
Set LOCAL_TIMEZONE to an IANA name (e.g. America/Los_Angeles).
"""

import os
import datetime
from zoneinfo import ZoneInfo


DEFAULT_TIMEZONE = "America/Los_Angeles"


def local_tz_name():
    """Validated IANA timezone name — safe to hand to libraries that want a string."""
    name = os.getenv("LOCAL_TIMEZONE", DEFAULT_TIMEZONE)
    try:
        ZoneInfo(name)
        return name
    except Exception:
        print(f"Unknown LOCAL_TIMEZONE {name!r}; falling back to {DEFAULT_TIMEZONE}")
        return DEFAULT_TIMEZONE


def local_tz():
    """tzinfo for the listener's timezone."""
    try:
        return ZoneInfo(local_tz_name())
    except Exception:
        # No tz database available — use whatever the system is set to.
        return datetime.datetime.now().astimezone().tzinfo


def local_now():
    """Timezone-aware current time where the listener is."""
    return datetime.datetime.now(local_tz())


def local_today():
    """The listener's current calendar date."""
    return local_now().date()
