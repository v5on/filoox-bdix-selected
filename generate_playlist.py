import os, json, random, string, requests
from datetime import datetime, timezone
import pytz

# --- CONFIG ---
BASE_API = os.getenv("XOTT_API_URL")
PHP_PROXY = "https://maxplay-tv.fun/5on/stream.php"
HEADERS = {"User-Agent": "Dalvik/2.1.0 (Linux; Android 10)"}

# SELECTED CATEGORIES ONLY
TARGET_CATEGORY_IDS = {
    "352", "3", "290", "196", "350", "4", "1016", "558", "340", "349",
    "377", "313", "198", "90", "14", "104", "675", "319", "891"
}

# --- 1️⃣ Generate new 32-char token ---
def generate_token():
    token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    timestamp = int(datetime.now().timestamp())
    with open("token.json", "w") as f:
        json.dump({"token": token, "generated_at": timestamp}, f, indent=2)
    return token

# --- 2️⃣ Fetch all categories ---
def fetch_categories():
    url = f"{BASE_API}&action=get_live_categories"
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print("❌ Error fetching categories:", e)
        return []

# --- 3️⃣ Fetch all channels ---
def fetch_channels():
    url = f"{BASE_API}&action=get_live_streams"
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print("❌ Error fetching channels:", e)
        return []

# --- 4️⃣ Generate organized playlist with SELECTED categories ---
def generate_playlist(channels, categories, token):
    # BD Timezone
    bd_tz = pytz.timezone('Asia/Dhaka')
    bd_time = datetime.now(bd_tz).strftime('%Y-%m-%d %H:%M:%S')

    # Create category mapping
    category_map = {str(cat["category_id"]): cat["category_name"] for cat in categories}

    # Group channels by SELECTED categories only
    channels_by_category = {}
    selected_count = 0

    for ch in channels:
        cat_id = str(ch.get("category_id"))
        # ONLY include selected categories
        if cat_id in TARGET_CATEGORY_IDS and cat_id in category_map:
            category_name = category_map[cat_id]
            if category_name not in channels_by_category:
                channels_by_category[category_name] = []
            channels_by_category[category_name].append(ch)
            selected_count += 1

    # Start building playlist
    lines = [
        "#EXTM3U",
        "# 📦 filoox-bdix Auto Playlist (Selected Categories)",
        f"# ⏰ BD Updated time: {bd_time}",
        f"# 🔄 Updated hourly — Total channels: {selected_count}",
        f"# 🎯 Selected categories: {len(TARGET_CATEGORY_IDS)}",
        "# 🔁 Each stream link uses token validation",
        "# 🌐 @ Credit: @sultanarabi161"
    ]

    # Add demo channel first
    lines.extend([
        '#EXTINF:-1 tvg-id="" tvg-name="📺 Welcome" tvg-logo="https://filexo.vercel.app/image/sultanarabi161.jpg" group-title="Intro",📺 Welcome',
        'https://filexo.vercel.app/video/credit_developed_by_sultanarabi161.mp4'
    ])

    # Add channels organized by SELECTED categories
    for category_name, category_channels in sorted(channels_by_category.items()):
        # Add category header
        lines.append(f"# 🟢 {category_name} ({len(category_channels)} channels)")

        for ch in category_channels:
            name = ch.get("name", "Unknown").strip()
            logo = ch.get("stream_icon", "").strip()
            stream_id = ch.get("stream_id")

            if not name or not stream_id:
                continue

            # Use token in URL
            stream_url = f"{PHP_PROXY}?id={stream_id}&token={token}"

            # EXTINF line with proper formatting
            extinf_line = f'#EXTINF:-1 tvg-id="" tvg-name="{name}" tvg-logo="{logo}" group-title="{category_name}",{name}'
            lines.append(extinf_line)
            lines.append(stream_url)

    # Write to file
    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return selected_count

# --- MAIN ---
if __name__ == "__main__":
    print("🔄 Starting playlist generation (Selected Categories)...")

    # Generate token
    new_token = generate_token()
    print("✅ Token generated")

    # Fetch data
    categories = fetch_categories()
    channels = fetch_channels()

    print(f"📊 Fetched {len(categories)} categories and {len(channels)} channels")

    # Generate playlist
    total_channels = generate_playlist(channels, categories, new_token)

    print(f"✅ Playlist generated with {total_channels} channels from selected categories")
    print("🎯 Token & playlist updated successfully")
