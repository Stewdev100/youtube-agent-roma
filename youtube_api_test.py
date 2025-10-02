import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")

if not API_KEY:
    print("❌ No API key found. Check your .env file!")
    print("📝 Please add your YouTube API key to the .env file:")
    print("   YOUTUBE_API_KEY=your_api_key_here")
    exit()

# Example: search for videos about Ethereum
url = "https://www.googleapis.com/youtube/v3/search"
params = {
    "part": "snippet",
    "q": "Ethereum",
    "maxResults": 3,
    "type": "video",
    "key": API_KEY
}

print("🔍 Searching for Ethereum videos...")
response = requests.get(url, params=params)

if response.status_code == 200:
    data = response.json()
    print(f"✅ Found {len(data.get('items', []))} videos:")
    for item in data.get("items", []):
        title = item["snippet"]["title"]
        channel = item["snippet"]["channelTitle"]
        video_id = item["id"]["videoId"]
        print(f"🎥 {title} — {channel}")
        print(f"   🔗 https://www.youtube.com/watch?v={video_id}")
        print()
else:
    print("❌ Error:", response.status_code, response.text)
