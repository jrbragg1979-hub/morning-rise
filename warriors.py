"""Golden State Warriors schedule lookup using ESPN's public API (no key required)."""

import os
import datetime
import requests

from localtime import local_tz, local_now


SCHEDULE_URL = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams/{team}/schedule"
DEFAULT_TEAM = "gs"

# Rotated daily so the announcement does not read the same way every game.
INTROS = [
    "And some Warriors news — ",
    "And on the Warriors front — ",
    "And a bit of basketball — ",
    "Also worth knowing — ",
    "",  # no intro; go straight into the matchup
]

# ESPN returns the whole season in one ~1 MB payload, so cache it per day.
_cache = {}


def _parse_utc(stamp):
    """ESPN stamps look like 2026-11-26T03:00Z (sometimes with seconds)."""
    if not stamp:
        return None
    try:
        return datetime.datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    except ValueError:
        return None


def get_todays_game(now=None):
    """Return today's Warriors game as a dict, or None if they aren't playing."""
    team = os.getenv("NBA_TEAM_SLUG", DEFAULT_TEAM)
    tz = local_tz()
    now = now or local_now()
    today = now.astimezone(tz).date()

    cache_key = (team, today)
    if cache_key in _cache:
        return _cache[cache_key]

    try:
        resp = requests.get(
            SCHEDULE_URL.format(team=team),
            headers={"User-Agent": "morning-rise/1.0"},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()

        our_team = data.get("team", {}) or {}
        our_id = our_team.get("id")
        record = our_team.get("recordSummary")

        game = None
        for event in data.get("events", []):
            tipoff_utc = _parse_utc(event.get("date"))
            if not tipoff_utc:
                continue

            tipoff = tipoff_utc.astimezone(tz)
            if tipoff.date() != today:
                continue

            competition = (event.get("competitions") or [{}])[0]

            opponent = None
            home_away = None
            for competitor in competition.get("competitors", []):
                side = (competitor.get("team") or {})
                if side.get("id") == our_id:
                    home_away = competitor.get("homeAway")
                else:
                    opponent = side.get("shortDisplayName") or side.get("displayName")

            # National TV is the only broadcast worth naming out loud.
            network = None
            for broadcast in competition.get("broadcasts", []):
                if (broadcast.get("market") or {}).get("type") == "National":
                    network = (broadcast.get("media") or {}).get("shortName")
                    break

            game = {
                "opponent": opponent,
                "home_away": home_away,
                "tipoff": tipoff,
                "time_known": bool(event.get("timeValid", True)),
                "network": network,
                "venue": ((competition.get("venue") or {}).get("address") or {}).get("city"),
                "record": record,
            }
            break

        _cache.clear()  # only today's lookup is ever useful
        _cache[cache_key] = game
        return game

    except Exception as e:
        print(f"Warriors schedule fetch error: {e}")
        return None


def format_game(game):
    """Turn the game dict into a spoken sentence."""
    if not game or not game.get("opponent"):
        return ""

    tipoff = game["tipoff"]
    if not game.get("time_known"):
        when = "today"
    elif tipoff.hour < 12:
        when = "this morning"
    elif tipoff.hour < 17:
        when = "this afternoon"
    else:
        when = "tonight"

    opponent = game["opponent"]
    if game.get("home_away") == "home":
        matchup = f"the Warriors host the {opponent} {when}"
    else:
        matchup = f"the Warriors play the {opponent} in {game['venue']} {when}" if game.get("venue") \
            else f"the Warriors are on the road against the {opponent} {when}"

    intro = INTROS[tipoff.date().toordinal() % len(INTROS)]
    text = intro + matchup

    if game.get("time_known"):
        text += f", tipping off at {tipoff.strftime('%-I:%M %p')}"
    else:
        text += ", tip-off time still to be announced"

    if game.get("network"):
        text += f", on {game['network']}"

    text += "."

    # With no intro the sentence leads, so it has to start capitalised.
    if not intro:
        text = text[0].upper() + text[1:]

    record = game.get("record")
    if record and "-" in record:
        wins, losses = record.split("-", 1)
        text += f" They're {wins} and {losses} on the season."

    return text
