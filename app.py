"""
Morning Rise — AI Morning Briefing Server

Serves today's personalized audio briefing as an MP3.
Designed to be called by an iOS Shortcut at alarm time.
"""

import os
import datetime
from pathlib import Path

from flask import Flask, send_file, jsonify, Response
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler

load_dotenv()

from briefing import create_todays_briefing, AUDIO_DIR

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret")


def pre_generate_briefing():
    """Called by scheduler to generate audio before alarm time."""
    print(f"[{datetime.datetime.now()}] Pre-generating today's briefing...")
    try:
        create_todays_briefing()
        print("Briefing generated successfully.")
    except Exception as e:
        print(f"Error generating briefing: {e}")


@app.route("/")
def index():
    return jsonify({
        "service": "Morning Rise",
        "status": "running",
        "endpoints": {
            "/today.mp3": "Today's morning briefing audio",
            "/today/text": "Today's briefing as text (for debugging)",
            "/generate": "Force regenerate today's briefing",
        }
    })


@app.route("/today.mp3")
def today_audio():
    """Serve today's briefing as MP3. Generate on-demand if not cached."""
    today_str = datetime.date.today().isoformat()
    audio_path = AUDIO_DIR / f"briefing_{today_str}.mp3"

    if not audio_path.exists():
        create_todays_briefing()

    if audio_path.exists():
        return send_file(
            audio_path,
            mimetype="audio/mpeg",
            as_attachment=False,
            download_name=f"morning-rise-{today_str}.mp3",
        )

    return Response("Briefing not available", status=503)


@app.route("/today/text")
def today_text():
    """Return today's briefing as text for debugging."""
    from briefing import compose_briefing
    text = compose_briefing()
    return Response(text, mimetype="text/plain")


@app.route("/today/duration")
def today_duration():
    """Return the duration of today's MP3 in seconds."""
    today_str = datetime.date.today().isoformat()
    audio_path = AUDIO_DIR / f"briefing_{today_str}.mp3"

    if not audio_path.exists():
        create_todays_briefing()

    if audio_path.exists():
        try:
            from mutagen.mp3 import MP3
            audio = MP3(str(audio_path))
            duration = round(audio.info.length)
            return jsonify({"duration_seconds": duration})
        except Exception:
            size = audio_path.stat().st_size
            estimated = round(size / 16000)
            return jsonify({"duration_seconds": estimated, "estimated": True})

    return jsonify({"duration_seconds": 60})


@app.route("/generate")
def force_generate():
    """Force regenerate today's briefing (deletes cached version)."""
    today_str = datetime.date.today().isoformat()
    audio_path = AUDIO_DIR / f"briefing_{today_str}.mp3"

    if audio_path.exists():
        audio_path.unlink()

    text, path = create_todays_briefing()
    return jsonify({
        "status": "generated",
        "text": text,
        "audio": str(path),
    })


def start_scheduler():
    """Start the daily briefing scheduler."""
    try:
        alarm_time = os.getenv("ALARM_TIME", "06:50")
        hour, minute = map(int, alarm_time.split(":"))
        scheduler = BackgroundScheduler()
        scheduler.add_job(
            pre_generate_briefing,
            "cron",
            hour=hour,
            minute=minute,
            id="daily_briefing",
        )
        scheduler.start()
        print(f"Daily briefing scheduled for {alarm_time}")
    except Exception as e:
        print(f"Scheduler error: {e}")


start_scheduler()


if __name__ == "__main__":
    port = int(os.getenv("PORT", 3003))
    print(f"Morning Rise server starting on port {port}")
    app.run(host="0.0.0.0", port=port, debug=True)
