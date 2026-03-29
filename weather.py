"""Weather integration using OpenWeatherMap free tier."""

import os
import requests


def get_weather():
    """Fetch current weather and today's forecast."""
    api_key = os.getenv("WEATHER_API_KEY")
    lat = os.getenv("WEATHER_LAT", "32.7767")
    lon = os.getenv("WEATHER_LON", "-96.7970")

    if not api_key:
        return None

    try:
        url = "https://api.openweathermap.org/data/2.5/forecast"
        resp = requests.get(url, params={
            "lat": lat,
            "lon": lon,
            "appid": api_key,
            "units": "imperial",
            "cnt": 8,  # next 24 hours in 3-hour blocks
        }, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        city = data.get("city", {}).get("name", "your area")
        forecasts = data.get("list", [])

        if not forecasts:
            return None

        current = forecasts[0]
        temp_now = round(current["main"]["temp"])
        desc_now = current["weather"][0]["description"]

        temps = [f["main"]["temp"] for f in forecasts]
        high = round(max(temps))
        low = round(min(temps))

        # Check for rain/snow
        precip = None
        for f in forecasts:
            for w in f.get("weather", []):
                if w["main"] in ("Rain", "Snow", "Thunderstorm"):
                    precip = w["description"]
                    break
            if precip:
                break

        return {
            "city": city,
            "temp_now": temp_now,
            "description": desc_now,
            "high": high,
            "low": low,
            "precipitation": precip,
        }
    except Exception as e:
        print(f"Weather fetch error: {e}")
        return None


def format_weather(weather):
    """Turn weather dict into a spoken sentence."""
    if not weather:
        return ""

    text = (
        f"The weather in {weather['city']} right now is {weather['temp_now']} degrees "
        f"and {weather['description']}. "
        f"Today's high is {weather['high']} and the low is {weather['low']}."
    )

    if weather["precipitation"]:
        text += f" Heads up — {weather['precipitation']} is expected later today."

    return text
