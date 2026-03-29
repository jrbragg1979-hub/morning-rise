# iOS Shortcut Setup — Morning Rise

## Prerequisites
- Morning Rise server running and accessible from your phone (local network or deployed)
- Server URL (e.g., `http://192.168.1.100:3003` or your deployed URL)
- YouTube Music app installed

## Create the Shortcut

1. Open **Shortcuts** app on iPhone
2. Tap **+** to create a new shortcut
3. Name it **"Morning Rise"**

### Add these actions in order:

**Action 1 — Get the audio**
- Search for: **"Get Contents of URL"**
- URL: `http://YOUR_SERVER/today.mp3`
- Method: GET

**Action 2 — Play the briefing**
- Search for: **"Play Sound"**
- Or use **"Encode Media"** → **"Play Media"** if Play Sound doesn't work with the URL content
- Alternative: Use **"Base64 Encode"** the content, save to file, then play

**Simpler approach for Action 1+2:**
- Use **"Get Contents of URL"** → set URL to your server's `/today.mp3`
- Add **"Save File"** → save to a known location (e.g., Shortcuts folder)
- Add **"Play Sound"** → select the saved file

**Action 3 — Wait for audio to finish**
- Search for: **"Wait"**
- Set to **90 seconds** (adjust based on your typical briefing length)

**Action 4 — Open YouTube Music playlist**
- Search for: **"Open URLs"**
- URL: `https://music.youtube.com/playlist?list=YOUR_PLAYLIST_ID`
- This will open the YouTube Music app directly to your playlist

### Final Shortcut Flow:
```
1. Get Contents of URL [your-server/today.mp3]
2. Save to [Shortcuts/morning-rise.mp3]
3. Play Sound [morning-rise.mp3]
4. Wait [90 seconds]
5. Open URL [youtube music playlist]
```

## Set Up the Automation

1. Go to **Shortcuts** → **Automation** tab
2. Tap **+** → **"Time of Day"**
3. Set time to **7:00 AM**
4. Set to repeat: **Daily** (or choose specific days)
5. Under "Do": select **"Run Shortcut"** → choose **"Morning Rise"**
6. **Important:** iOS will show a notification asking you to tap "Run" — this is an iOS limitation for time-based automations

## Testing

Before setting up the automation, test the shortcut manually:
1. Make sure your server is running
2. Open the Morning Rise shortcut
3. Tap the play button
4. You should hear the briefing, then YouTube Music opens

## Finding Your YouTube Music Playlist URL

1. Open YouTube Music app or music.youtube.com
2. Go to your playlist
3. Tap Share → Copy Link
4. The URL will look like: `https://music.youtube.com/playlist?list=PLxxxxx`

## Troubleshooting

- **No audio plays:** Check that the server URL is reachable from your phone (try opening it in Safari first)
- **Shortcut times out:** Your server might be slow to generate — visit `/generate` in a browser first to pre-cache
- **YouTube Music doesn't open:** Make sure the app is installed; the URL scheme should auto-redirect
