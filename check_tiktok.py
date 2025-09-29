import os
import json
import hashlib
import requests
from datetime import datetime
import re

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
# TikTok abrufen (stabiler)
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

        html = resp.text
        # JSON-Daten im HTML suchen (itemInfos)
        match = re.search(r'\"itemInfos\":({.*?})\,\"authorInfos\"', html)
        if not match:
            print("Konnte TikTok-Daten nicht finden")
            return []

        item_json = json.loads(match.group(1))
        videos = []
        for vid_id, vid in item_json.items():
            videos.append({
                "id": vid.get("id"),
                "desc": vid.get("text"),
                "url": f"https://www.tiktok.com/@{USERNAME}/video/{vid.get('id')}",
                "thumb": vid.get("cover"),
                "author": USERNAME
            })
        return videos

    except Exception as e:
        print("Fehler beim Abrufen von TikTok:", e)
        return []

# ---------------------------
# Discord Embed erstellen
# ---------------------------
def post_to_discord(video):
    if not WEBHOOK:
        print("ERROR: DISCORD_WEBHOOK nicht gesetzt")
        return False

    embed = {
        "title": video["desc"][:256] or "Neues TikTok",
        "url": video["url"],
        "color": COLOR,
        "author": {"name": video["author"], "url": f"https://www.tiktok.com/@{USERNAME}"},
        "thumbnail": {"url": video["thumb"]} if video["thumb"] else None,
        "footer": {"text": "Neues TikTok Video!"},
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

    payload = {
        "username": "TikTok Bot",
        "avatar_url": "https://upload.wikimedia.org/wikipedia/en/6/69/TikTok_logo.png",
        "embeds": [embed]
    }

    try:
        resp = requests.post(WEBHOOK, json=payload, timeout=15)
        print("Discord response:", resp.status_code)
        return resp.status_code in (200, 204)
    except Exception as e:
        print("Fehler beim Senden an Discord:", e)
        return False

# ---------------------------
# Hauptfunktion
# ---------------------------
def main():
    state = load_state()
    videos = fetch_videos()
    new_posted = False

    for video in videos:
        eid = id_for_video(video)
        if eid in state["posted"]:
            continue
        ok = post_to_discord(video)
        if ok:
            state["posted"].append(eid)
            new_posted = True

    if new_posted:
        save_state(state)
    else:
        print("Keine neuen TikToks.")

if __name__ == "__main__":
    main()


# ---------------------------
# Disc
