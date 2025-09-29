# check_tiktok.py
import os
import json
import hashlib
import feedparser
import requests
from datetime import datetime

# Konfiguration
RSS_URL = "https://rsshub.app/tiktok/user/ice22d.ttv"
WEBHOOK = os.environ.get("DISCORD_WEBHOOK")
STATE_FILE = "posted.json"

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"posted": []}

def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False)

def id_for_entry(entry):
    key = (entry.get("link","") + entry.get("published","")).encode("utf-8")
    return hashlib.sha1(key).hexdigest()

def make_embed(entry):
    title = entry.get("title", "Neues TikTok")
    link = entry.get("link")
    desc = entry.get("summary", "")[:2048]
    author = entry.get("author", "")
    thumb = None
    if 'media_thumbnail' in entry:
        thumb = entry.media_thumbnail[0]['url']
    elif 'media_content' in entry:
        thumb = entry.media_content[0].get('url')
    try:
        ts = datetime(*entry.published_parsed[:6]).isoformat() + "Z"
    except Exception:
        ts = datetime.utcnow().isoformat() + "Z"

    embed = {
        "title": title,
        "url": link,
        "description": desc,
        "color": 1044,  # Farbe #0010e4 in Decimal ist 1044
        "author": {"name": author, "url": f"https://www.tiktok.com/@{author.lstrip('@')}" if author else None},
        "footer": {"text": "Neues TikTok Video!"},
        "timestamp": ts
    }
    if thumb:
        embed["thumbnail"] = {"url": thumb}
    return embed

def post_to_discord(embed):
    if not WEBHOOK:
        print("ERROR: DISCORD_WEBHOOK nicht gesetzt")
        return False
    payload = {
        "username": "TikTok Bot",
        "avatar_url": "https://upload.wikimedia.org/wikipedia/en/6/69/TikTok_logo.png",
        "embeds": [embed]
    }
    resp = requests.post(WEBHOOK, json=payload, timeout=15)
    print("Discord response:", resp.status_code)
    return resp.status_code == 204 or resp.status_code == 200

def main():
    state = load_state()
    feed = feedparser.parse(RSS_URL)
    new_posted = False

    for entry in feed.entries:
        eid = id_for_entry(entry)
        if eid in state["posted"]:
            continue
        embed = make_embed(entry)
        ok = post_to_discord(embed)
        if ok:
            state["posted"].append(eid)
            new_posted = True
        else:
            print("Fehler beim Posten")

    if new_posted:
        save_state(state)
    else:
        print("Keine neuen TikToks.")

if __name__ == "__main__":
    main()

