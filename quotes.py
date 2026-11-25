"""
Inspirational quotes — fetches from API Ninjas with curated fallback.
"""

import os
import random
import requests

from localtime import local_today


# Fallback quotes if API is unavailable
FALLBACK_QUOTES = [
    {"text": "Tell me, what is it you plan to do with your one wild and precious life?", "source": "Mary Oliver"},
    {"text": "You must be the change you wish to see in the world.", "source": "Mahatma Gandhi"},
    {"text": "It is never too late to be what you might have been.", "source": "George Eliot"},
    {"text": "Nothing can dim the light that shines from within.", "source": "Maya Angelou"},
    {"text": "The best time to plant a tree was twenty years ago. The second best time is now.", "source": "Chinese Proverb"},
    {"text": "In the middle of difficulty lies opportunity.", "source": "Albert Einstein"},
    {"text": "Life shrinks or expands in proportion to one's courage.", "source": "Anaïs Nin"},
    {"text": "Keep your face always toward the sunshine, and shadows will fall behind you.", "source": "Walt Whitman"},
    {"text": "The secret of getting ahead is getting started.", "source": "Mark Twain"},
    {"text": "You are never too old to set another goal or to dream a new dream.", "source": "C.S. Lewis"},
]


def fetch_api_quote():
    """Fetch an inspirational quote from ZenQuotes (free, no key needed)."""
    try:
        resp = requests.get(
            "https://zenquotes.io/api/today",
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()

        if data and len(data) > 0 and data[0].get("q"):
            return {
                "text": data[0]["q"],
                "source": data[0]["a"],
            }
    except Exception as e:
        print(f"Quote API error: {e}")

    return None


def get_daily_quote():
    """Fetch a fresh inspirational quote. Falls back to curated list if API fails."""
    quote = fetch_api_quote()
    if quote:
        return quote

    # Fallback: deterministic daily rotation
    idx = local_today().toordinal() % len(FALLBACK_QUOTES)
    return FALLBACK_QUOTES[idx]
