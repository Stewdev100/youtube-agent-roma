#!/usr/bin/env python3
"""
AI Crypto Dashboard - Web Interface for Data Feed
Visual dashboard for monitoring AI crypto content creators
"""

from flask import Flask, render_template, jsonify, request
import json
from datetime import datetime, timedelta
from ai_crypto_channel_library import AICryptoChannelLibrary

app = Flask(__name__)

class AICryptoDashboard:
    """Dashboard for AI crypto data feed"""
    
    def __init__(self):
        self.library = AICryptoChannelLibrary()
        self.data_file = "ai_crypto_feed.json"
        self.load_data()
    
    def load_data(self):
        """Load data from file"""
        try:
            with open(self.data_file, 'r') as f:
                self.feed_data = json.load(f)
        except FileNotFoundError:
            self.feed_data = {
                "channels": {},
                "trending_topics": {},
                "alerts": [],
                "last_updated": None
            }
    
    def get_dashboard_data(self):
        """Get data for dashboard"""
        # Fetch real YouTube videos about AI crypto projects
        recent_videos = self.library.fetch_ai_crypto_videos(20)
        
        # Process videos for display
        processed_videos = []
        for video in recent_videos:
            try:
                video_time = datetime.fromisoformat(video["published_at"].replace('Z', '+00:00'))
                processed_videos.append({
                    **video,
                    "channel_name": video["channel"],
                    "time_ago": self._time_ago(video_time)
                })
            except:
                # Handle any date parsing errors
                processed_videos.append({
                    **video,
                    "channel_name": video["channel"],
                    "time_ago": "Recently"
                })
        
        # Calculate statistics
        total_videos = len(processed_videos)
        unique_channels = len(set(video["channel"] for video in processed_videos))
        
        # Recent activity (last 24 hours)
        cutoff_time = datetime.now() - timedelta(hours=24)
        recent_24h_videos = []
        for video in processed_videos:
            try:
                video_time = datetime.fromisoformat(video["published_at"].replace('Z', '+00:00'))
                if video_time > cutoff_time:
                    recent_24h_videos.append(video)
            except:
                continue
        
        # Top channels by video count
        channel_counts = {}
        for video in processed_videos:
            channel = video["channel"]
            channel_counts[channel] = channel_counts.get(channel, 0) + 1
        
        top_channels = [(channel, count) for channel, count in channel_counts.items()]
        top_channels.sort(key=lambda x: x[1], reverse=True)
        
        # Recent alerts
        recent_alerts = self.library.get_alerts(24)
        
        return {
            "stats": {
                "total_videos": total_videos,
                "active_channels": unique_channels,
                "recent_videos_24h": len(recent_24h_videos),
                "recent_alerts_24h": len(recent_alerts)
            },
            "recent_videos": processed_videos[:20],  # Last 20 videos
            "top_channels": top_channels[:10],
            "recent_alerts": recent_alerts[-10:],  # Last 10 alerts
            "last_updated": datetime.now().isoformat()
        }
    
    def _time_ago(self, dt):
        """Calculate time ago string"""
        now = datetime.now(dt.tzinfo)
        diff = now - dt
        
        if diff.days > 0:
            return f"{diff.days}d ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours}h ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes}m ago"
        else:
            return "Just now"

# Initialize dashboard
dashboard = AICryptoDashboard()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('ai_crypto_dashboard.html')

@app.route('/api/dashboard')
def api_dashboard():
    """API endpoint for dashboard data"""
    return jsonify(dashboard.get_dashboard_data())

@app.route('/api/channels')
def api_channels():
    """API endpoint for channel data"""
    return jsonify(dashboard.feed_data["channels"])

@app.route('/api/trending')
def api_trending():
    """API endpoint for trending topics"""
    return jsonify(dashboard.feed_data.get("trending_topics", {}))

@app.route('/api/alerts')
def api_alerts():
    """API endpoint for alerts"""
    hours = request.args.get('hours', 24, type=int)
    cutoff_time = datetime.now() - timedelta(hours=hours)
    
    recent_alerts = [a for a in dashboard.feed_data["alerts"] 
                    if datetime.fromisoformat(a["timestamp"]) > cutoff_time]
    
    return jsonify({
        "alerts": recent_alerts,
        "count": len(recent_alerts),
        "hours": hours
    })

@app.route('/api/refresh')
def api_refresh():
    """API endpoint to refresh data"""
    try:
        # Run monitoring cycle
        from ai_crypto_monitor import AICryptoMonitor
        monitor = AICryptoMonitor()
        monitor.check_for_new_content()
        
        # Reload data
        dashboard.load_data()
        
        return jsonify({
            "success": True,
            "message": "Data refreshed successfully",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/dashboard')
def full_dashboard():
    """Full AI Crypto Dashboard with all features"""
    return render_template('full_dashboard.html')

@app.route('/search')
def search_page():
    """AI Crypto Search Tool page"""
    return render_template('ai_crypto_search.html')

@app.route('/api/search')
def search_api():
    """AI Crypto Search API endpoint"""
    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify({
            "status": "error",
            "message": "Search query is required"
        }), 400
    
    try:
        # Simulate comprehensive search results
        search_results = {
            "query": query,
            "total_results": 0,
            "results": []
        }
        
        # AI Crypto Projects search
        ai_crypto_projects = [
            {"name": "Bittensor (TAO)", "symbol": "TAO", "price": "$400.06", "change": "+38.61%", "category": "AI Training Network"},
            {"name": "NEAR Protocol (NEAR)", "symbol": "NEAR", "price": "$2.16", "change": "+3.10%", "category": "AI Development Platform"},
            {"name": "Story Protocol (IP)", "symbol": "IP", "price": "$5.40", "change": "+1.41%", "category": "AI Content Creation"},
            {"name": "Internet Computer (ICP)", "symbol": "ICP", "price": "$3.02", "change": "+2.20%", "category": "AI Computing Infrastructure"},
            {"name": "Render (RENDER)", "symbol": "RENDER", "price": "$2.45", "change": "+5.77%", "category": "AI Rendering Network"},
            {"name": "Filecoin (FIL)", "symbol": "FIL", "price": "$4.12", "change": "+1.85%", "category": "AI Data Storage"},
            {"name": "Injective (INJ)", "symbol": "INJ", "price": "$24.50", "change": "+2.45%", "category": "AI Trading Protocol"},
            {"name": "The Graph (GRT)", "symbol": "GRT", "price": "$0.15", "change": "+4.20%", "category": "AI Data Indexing"},
            {"name": "Artificial Superintelligence Alliance (FET)", "symbol": "FET", "price": "$1.85", "change": "+3.15%", "category": "AI Development"},
            {"name": "Theta Network (THETA)", "symbol": "THETA", "price": "$0.95", "change": "+2.80%", "category": "AI Video Streaming"}
        ]
        
        # Filter results based on query
        filtered_projects = []
        for project in ai_crypto_projects:
            if (query.lower() in project["name"].lower() or 
                query.lower() in project["symbol"].lower() or 
                query.lower() in project["category"].lower()):
                filtered_projects.append({
                    "type": "project",
                    "title": project["name"],
                    "symbol": project["symbol"],
                    "price": project["price"],
                    "change": project["change"],
                    "category": project["category"],
                    "relevance": "95%"
                })
        
        # Add YouTube videos related to the search
        youtube_results = [
            {
                "type": "video",
                "title": f"🚀 {query} Price Analysis & Future Predictions",
                "channel": "AI Crypto News",
                "video_id": "9bZkp7q19f0",
                "video_url": "https://www.youtube.com/watch?v=9bZkp7q19f0",
                "description": f"Comprehensive analysis of {query} token, market trends, and future predictions in the AI crypto space.",
                "relevance": "92%"
            },
            {
                "type": "video", 
                "title": f"📊 {query} Technical Analysis & Trading Strategy",
                "channel": "Crypto Trading Pro",
                "video_id": "M7lc1UVf-VE",
                "video_url": "https://www.youtube.com/watch?v=M7lc1UVf-VE",
                "description": f"Deep dive into {query} technical indicators, support/resistance levels, and trading opportunities.",
                "relevance": "88%"
            },
            {
                "type": "video",
                "title": f"🔍 {query} Project Deep Dive & Roadmap",
                "channel": "Blockchain AI",
                "video_id": "kJQP7kiw5Fk", 
                "video_url": "https://www.youtube.com/watch?v=kJQP7kiw5Fk",
                "description": f"Complete project analysis of {query}, including technology, team, partnerships, and future roadmap.",
                "relevance": "85%"
            }
        ]
        
        # Add news articles
        news_results = [
            {
                "type": "news",
                "title": f"{query} Surges 25% as AI Crypto Market Heats Up",
                "source": "CryptoNews",
                "url": "#",
                "published": "2 hours ago",
                "relevance": "90%"
            },
            {
                "type": "news",
                "title": f"Major Partnership Announcement Boosts {query} Adoption",
                "source": "AI Crypto Daily",
                "url": "#",
                "published": "5 hours ago", 
                "relevance": "87%"
            }
        ]
        
        # Combine all results
        all_results = filtered_projects + youtube_results + news_results
        search_results["total_results"] = len(all_results)
        search_results["results"] = all_results
        
        return jsonify(search_results)
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Search failed: {str(e)}"
        }), 500

if __name__ == '__main__':
    # Create templates directory and HTML file
    import os
    os.makedirs('templates', exist_ok=True)
    
    # Create the HTML template
    html_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Crypto Dashboard</title>
    <link rel="icon" type="image/svg+xml" href="/static/branding/favicon.svg">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #f5576c 75%, #4facfe 100%);
            background-size: 400% 400%;
            animation: gradientShift 15s ease infinite;
            min-height: 100vh;
            color: #333;
            position: relative;
            overflow-x: hidden;
        }
        
        @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.4) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.4) 0%, transparent 50%),
                radial-gradient(circle at 40% 40%, rgba(120, 219, 255, 0.3) 0%, transparent 50%),
                radial-gradient(circle at 60% 60%, rgba(255, 200, 100, 0.2) 0%, transparent 50%);
            pointer-events: none;
            z-index: -1;
            animation: floatBackground 20s ease-in-out infinite;
        }
        
        @keyframes floatBackground {
            0%, 100% { transform: translateY(0px) rotate(0deg); }
            33% { transform: translateY(-20px) rotate(1deg); }
            66% { transform: translateY(10px) rotate(-1deg); }
        }
        
        body::after {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.1) 50%, transparent 70%);
            pointer-events: none;
            z-index: -1;
            animation: shimmer 8s ease-in-out infinite;
        }
        
        @keyframes shimmer {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(100%); }
        }
        
        /* Custom Branding Graphics */
        .brand-graphics {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 1;
        }
        
        .crypto-symbol {
            position: absolute;
            width: 40px;
            height: 40px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            border-radius: 8px;
            animation: symbolFloat 8s ease-in-out infinite;
            box-shadow: 0 0 20px rgba(102, 126, 234, 0.3);
        }
        
        .crypto-symbol::before {
            content: '₿';
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: white;
            font-size: 1.5rem;
            font-weight: bold;
        }
        
        .crypto-symbol:nth-child(1) { top: 10%; left: 10%; animation-delay: 0s; }
        .crypto-symbol:nth-child(2) { top: 20%; right: 15%; animation-delay: 2s; }
        .crypto-symbol:nth-child(3) { bottom: 30%; left: 20%; animation-delay: 4s; }
        .crypto-symbol:nth-child(4) { bottom: 15%; right: 10%; animation-delay: 6s; }
        
        @keyframes symbolFloat {
            0%, 100% { transform: translateY(0px) rotate(0deg); }
            50% { transform: translateY(-20px) rotate(180deg); }
        }
        
        .neural-network {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 200px;
            height: 200px;
            opacity: 0.1;
            animation: networkPulse 6s ease-in-out infinite;
        }
        
        .neural-network::before,
        .neural-network::after {
            content: '';
            position: absolute;
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-radius: 50%;
        }
        
        .neural-network::before {
            width: 100px;
            height: 100px;
            top: 50px;
            left: 50px;
            animation: networkRotate 10s linear infinite;
        }
        
        .neural-network::after {
            width: 60px;
            height: 60px;
            top: 70px;
            left: 70px;
            animation: networkRotate 8s linear infinite reverse;
        }
        
        @keyframes networkPulse {
            0%, 100% { transform: translate(-50%, -50%) scale(1); }
            50% { transform: translate(-50%, -50%) scale(1.1); }
        }
        
        @keyframes networkRotate {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .data-visualization {
            position: absolute;
            top: 15%;
            right: 5%;
            width: 100px;
            height: 100px;
            opacity: 0.2;
            animation: dataVisualize 4s ease-in-out infinite;
        }
        
        .data-visualization::before,
        .data-visualization::after {
            content: '';
            position: absolute;
            background: linear-gradient(45deg, #667eea, #764ba2);
            border-radius: 4px;
        }
        
        .data-visualization::before {
            width: 4px;
            height: 60px;
            top: 20px;
            left: 20px;
            animation: barGrow 2s ease-in-out infinite;
        }
        
        .data-visualization::after {
            width: 4px;
            height: 40px;
            top: 40px;
            left: 40px;
            animation: barGrow 2s ease-in-out infinite 0.5s;
        }
        
        @keyframes dataVisualize {
            0%, 100% { transform: scale(1) rotate(0deg); }
            50% { transform: scale(1.1) rotate(5deg); }
        }
        
        @keyframes barGrow {
            0%, 100% { height: 20px; }
            50% { height: 60px; }
        }
        
        .crypto-chart {
            position: absolute;
            bottom: 20%;
            left: 5%;
            width: 80px;
            height: 50px;
            opacity: 0.15;
            animation: chartPulse 3s ease-in-out infinite;
        }
        
        .crypto-chart::before {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 30px;
            background: linear-gradient(45deg, #f093fb, #f5576c);
            clip-path: polygon(0% 100%, 20% 80%, 40% 60%, 60% 40%, 80% 20%, 100% 0%);
        }
        
        @keyframes chartPulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }
        
        /* Floating Particles */
        .particles {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 1;
        }
        
        .particle {
            position: absolute;
            width: 4px;
            height: 4px;
            background: rgba(255, 255, 255, 0.6);
            border-radius: 50%;
            animation: floatParticle 20s linear infinite;
        }
        
        .particle:nth-child(1) { left: 10%; animation-delay: 0s; }
        .particle:nth-child(2) { left: 20%; animation-delay: 2s; }
        .particle:nth-child(3) { left: 30%; animation-delay: 4s; }
        .particle:nth-child(4) { left: 40%; animation-delay: 6s; }
        .particle:nth-child(5) { left: 50%; animation-delay: 8s; }
        .particle:nth-child(6) { left: 60%; animation-delay: 10s; }
        .particle:nth-child(7) { left: 70%; animation-delay: 12s; }
        .particle:nth-child(8) { left: 80%; animation-delay: 14s; }
        .particle:nth-child(9) { left: 90%; animation-delay: 16s; }
        .particle:nth-child(10) { left: 15%; animation-delay: 18s; }
        
        @keyframes floatParticle {
            0% {
                transform: translateY(100vh) rotate(0deg);
                opacity: 0;
            }
            10% {
                opacity: 1;
            }
            90% {
                opacity: 1;
            }
            100% {
                transform: translateY(-100px) rotate(360deg);
                opacity: 0;
            }
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 50px;
            color: white;
            position: relative;
        }
        
        .header h1 {
            font-size: 4rem;
            margin-bottom: 20px;
            text-shadow: 
                0 0 10px rgba(255,255,255,0.5),
                0 0 20px rgba(255,255,255,0.3),
                0 0 30px rgba(255,255,255,0.2),
                2px 2px 4px rgba(0,0,0,0.3);
            background: linear-gradient(45deg, #fff, #f0f0f0, #fff, #e0e0e0);
            background-size: 400% 400%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            animation: textShimmer 3s ease-in-out infinite;
            position: relative;
        }
        
        @keyframes textShimmer {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        .header h1::before {
            content: '';
            position: absolute;
            left: -80px;
            top: 50%;
            transform: translateY(-50%);
            width: 60px;
            height: 60px;
            background: linear-gradient(45deg, #667eea, #764ba2, #f093fb);
            border-radius: 50%;
            animation: logoFloat 2s ease-in-out infinite;
            box-shadow: 
                0 0 20px rgba(102, 126, 234, 0.5),
                0 0 40px rgba(118, 75, 162, 0.3),
                inset 0 0 20px rgba(255, 255, 255, 0.2);
        }
        
        .header h1::after {
            content: '⚡';
            position: absolute;
            left: -75px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 2rem;
            color: white;
            text-shadow: 0 0 10px rgba(255, 255, 255, 0.8);
            animation: logoFloat 2s ease-in-out infinite;
        }
        
        @keyframes logoFloat {
            0%, 100% { transform: translateY(-50%) rotate(-5deg) scale(1); }
            50% { transform: translateY(-60%) rotate(5deg) scale(1.1); }
        }
        
        .header p {
            font-size: 1.3rem;
            opacity: 0.95;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
            animation: fadeInUp 1s ease-out;
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 0.95;
                transform: translateY(0);
            }
        }
        
        .header-actions {
            display: flex;
            gap: 15px;
            justify-content: center;
            align-items: center;
            flex-wrap: wrap;
            margin-top: 20px;
        }
        
        .search-link {
            background: rgba(255,255,255,0.2);
            color: white;
            padding: 12px 24px;
            border-radius: 25px;
            text-decoration: none;
            font-weight: 500;
            transition: all 0.3s ease;
            border: 2px solid rgba(255,255,255,0.3);
        }
        
        .search-link:hover {
            background: rgba(255,255,255,0.3);
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        
        /* Modern Search Interface */
        .main-search-container {
            max-width: 800px;
            margin: 0 auto;
            padding: 40px 20px;
        }
        
        .search-hero {
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(25px);
            border-radius: 40px;
            padding: 80px 50px;
            text-align: center;
            box-shadow: 
                0 30px 60px rgba(0, 0, 0, 0.2),
                0 0 0 1px rgba(255, 255, 255, 0.1),
                inset 0 1px 0 rgba(255, 255, 255, 0.3);
            border: 2px solid rgba(255, 255, 255, 0.2);
            margin-bottom: 50px;
            position: relative;
            overflow: hidden;
            animation: heroFloat 6s ease-in-out infinite;
        }
        
        @keyframes heroFloat {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
        }
        
        .search-hero::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: conic-gradient(from 0deg, transparent, rgba(255,255,255,0.1), transparent);
            animation: rotate 10s linear infinite;
            z-index: -1;
        }
        
        @keyframes rotate {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .search-hero::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(45deg, 
                rgba(255,255,255,0.1) 0%, 
                transparent 25%, 
                transparent 75%, 
                rgba(255,255,255,0.1) 100%);
            animation: sweep 4s ease-in-out infinite;
            z-index: -1;
        }
        
        @keyframes sweep {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(100%); }
        }
        
        .search-box-large {
            display: flex;
            margin-bottom: 40px;
            border-radius: 30px;
            overflow: hidden;
            box-shadow: 
                0 25px 50px rgba(0, 0, 0, 0.2),
                0 0 0 1px rgba(255, 255, 255, 0.2),
                inset 0 1px 0 rgba(255, 255, 255, 0.3);
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(15px);
            position: relative;
            animation: searchBoxPulse 4s ease-in-out infinite;
        }
        
        @keyframes searchBoxPulse {
            0%, 100% { 
                box-shadow: 
                    0 25px 50px rgba(0, 0, 0, 0.2),
                    0 0 0 1px rgba(255, 255, 255, 0.2),
                    inset 0 1px 0 rgba(255, 255, 255, 0.3);
            }
            50% { 
                box-shadow: 
                    0 30px 60px rgba(0, 0, 0, 0.3),
                    0 0 0 2px rgba(255, 255, 255, 0.4),
                    inset 0 1px 0 rgba(255, 255, 255, 0.5);
            }
        }
        
        .search-box-large::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, 
                transparent, 
                rgba(255,255,255,0.4), 
                transparent);
            animation: searchShimmer 3s ease-in-out infinite;
        }
        
        .search-box-large::after {
            content: '🔍';
            position: absolute;
            right: 20px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 1.5rem;
            opacity: 0.3;
            animation: searchIconPulse 2s ease-in-out infinite;
            z-index: 2;
        }
        
        @keyframes searchShimmer {
            0% { left: -100%; }
            100% { left: 100%; }
        }
        
        @keyframes searchIconPulse {
            0%, 100% { opacity: 0.3; transform: translateY(-50%) scale(1); }
            50% { opacity: 0.6; transform: translateY(-50%) scale(1.1); }
        }
        
        .search-box-large input {
            flex: 1;
            padding: 25px 30px;
            border: none;
            font-size: 1.3rem;
            background: transparent;
            color: #333;
            font-weight: 500;
        }
        
        .search-box-large input:focus {
            outline: none;
        }
        
        .search-box-large input::placeholder {
            color: #666;
            font-weight: 400;
        }
        
        .search-box-large button {
            padding: 25px 40px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            background-size: 200% 200%;
            color: white;
            border: none;
            font-size: 1.3rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
            animation: buttonGradient 3s ease infinite;
        }
        
        @keyframes buttonGradient {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        .search-box-large button::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
            transition: left 0.5s;
        }
        
        .search-box-large button:hover::before {
            left: 100%;
        }
        
        .search-box-large button::after {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            background: rgba(255,255,255,0.2);
            border-radius: 50%;
            transform: translate(-50%, -50%);
            transition: all 0.3s ease;
        }
        
        .search-box-large button:hover::after {
            width: 300px;
            height: 300px;
        }
        
        .search-box-large button:hover {
            transform: scale(1.08);
            box-shadow: 
                0 15px 40px rgba(102, 126, 234, 0.5),
                0 0 20px rgba(240, 147, 251, 0.3);
        }
        
        .search-hint {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
            color: rgba(255, 255, 255, 0.9);
            font-size: 1.1rem;
            font-weight: 500;
        }
        
        .hint-icon {
            font-size: 2rem;
            animation: float 3s ease-in-out infinite;
            filter: drop-shadow(0 0 10px rgba(255,255,255,0.5));
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0px) rotate(0deg); }
            50% { transform: translateY(-15px) rotate(10deg); }
        }
        
        .hint-text {
            animation: textGlow 2s ease-in-out infinite alternate;
        }
        
        @keyframes textGlow {
            from { text-shadow: 0 0 5px rgba(255,255,255,0.5); }
            to { text-shadow: 0 0 20px rgba(255,255,255,0.8), 0 0 30px rgba(255,255,255,0.4); }
        }
        
        .quick-actions {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            margin-top: 40px;
        }
        
        .action-card {
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(25px);
            border-radius: 25px;
            padding: 40px;
            text-decoration: none;
            color: white;
            transition: all 0.4s ease;
            border: 2px solid rgba(255, 255, 255, 0.2);
            position: relative;
            overflow: hidden;
            animation: cardFloat 8s ease-in-out infinite;
        }
        
        .action-card:nth-child(2) {
            animation-delay: -4s;
        }
        
        @keyframes cardFloat {
            0%, 100% { transform: translateY(0px) rotate(0deg); }
            50% { transform: translateY(-5px) rotate(1deg); }
        }
        
        .action-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(135deg, 
                rgba(255,255,255,0.2) 0%, 
                rgba(255,255,255,0.1) 50%,
                rgba(255,255,255,0.05) 100%);
            opacity: 0;
            transition: opacity 0.4s ease;
        }
        
        .action-card::after {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: conic-gradient(from 0deg, 
                transparent, 
                rgba(255,255,255,0.1), 
                transparent, 
                rgba(255,255,255,0.05), 
                transparent);
            animation: cardRotate 15s linear infinite;
            opacity: 0;
            transition: opacity 0.4s ease;
        }
        
        @keyframes cardRotate {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .action-card:hover::before {
            opacity: 1;
        }
        
        .action-card:hover::after {
            opacity: 1;
        }
        
        .action-card:hover {
            transform: translateY(-15px) scale(1.02);
            box-shadow: 
                0 25px 50px rgba(0, 0, 0, 0.3),
                0 0 30px rgba(255, 255, 255, 0.2);
            border-color: rgba(255, 255, 255, 0.4);
        }
        
        .action-icon {
            font-size: 4rem;
            margin-bottom: 20px;
            display: block;
            animation: iconBounce 2s ease-in-out infinite;
            filter: drop-shadow(0 0 10px rgba(255,255,255,0.3));
            position: relative;
        }
        
        .action-icon::before {
            content: '';
            position: absolute;
            top: -10px;
            left: -10px;
            right: -10px;
            bottom: -10px;
            background: linear-gradient(45deg, rgba(102, 126, 234, 0.2), rgba(240, 147, 251, 0.2));
            border-radius: 50%;
            z-index: -1;
            animation: iconGlow 3s ease-in-out infinite;
        }
        
        @keyframes iconBounce {
            0%, 100% { transform: scale(1) rotate(0deg); }
            50% { transform: scale(1.1) rotate(5deg); }
        }
        
        @keyframes iconGlow {
            0%, 100% { opacity: 0.3; transform: scale(1); }
            50% { opacity: 0.6; transform: scale(1.2); }
        }
        
        .action-title {
            font-size: 1.6rem;
            font-weight: 700;
            margin-bottom: 12px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
            background: linear-gradient(45deg, #fff, #f0f0f0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .action-desc {
            font-size: 1.1rem;
            opacity: 0.9;
            text-shadow: 0 1px 2px rgba(0,0,0,0.2);
        }
        
        .search-results {
            margin-top: 30px;
        }
        
        .result-item {
            background: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 15px;
            border-left: 4px solid #667eea;
            transition: all 0.3s ease;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }
        
        .result-item:hover {
            transform: translateX(10px);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
        }
        
        .result-title {
            font-size: 1.2rem;
            font-weight: 600;
            color: #333;
            margin-bottom: 8px;
        }
        
        .result-title a {
            color: #667eea;
            text-decoration: none;
        }
        
        .result-title a:hover {
            text-decoration: underline;
        }
        
        .result-meta {
            font-size: 0.9rem;
            color: #666;
            margin-bottom: 8px;
        }
        
        .result-description {
            color: #555;
            line-height: 1.5;
            font-size: 0.95rem;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s ease;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
        }
        
        .stat-number {
            font-size: 2.5rem;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }
        
        .stat-label {
            font-size: 1rem;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .content-grid {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 30px;
        }
        
        .panel {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        .panel h2 {
            margin-bottom: 20px;
            color: #333;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        
        .video-item {
            display: flex;
            align-items: flex-start;
            padding: 15px;
            border-bottom: 1px solid #eee;
            transition: background 0.3s ease;
            gap: 15px;
        }
        
        .video-thumbnail {
            flex-shrink: 0;
            width: 120px;
            height: 90px;
        }
        
        .video-thumbnail img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            border-radius: 8px;
            transition: transform 0.3s ease;
        }
        
        .video-thumbnail img:hover {
            transform: scale(1.05);
        }
        
        /* Market Overview Styles */
        .market-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 20px;
            margin-top: 15px;
        }
        
        .stat-item {
            text-align: center;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 12px;
            color: white;
        }
        
        .stat-label {
            font-size: 0.9rem;
            opacity: 0.9;
            margin-bottom: 8px;
        }
        
        .stat-value {
            font-size: 1.8rem;
            font-weight: bold;
        }
        
        /* Top Projects Styles */
        .project-list {
            margin-top: 15px;
        }
        
        .project-item {
            display: flex;
            align-items: center;
            padding: 15px;
            margin-bottom: 10px;
            background: #f8f9fa;
            border-radius: 10px;
            border-left: 4px solid #007bff;
        }
        
        .project-rank {
            width: 30px;
            height: 30px;
            background: #007bff;
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            margin-right: 15px;
        }
        
        .project-info {
            flex: 1;
        }
        
        .project-name {
            font-weight: 600;
            color: #333;
        }
        
        .project-price {
            font-size: 0.9rem;
            color: #666;
            margin-top: 2px;
        }
        
        .project-change {
            font-weight: bold;
            padding: 4px 8px;
            border-radius: 6px;
        }
        
        .project-change.positive {
            background: #d4edda;
            color: #155724;
        }
        
        .project-change.negative {
            background: #f8d7da;
            color: #721c24;
        }
        
        /* Search Section Styles */
        .search-box {
            display: flex;
            margin-bottom: 15px;
        }
        
        .search-box input {
            flex: 1;
            padding: 12px;
            border: 2px solid #e9ecef;
            border-radius: 8px 0 0 8px;
            font-size: 1rem;
        }
        
        .search-box button {
            padding: 12px 20px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 0 8px 8px 0;
            cursor: pointer;
            font-size: 1.2rem;
        }
        
        .search-box button:hover {
            background: #0056b3;
        }
        
        .search-results {
            min-height: 100px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        
        .search-hint {
            color: #666;
            font-style: italic;
            text-align: center;
            padding: 20px;
        }
        
        /* Trending Topics Styles */
        .topic-list {
            margin-top: 15px;
        }
        
        .topic-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px;
            margin-bottom: 8px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #28a745;
        }
        
        .topic-tag {
            font-weight: 600;
            color: #007bff;
        }
        
        .topic-count {
            font-size: 0.9rem;
            color: #666;
        }
        
        /* Responsive Grid */
        .content-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        @media (max-width: 768px) {
            .content-grid {
                grid-template-columns: 1fr;
            }
            
            .market-stats {
                grid-template-columns: 1fr;
            }
        }
        
        .video-item:hover {
            background: #f8f9ff;
        }
        
        .video-item:last-child {
            border-bottom: none;
        }
        
        .video-info {
            flex: 1;
        }
        
        .video-title {
            font-weight: 600;
            margin-bottom: 5px;
            color: #333;
        }
        
        .video-meta {
            font-size: 0.9rem;
            color: #666;
        }
        
        .video-description {
            font-size: 0.85rem;
            color: #888;
            margin-top: 5px;
            line-height: 1.4;
        }
        
        .video-link {
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
        }
        
        .video-link:hover {
            text-decoration: underline;
        }
        
        .tier-badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 600;
            margin-left: 10px;
        }
        
        .tier-1 { background: #ff6b6b; color: white; }
        .tier-2 { background: #4ecdc4; color: white; }
        .tier-3 { background: #45b7d1; color: white; }
        
        .alert-item {
            padding: 15px;
            border-left: 4px solid #ff6b6b;
            background: #fff5f5;
            margin-bottom: 10px;
            border-radius: 0 8px 8px 0;
        }
        
        .alert-message {
            font-weight: 600;
            margin-bottom: 5px;
        }
        
        .alert-time {
            font-size: 0.9rem;
            color: #666;
        }
        
        .refresh-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1rem;
            margin-bottom: 20px;
            transition: background 0.3s ease;
        }
        
        .refresh-btn:hover {
            background: #5a6fd8;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 15px;
            }
            
            .header h1 {
                font-size: 2.5rem;
            }
            
            .header h1::before {
                left: -40px;
                font-size: 2rem;
            }
            
            .search-hero {
                padding: 40px 20px;
                border-radius: 25px;
            }
            
            .search-box-large {
                flex-direction: column;
                border-radius: 20px;
            }
            
            .search-box-large input {
                border-radius: 20px 20px 0 0;
                padding: 20px 25px;
                font-size: 1.1rem;
            }
            
            .search-box-large button {
                border-radius: 0 0 20px 20px;
                padding: 20px 30px;
                font-size: 1.1rem;
            }
            
            .quick-actions {
                grid-template-columns: 1fr;
                gap: 20px;
            }
            
            .action-card {
                padding: 30px 20px;
            }
            
            .action-icon {
                font-size: 3rem;
            }
            
            .action-title {
                font-size: 1.4rem;
            }
            
            .content-grid {
                grid-template-columns: 1fr;
            }
            
            .stats-grid {
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            }
            
            .particle {
                width: 3px;
                height: 3px;
            }
            
            .crypto-symbol {
                width: 30px;
                height: 30px;
            }
            
            .crypto-symbol::before {
                font-size: 1.2rem;
            }
            
            .neural-network {
                width: 150px;
                height: 150px;
            }
            
            .data-visualization {
                width: 80px;
                height: 80px;
            }
            
            .crypto-chart {
                width: 60px;
                height: 40px;
            }
        }
        
        @media (max-width: 480px) {
            .header h1 {
                font-size: 2rem;
            }
            
            .header h1::before {
                display: none;
            }
            
            .search-hero {
                padding: 30px 15px;
            }
            
            .action-card {
                padding: 25px 15px;
            }
        }
    </style>
</head>
<body>
    <!-- Custom Branding Graphics -->
    <div class="brand-graphics">
        <div class="crypto-symbol"></div>
        <div class="crypto-symbol"></div>
        <div class="crypto-symbol"></div>
        <div class="crypto-symbol"></div>
        <div class="neural-network"></div>
        <div class="data-visualization"></div>
        <div class="crypto-chart"></div>
    </div>
    
    <!-- Floating Particles -->
    <div class="particles">
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
    </div>
    
    <div class="container">
        <div class="header">
            <img src="/static/branding/ai-logo.svg" alt="AI Crypto Hub" style="height:48px; margin-bottom:16px; filter: drop-shadow(0 2px 6px rgba(0,0,0,0.35));" />
            <h1>🚀 AI Crypto Hub</h1>
            <p>Discover the future of AI-powered cryptocurrency</p>
        </div>
        
        <div class="main-search-container">
            <div class="search-hero" style="background-image: url('/static/branding/hero-illustration.svg'); background-size: cover; background-position: center; background-blend-mode: overlay;">
                <div class="search-box-large">
                    <input type="text" id="searchInput" placeholder="Search AI crypto projects, tokens, videos..." />
                    <button id="searchBtn">🔍 Search</button>
                </div>
                <div class="search-results" id="searchResults">
                    <div class="search-hint">
                        <div class="hint-icon">🚀</div>
                        <div class="hint-text">Discover the latest AI crypto projects and videos</div>
                    </div>
                </div>
            </div>
            
            <div class="quick-actions">
                <a href="/dashboard" class="action-card">
                    <div class="action-icon">📊</div>
                    <div class="action-title">Full Dashboard</div>
                    <div class="action-desc">Complete AI crypto overview with real-time data</div>
                </a>
                <a href="/search" class="action-card">
                    <div class="action-icon">🔍</div>
                    <div class="action-title">Advanced Search</div>
                    <div class="action-desc">AI-powered search with smart filters</div>
                </a>
            </div>
        </div>
    </div>
    
    <script>
        async function loadDashboardData() {
            try {
                const response = await fetch('/api/dashboard');
                const data = await response.json();
                
                updateStats(data.stats);
                updateRecentVideos(data.recent_videos);
                updateRecentAlerts(data.recent_alerts);
                
            } catch (error) {
                console.error('Error loading dashboard data:', error);
            }
        }
        
        function updateStats(stats) {
            const statsGrid = document.getElementById('statsGrid');
            statsGrid.innerHTML = `
                <div class="stat-card">
                    <div class="stat-number">${stats.total_videos}</div>
                    <div class="stat-label">Total Videos</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${stats.active_channels}</div>
                    <div class="stat-label">Active Channels</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${stats.recent_videos_24h}</div>
                    <div class="stat-label">Videos (24h)</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${stats.recent_alerts_24h}</div>
                    <div class="stat-label">Alerts (24h)</div>
                </div>
            `;
        }
        
        function updateRecentVideos(videos) {
            const container = document.getElementById('recentVideos');
            
            if (videos.length === 0) {
                container.innerHTML = '<div class="loading">No recent AI crypto videos found</div>';
                return;
            }
            
            container.innerHTML = videos.map(video => `
                <div class="video-item">
                    <div class="video-thumbnail">
                        <a href="${video.video_url}" target="_blank">
                            <img src="${video.thumbnail || 'https://img.youtube.com/vi/' + video.video_id + '/mqdefault.jpg'}" 
                                 alt="${video.title}" 
                                 onerror="this.src='https://img.youtube.com/vi/${video.video_id}/mqdefault.jpg'">
                        </a>
                    </div>
                    <div class="video-info">
                        <div class="video-title">
                            <a href="${video.video_url}" target="_blank" class="video-link">${video.title}</a>
                            <span class="tier-badge tier-${video.tier.toLowerCase().replace(' ', '-')}">${video.tier}</span>
                        </div>
                        <div class="video-meta">
                            📺 ${video.channel} • ⏰ ${video.time_ago}
                        </div>
                        ${video.description ? `<div class="video-description">${video.description}</div>` : ''}
                    </div>
                </div>
            `).join('');
        }
        
        function updateRecentAlerts(alerts) {
            const container = document.getElementById('recentAlerts');
            
            if (alerts.length === 0) {
                container.innerHTML = '<div class="loading">No recent alerts</div>';
                return;
            }
            
            container.innerHTML = alerts.map(alert => `
                <div class="alert-item">
                    <div class="alert-message">${alert.message}</div>
                    <div class="alert-time">${new Date(alert.timestamp).toLocaleString()}</div>
                </div>
            `).join('');
        }
        
        async function refreshData() {
            const btn = document.querySelector('.refresh-btn');
            btn.textContent = '🔄 Refreshing...';
            btn.disabled = true;
            
            try {
                await fetch('/api/refresh');
                await loadDashboardData();
            } catch (error) {
                console.error('Error refreshing data:', error);
            } finally {
                btn.textContent = '🔄 Refresh Data';
                btn.disabled = false;
            }
        }
        
        // Search functionality
        document.getElementById('searchBtn').addEventListener('click', performSearch);
        document.getElementById('searchInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                performSearch();
            }
        });
        
        function performSearch() {
            const query = document.getElementById('searchInput').value.trim();
            const resultsDiv = document.getElementById('searchResults');
            
            if (!query) {
                resultsDiv.innerHTML = '<div class="search-hint">Search for AI crypto projects, tokens, or analysis</div>';
                return;
            }
            
            // Simulate search results
            const searchResults = [
                { title: `Bittensor (TAO) - ${query} Analysis`, type: 'Project', relevance: '95%' },
                { title: `NEAR Protocol - ${query} Integration`, type: 'Platform', relevance: '87%' },
                { title: `Render Network - ${query} Rendering`, type: 'Service', relevance: '82%' },
                { title: `AI Crypto Market - ${query} Trends`, type: 'Analysis', relevance: '78%' }
            ];
            
            resultsDiv.innerHTML = searchResults.map(result => `
                <div class="search-result-item" style="padding: 10px; margin-bottom: 8px; background: white; border-radius: 6px; border-left: 3px solid #007bff;">
                    <div style="font-weight: 600; color: #333;">${result.title}</div>
                    <div style="font-size: 0.9rem; color: #666; margin-top: 4px;">
                        <span style="background: #e9ecef; padding: 2px 6px; border-radius: 4px; margin-right: 8px;">${result.type}</span>
                        <span>Relevance: ${result.relevance}</span>
                    </div>
                </div>
            `).join('');
        }
        
        // Load data on page load
        loadDashboardData();
        
        // Auto-refresh every 5 minutes
        setInterval(loadDashboardData, 5 * 60 * 1000);
    </script>
</body>
</html>'''
    
    with open('templates/ai_crypto_dashboard.html', 'w') as f:
        f.write(html_template)
    
    # Create the AI Crypto Search page template
    search_html_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Crypto Search</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 40px 20px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 40px;
            color: white;
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }
        
        .back-link {
            display: inline-block;
            margin-bottom: 30px;
            color: white;
            text-decoration: none;
            padding: 10px 20px;
            background: rgba(255,255,255,0.2);
            border-radius: 10px;
            transition: background 0.2s;
        }
        
        .back-link:hover {
            background: rgba(255,255,255,0.3);
        }
        
        .search-container {
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
        
        .search-box {
            display: flex;
            margin-bottom: 30px;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        .search-box input {
            flex: 1;
            padding: 20px 25px;
            border: none;
            font-size: 1.2rem;
            background: #f8f9fa;
        }
        
        .search-box input:focus {
            outline: none;
            background: white;
        }
        
        .search-box button {
            padding: 20px 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            font-size: 1.2rem;
            cursor: pointer;
            transition: transform 0.2s;
        }
        
        .search-box button:hover {
            transform: scale(1.05);
        }
        
        .results-container {
            min-height: 300px;
        }
        
        .result-item {
            background: #f8f9fa;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            border-left: 4px solid #667eea;
            transition: all 0.2s;
        }
        
        .result-item:hover {
            background: #e9ecef;
            transform: translateX(5px);
        }
        
        .result-title {
            font-size: 1.2rem;
            font-weight: 600;
            color: #333;
            margin-bottom: 8px;
        }
        
        .result-title a {
            color: #667eea;
            text-decoration: none;
        }
        
        .result-title a:hover {
            text-decoration: underline;
        }
        
        .result-meta {
            font-size: 0.9rem;
            color: #666;
            margin-bottom: 8px;
        }
        
        .result-description {
            color: #555;
            line-height: 1.5;
            font-size: 0.95rem;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
            font-size: 1.1rem;
        }
        
        .no-results {
            text-align: center;
            padding: 40px;
            color: #666;
        }
        
        .no-results h3 {
            margin-bottom: 10px;
            color: #333;
        }
    </style>
</head>
<body>
    <div class="container">
        <a href="/" class="back-link">← Back to Dashboard</a>
        
        <div class="header">
            <h1>🔍 AI Crypto Search</h1>
            <p>Search for AI crypto projects and videos</p>
        </div>
        
        <div class="search-container">
            <div class="search-box">
                <input type="text" id="searchInput" placeholder="Search for AI crypto projects, tokens, or topics..." />
                <button id="searchBtn">🔍 Search</button>
            </div>
            
            <div class="results-container" id="resultsContainer">
                <div class="loading" id="loadingState" style="display: none;">
                    🔍 Searching...
                </div>
                <div class="no-results" id="noResults" style="display: none;">
                    <h3>No results found</h3>
                    <p>Try searching for different terms.</p>
                </div>
                <div id="searchResults"></div>
            </div>
        </div>
    </div>
    
    <script>
        document.getElementById('searchBtn').addEventListener('click', performSearch);
        document.getElementById('searchInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                performSearch();
            }
        });
        
        async function performSearch() {
            const query = document.getElementById('searchInput').value.trim();
            
            if (!query) {
                alert('Please enter a search term');
                return;
            }
            
            // Show loading state
            document.getElementById('loadingState').style.display = 'block';
            document.getElementById('searchResults').innerHTML = '';
            document.getElementById('noResults').style.display = 'none';
            
            try {
                const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
                const data = await response.json();
                
                if (data.status === 'error') {
                    throw new Error(data.message);
                }
                
                displayResults(data.results);
                
            } catch (error) {
                console.error('Search error:', error);
                document.getElementById('searchResults').innerHTML = `
                    <div class="result-item">
                        <div class="result-title">Search Error</div>
                        <div class="result-description">Failed to search: ${error.message}</div>
                    </div>
                `;
            } finally {
                document.getElementById('loadingState').style.display = 'none';
            }
        }
        
        function displayResults(results) {
            const container = document.getElementById('searchResults');
            const noResults = document.getElementById('noResults');
            
            if (results.length === 0) {
                container.innerHTML = '';
                noResults.style.display = 'block';
                return;
            }
            
            noResults.style.display = 'none';
            
            container.innerHTML = results.map(result => {
                let link = '#';
                let linkText = result.title;
                
                if (result.type === 'video') {
                    link = result.video_url;
                    linkText = `📺 ${result.title}`;
                } else if (result.type === 'news') {
                    link = result.url;
                    linkText = `📰 ${result.title}`;
                } else if (result.type === 'project') {
                    link = `#${result.symbol}`;
                    linkText = `💰 ${result.title}`;
                }
                
                return `
                    <div class="result-item">
                        <div class="result-title">
                            <a href="${link}" target="_blank">${linkText}</a>
                        </div>
                        <div class="result-meta">
                            ${result.type.toUpperCase()} • ${result.relevance} relevance
                        </div>
                        <div class="result-description">
                            ${result.description || 'No description available.'}
                        </div>
                    </div>
                `;
            }).join('');
        }
    </script>
</body>
</html>'''
    
    with open('templates/ai_crypto_search.html', 'w') as f:
        f.write(search_html_template)
    
    # Create the full dashboard template with all features
    full_dashboard_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Crypto Dashboard - Full View</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            min-height: 100vh;
            color: #333;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 40px;
            color: white;
        }
        
        .header h1 {
            font-size: 3rem;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .header p {
            font-size: 1.2rem;
            opacity: 0.9;
        }
        
        .back-link {
            display: inline-block;
            margin-bottom: 30px;
            color: white;
            text-decoration: none;
            padding: 12px 24px;
            background: rgba(255,255,255,0.2);
            border-radius: 25px;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        }
        
        .back-link:hover {
            background: rgba(255,255,255,0.3);
            transform: translateY(-2px);
        }
        
        .content-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
            margin-top: 30px;
        }
        
        .panel {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .panel h2 {
            font-size: 1.5rem;
            margin-bottom: 20px;
            color: #333;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .video-item {
            display: flex;
            gap: 15px;
            padding: 15px;
            margin-bottom: 15px;
            background: #f8f9fa;
            border-radius: 12px;
            transition: all 0.3s ease;
        }
        
        .video-item:hover {
            background: #e9ecef;
            transform: translateX(5px);
        }
        
        .video-thumbnail {
            flex-shrink: 0;
            width: 120px;
            height: 90px;
        }
        
        .video-thumbnail img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            border-radius: 8px;
        }
        
        .video-info {
            flex: 1;
        }
        
        .video-title {
            font-weight: 600;
            margin-bottom: 5px;
        }
        
        .video-title a {
            color: #667eea;
            text-decoration: none;
        }
        
        .video-title a:hover {
            text-decoration: underline;
        }
        
        .video-meta {
            font-size: 0.9rem;
            color: #666;
            margin-bottom: 5px;
        }
        
        .video-description {
            font-size: 0.85rem;
            color: #888;
            line-height: 1.4;
        }
        
        .tier-badge {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 500;
            margin-left: 10px;
        }
        
        .tier-tier-1 { background: #d4edda; color: #155724; }
        .tier-tier-2 { background: #fff3cd; color: #856404; }
        .tier-tier-3 { background: #f8d7da; color: #721c24; }
        
        .market-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 20px;
            margin-top: 15px;
        }
        
        .stat-item {
            text-align: center;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 12px;
            color: white;
        }
        
        .stat-label {
            font-size: 0.9rem;
            opacity: 0.9;
            margin-bottom: 8px;
        }
        
        .stat-value {
            font-size: 1.8rem;
            font-weight: bold;
        }
        
        .project-list {
            margin-top: 15px;
        }
        
        .project-item {
            display: flex;
            align-items: center;
            padding: 15px;
            margin-bottom: 10px;
            background: #f8f9fa;
            border-radius: 10px;
            border-left: 4px solid #007bff;
        }
        
        .project-rank {
            width: 30px;
            height: 30px;
            background: #007bff;
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            margin-right: 15px;
        }
        
        .project-info {
            flex: 1;
        }
        
        .project-name {
            font-weight: 600;
            color: #333;
        }
        
        .project-price {
            font-size: 0.9rem;
            color: #666;
            margin-top: 2px;
        }
        
        .project-change {
            font-weight: bold;
            padding: 4px 8px;
            border-radius: 6px;
        }
        
        .project-change.positive {
            background: #d4edda;
            color: #155724;
        }
        
        .topic-list {
            margin-top: 15px;
        }
        
        .topic-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px;
            margin-bottom: 8px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #28a745;
        }
        
        .topic-tag {
            font-weight: 600;
            color: #007bff;
        }
        
        .topic-count {
            font-size: 0.9rem;
            color: #666;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
            font-size: 1.1rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <a href="/" class="back-link">← Back to Main Search</a>
        
        <div class="header">
            <h1>📊 AI Crypto Dashboard</h1>
            <p>Complete overview of AI cryptocurrency projects and market data</p>
        </div>
        
        <div class="content-grid">
            <div class="panel">
                <h2>📺 Latest AI Crypto YouTube Videos</h2>
                <div id="recentVideos">
                    <div class="loading">Loading latest AI crypto videos...</div>
                </div>
            </div>
            
            <div class="panel">
                <h2>📊 AI Crypto Market Overview</h2>
                <div id="marketOverview">
                    <div class="market-stats">
                        <div class="stat-item">
                            <div class="stat-label">Total AI Crypto Projects</div>
                            <div class="stat-value">10</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Total Market Cap</div>
                            <div class="stat-value">$15.2B</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">24h Volume</div>
                            <div class="stat-value">$2.1B</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="panel">
                <h2>🏆 Top AI Crypto Projects</h2>
                <div id="topProjects">
                    <div class="project-list">
                        <div class="project-item">
                            <div class="project-rank">1</div>
                            <div class="project-info">
                                <div class="project-name">Bittensor (TAO)</div>
                                <div class="project-price">$400.06</div>
                            </div>
                            <div class="project-change positive">+38.61%</div>
                        </div>
                        <div class="project-item">
                            <div class="project-rank">2</div>
                            <div class="project-info">
                                <div class="project-name">NEAR Protocol (NEAR)</div>
                                <div class="project-price">$2.16</div>
                            </div>
                            <div class="project-change positive">+3.10%</div>
                        </div>
                        <div class="project-item">
                            <div class="project-rank">3</div>
                            <div class="project-info">
                                <div class="project-name">Story Protocol (IP)</div>
                                <div class="project-price">$5.40</div>
                            </div>
                            <div class="project-change positive">+1.41%</div>
                        </div>
                        <div class="project-item">
                            <div class="project-rank">4</div>
                            <div class="project-info">
                                <div class="project-name">Internet Computer (ICP)</div>
                                <div class="project-price">$3.02</div>
                            </div>
                            <div class="project-change positive">+2.20%</div>
                        </div>
                        <div class="project-item">
                            <div class="project-rank">5</div>
                            <div class="project-info">
                                <div class="project-name">Render (RENDER)</div>
                                <div class="project-price">$2.45</div>
                            </div>
                            <div class="project-change positive">+5.77%</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="panel">
                <h2>📈 Trending AI Crypto Topics</h2>
                <div id="trendingTopics">
                    <div class="topic-list">
                        <div class="topic-item">
                            <span class="topic-tag">#Bittensor</span>
                            <span class="topic-count">1.2K mentions</span>
                        </div>
                        <div class="topic-item">
                            <span class="topic-tag">#AITraining</span>
                            <span class="topic-count">856 mentions</span>
                        </div>
                        <div class="topic-item">
                            <span class="topic-tag">#NEARProtocol</span>
                            <span class="topic-count">743 mentions</span>
                        </div>
                        <div class="topic-item">
                            <span class="topic-tag">#RenderNetwork</span>
                            <span class="topic-count">621 mentions</span>
                        </div>
                        <div class="topic-item">
                            <span class="topic-tag">#AICrypto</span>
                            <span class="topic-count">2.1K mentions</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        async function loadDashboardData() {
            try {
                const response = await fetch('/api/dashboard');
                const data = await response.json();
                
                if (data.recent_videos) {
                    updateRecentVideos(data.recent_videos);
                }
            } catch (error) {
                console.error('Error loading dashboard data:', error);
            }
        }
        
        function updateRecentVideos(videos) {
            const container = document.getElementById('recentVideos');
            if (!videos || videos.length === 0) {
                container.innerHTML = '<div class="loading">No videos available</div>';
                return;
            }
            
            container.innerHTML = videos.map(video => `
                <div class="video-item">
                    <div class="video-thumbnail">
                        <a href="${video.video_url}" target="_blank">
                            <img src="${video.thumbnail || 'https://img.youtube.com/vi/' + video.video_id + '/mqdefault.jpg'}" 
                                 alt="${video.title}" 
                                 onerror="this.src='https://img.youtube.com/vi/${video.video_id}/mqdefault.jpg'">
                        </a>
                    </div>
                    <div class="video-info">
                        <div class="video-title">
                            <a href="${video.video_url}" target="_blank" class="video-link">${video.title}</a>
                            <span class="tier-badge tier-${video.tier.toLowerCase().replace(' ', '-')}">${video.tier}</span>
                        </div>
                        <div class="video-meta">
                            📺 ${video.channel} • ⏰ ${video.time_ago}
                        </div>
                        ${video.description ? `<div class="video-description">${video.description}</div>` : ''}
                    </div>
                </div>
            `).join('');
        }
        
        // Load data on page load
        loadDashboardData();
        
        // Auto-refresh every 5 minutes
        setInterval(loadDashboardData, 5 * 60 * 1000);
    </script>
</body>
</html>'''
    
    with open('templates/full_dashboard.html', 'w') as f:
        f.write(full_dashboard_template)
    
    print("🚀 Starting AI Crypto Dashboard...")
    print("📊 Dashboard will be available at: http://localhost:5001")
    print("⏹️  Press Ctrl+C to stop")
    
    app.run(host='0.0.0.0', port=5001, debug=True)
