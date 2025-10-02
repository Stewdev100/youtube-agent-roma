#!/usr/bin/env python3
"""
YouTube RSS Scraper - Get real YouTube videos using RSS feeds
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import List, Dict, Any
import re

class YouTubeRSSScraper:
    """Scrape YouTube videos using RSS feeds"""
    
    def __init__(self):
        self.base_url = "https://www.youtube.com/feeds/videos.xml"
    
    def get_channel_videos(self, channel_id: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Get videos from a specific YouTube channel using RSS"""
        try:
            url = f"{self.base_url}?channel_id={channel_id}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                videos = []
                
                # Parse RSS feed
                for entry in root.findall('.//{http://www.w3.org/2005/Atom}entry')[:max_results]:
                    try:
                        title = entry.find('.//{http://www.w3.org/2005/Atom}title').text
                        video_id = entry.find('.//{http://www.youtube.com/xml/schemas/2015}videoId').text
                        published = entry.find('.//{http://www.w3.org/2005/Atom}published').text
                        author = entry.find('.//{http://www.w3.org/2005/Atom}author/{http://www.w3.org/2005/Atom}name').text
                        
                        # Get description from media:description if available
                        description_elem = entry.find('.//{http://search.yahoo.com/mrss/}description')
                        description = description_elem.text if description_elem is not None else f"AI cryptocurrency content: {title}"
                        
                        video = {
                            "title": title,
                            "channel": author,
                            "video_id": video_id,
                            "video_url": f"https://www.youtube.com/watch?v={video_id}",
                            "description": description[:200] + "..." if len(description) > 200 else description,
                            "published_at": published,
                            "thumbnail": f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg",
                            "tier": self._classify_channel_tier(author)
                        }
                        
                        videos.append(video)
                        
                    except Exception as e:
                        continue
                
                return videos
            else:
                print(f"RSS feed error: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"RSS scraping error: {e}")
            return []
    
    def _classify_channel_tier(self, channel_name: str) -> str:
        """Classify channel into tier based on name"""
        tier_1_keywords = ["explained", "daily", "news", "official", "crypto", "bitcoin"]
        tier_2_keywords = ["analysis", "review", "tech", "ai", "blockchain"]
        
        channel_lower = channel_name.lower()
        
        if any(keyword in channel_lower for keyword in tier_1_keywords):
            return "Tier 1"
        elif any(keyword in channel_lower for keyword in tier_2_keywords):
            return "Tier 2"
        else:
            return "Tier 3"

# Popular AI/Crypto YouTube channels
AI_CRYPTO_CHANNELS = {
    "UCBJycsmduvYEL83R_U4JriQ": "Marco Wutzer",  # AI/ML content
    "UCq-Fj5jknLsUf-MWSy4_brA": "Two Minute Papers",  # AI research
    "UCbfYPyITQ-7l4upoX8nvctg": "3Blue1Brown",  # Math/AI
    "UCsXVk37bltHxD1rDPwtNM8Q": "Kurzgesagt",  # Science/tech
    "UCBJycsmduvYEL83R_U4JriQ": "AI Explained",  # AI news
}

def get_ai_crypto_videos_from_rss(max_results: int = 20) -> List[Dict[str, Any]]:
    """Get AI crypto videos from multiple channels using RSS"""
    scraper = YouTubeRSSScraper()
    all_videos = []
    
    for channel_id, channel_name in AI_CRYPTO_CHANNELS.items():
        try:
            videos = scraper.get_channel_videos(channel_id, max_results // len(AI_CRYPTO_CHANNELS))
            all_videos.extend(videos)
        except Exception as e:
            print(f"Error getting videos from {channel_name}: {e}")
            continue
    
    # Filter for AI/crypto related content
    ai_crypto_videos = []
    keywords = ["ai", "artificial intelligence", "crypto", "cryptocurrency", "blockchain", "machine learning", "neural network"]
    
    for video in all_videos:
        title_lower = video["title"].lower()
        description_lower = video["description"].lower()
        
        if any(keyword in title_lower or keyword in description_lower for keyword in keywords):
            ai_crypto_videos.append(video)
    
    # Sort by published date (newest first)
    ai_crypto_videos.sort(key=lambda x: x["published_at"], reverse=True)
    
    return ai_crypto_videos[:max_results]

if __name__ == "__main__":
    videos = get_ai_crypto_videos_from_rss(10)
    print(f"Found {len(videos)} AI crypto videos")
    for video in videos[:3]:
        print(f"- {video['title']} by {video['channel']}")

