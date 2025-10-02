#!/usr/bin/env python3
"""
YouTube Agent Roma - Test Script
"""

import requests
import json

def test_api():
    """Test the YouTube Agent Roma API"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing YouTube Agent Roma API...")
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ Health check: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # Test search endpoint
    try:
        search_data = {
            "topic": "Restaking on Ethereum for beginners",
            "audience": "beginners"
        }
        response = requests.post(
            f"{base_url}/search",
            headers={"Content-Type": "application/json"},
            json=search_data
        )
        print(f"✅ Search test: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Search test failed: {e}")
    
    # Test analyze endpoint
    try:
        analyze_data = {
            "data": {"content": "test analysis"}
        }
        response = requests.post(
            f"{base_url}/analyze",
            headers={"Content-Type": "application/json"},
            json=analyze_data
        )
        print(f"✅ Analyze test: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Analyze test failed: {e}")
    
    print("\n🎉 API testing complete!")

if __name__ == "__main__":
    test_api()
