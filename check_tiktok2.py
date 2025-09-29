import os
import json
import hashlib
import requests
from datetime import datetime

# ---------------------------
# Konfiguration
# ---------------------------
USERNAME = "ice22d.ttv"
WEBHOOK = os.environ.get("DISCORD_WEBHOOK")
STATE_FILE = "posted.json"
COLOR = 0x0010e4  # Discord Embed Farbe

# ---------------------------
# Zustand laden / speichern
# ---------------------------
def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"posted": []}

def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False)

def id_for_video(video):
    return hashlib.sha1(video["id"].encode("utf-8")).hexdigest()

# ---------------------------
# TikTok abrufen
# ---------------------------
def fetch_videos():
    url = f"https://www.tiktok.com/@{USERNAME}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
    print("Fehler beim Abrufen von TikTok:", resp.status_code)
    return []
