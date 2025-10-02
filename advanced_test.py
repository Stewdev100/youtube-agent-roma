#!/usr/bin/env python3
"""
Advanced YouTube Agent Roma Testing Script
"""

import requests
import json
import time

API_BASE = "http://localhost:5050"

def test_search(topic, audience="beginners"):
    """Test search functionality"""
    print(f"\n🔍 Testing: '{topic}' for {audience}")
    
    response = requests.post(f"{API_BASE}/search", 
                           json={"topic": topic, "audience": audience})
    
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            results = data["data"]["results"]
            print(f"✅ Found {len(results)} videos")
            print(f"📊 Total available: {data['data']['total_results']:,}")
            
            # Show first video
            if results:
                first_video = results[0]
                print(f"🎥 Top result: {first_video['title']}")
                print(f"📺 Channel: {first_video['channel']}")
                print(f"🔗 URL: {first_video['url']}")
        else:
            print(f"❌ Search failed: {data.get('error')}")
    else:
        print(f"❌ HTTP Error: {response.status_code}")

def test_analyze():
    """Test analyze functionality"""
    print(f"\n🧠 Testing analyze endpoint")
    
    test_data = {
        "data": {
            "videos": ["test_video_1", "test_video_2"],
            "analysis_type": "sentiment"
        }
    }
    
    response = requests.post(f"{API_BASE}/analyze", json=test_data)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Analysis completed: {data.get('message')}")
    else:
        print(f"❌ Analysis failed: {response.status_code}")

def test_process():
    """Test process functionality"""
    print(f"\n⚙️ Testing process endpoint")
    
    test_data = {
        "input_data": {
            "format": "json",
            "videos": ["video1", "video2"]
        }
    }
    
    response = requests.post(f"{API_BASE}/process", json=test_data)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Processing completed: {data.get('message')}")
    else:
        print(f"❌ Processing failed: {response.status_code}")

def main():
    """Run comprehensive tests"""
    print("🚀 YouTube Agent Roma - Advanced Testing")
    print("=" * 50)
    
    # Test different topics and audiences
    test_cases = [
        ("Cryptocurrency trading strategies", "intermediate"),
        ("Python web development", "beginners"),
        ("Machine learning algorithms", "advanced"),
        ("Digital marketing automation", "professionals"),
        ("Blockchain technology", "students")
    ]
    
    for topic, audience in test_cases:
        test_search(topic, audience)
        time.sleep(1)  # Be nice to the API
    
    # Test other endpoints
    test_analyze()
    test_process()
    
    print("\n🎉 All tests completed!")
    print("\n💡 Try these in your browser at http://localhost:5050")

if __name__ == "__main__":
    main()
