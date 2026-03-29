"""Composes the morning briefing script and generates audio via OpenAI TTS."""

import os
import datetime
from pathlib import Path

from openai import OpenAI

from quotes import get_daily_quote
from weather import get_weather, format_weather
from calendar_integration import get_todays_events, format_calendar


AUDIO_DIR = Path("audio")
AUDIO_DIR.mkdir(exist_ok=True)


def compose_briefing(recipient_name=None):
    """Build the full spoken briefing text."""
    name = recipient_name or os.getenv("RECIPIENT_NAME", "there")
    now = datetime.datetime.now()
    day_of_week = now.strftime("%A")
    date_str = now.strftime("%B %-d")

    # Greeting
    hour = now.hour
    if hour < 12:
        time_of_day = "morning"
    elif hour < 17:
        time_of_day = "afternoon"
    else:
        time_of_day = "evening"

    greeting = f"Good {time_of_day}, {name}. It's {day_of_week}, {date_str}."

    # Inspirational quote
    quote = get_daily_quote()
    quote_section = (
        f"Here's something to carry with you today. "
        f"{quote['text']} "
        f"That was {quote['source']}."
    )

    # Weather
    weather = get_weather()
    weather_section = format_weather(weather)

    # Calendar
    events = get_todays_events()
    calendar_section = format_calendar(events)

    # Closing
    closing = f"Have a wonderful {day_of_week}, {name}. You've got this."

    # Assemble — leading pause prevents iOS audio cutoff
    sections = ["...", greeting, quote_section]
    if weather_section:
        sections.append(weather_section)
    sections.append(calendar_section)
    sections.append(closing)

    return "\n\n".join(sections)


def generate_audio(text, voice="nova"):
    """Generate MP3 from text using OpenAI TTS.

    Voice options: alloy, echo, fable, onyx, nova, shimmer
    'nova' is warm and friendly — good default for a morning greeting.
    """
    client = OpenAI()

    today_str = datetime.date.today().isoformat()
    output_path = AUDIO_DIR / f"briefing_{today_str}.mp3"

    # Skip regeneration if today's audio already exists
    if output_path.exists():
        return output_path

    response = client.audio.speech.create(
        model="tts-1-hd",
        voice=voice,
        input=text,
        response_format="mp3",
        speed=0.95,  # slightly slower for clarity
    )

    response.stream_to_file(str(output_path))
    return output_path


def create_todays_briefing(recipient_name=None, voice="nova"):
    """Full pipeline: compose text -> generate audio -> return path."""
    text = compose_briefing(recipient_name)
    print(f"--- Briefing Script ---\n{text}\n---")
    audio_path = generate_audio(text, voice)
    print(f"Audio saved to: {audio_path}")
    return text, audio_path
