import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")
print(f"🔑 Using API Key: {API_KEY[:10]}...")

# Test with a simple request
url = "https://www.googleapis.com/youtube/v3/search"
params = {
    "part": "snippet",
    "q": "test",
    "maxResults": 1,
    "type": "video",
    "key": API_KEY
}

print("🧪 Testing API key...")
response = requests.get(url, params=params)

print(f"📊 Status Code: {response.status_code}")
print(f"📝 Response: {response.text[:200]}...")

if response.status_code == 200:
    print("✅ API key is working!")
else:
    print("❌ API key issue. Please check:")
    print("   1. YouTube Data API v3 is enabled")
    print("   2. API key has correct permissions")
    print("   3. API key is not restricted")
