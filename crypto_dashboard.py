#!/usr/bin/env python3
"""
Crypto Dashboard - Real-time cryptocurrency market data and YouTube content integration
"""

import os
import sys
import asyncio
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
import json

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    import requests
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse, HTMLResponse
    from pydantic import BaseModel
    from loguru import logger
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please ensure all dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)

# Crypto data models
class CryptoPriceRequest(BaseModel):
    symbols: List[str] = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "SOLUSDT", "BNBUSDT"]
    market_type: Optional[str] = "spot"

class CryptoFeedRequest(BaseModel):
    category: Optional[str] = "trending"  # trending, gainers, losers, volume
    limit: Optional[int] = 20

class CryptoAnalysisRequest(BaseModel):
    symbol: str
    timeframe: Optional[str] = "24h"
    analysis_type: Optional[str] = "technical"  # technical, fundamental, sentiment

class CryptoResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class CryptoDashboard:
    """Crypto dashboard with real-time market data and YouTube integration"""
    
    def __init__(self):
        self.binance_base_url = "https://api.binance.com/api/v3"
        self.coingecko_base_url = "https://api.coingecko.com/api/v3"
        self.cache = {}
        self.cache_ttl = 60  # 1 minute cache
        
    async def get_crypto_prices(self, symbols: List[str], market_type: str = "spot") -> Dict[str, Any]:
        """Get real-time crypto prices from Binance"""
        try:
            # Convert symbols to Binance format
            binance_symbols = [s.upper() for s in symbols]
            
            # Check cache first
            cache_key = f"prices_{market_type}_{'_'.join(binance_symbols)}"
            if cache_key in self.cache:
                cached_data, timestamp = self.cache[cache_key]
                if time.time() - timestamp < self.cache_ttl:
                    return cached_data
            
            # Fetch from Binance API
            url = f"{self.binance_base_url}/ticker/24hr"
            params = {"symbols": json.dumps(binance_symbols)}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Process and format data
                processed_data = []
                for item in data:
                    processed_data.append({
                        "symbol": item["symbol"],
                        "price": float(item["lastPrice"]),
                        "change_24h": float(item["priceChange"]),
                        "change_24h_pct": float(item["priceChangePercent"]),
                        "volume": float(item["volume"]),
                        "high_24h": float(item["highPrice"]),
                        "low_24h": float(item["lowPrice"]),
                        "market_cap_rank": None,  # Will be filled from CoinGecko
                        "trend": "bullish" if float(item["priceChangePercent"]) > 0 else "bearish"
                    })
                
                # Cache the result
                self.cache[cache_key] = (processed_data, time.time())
                
                return {
                    "success": True,
                    "data": processed_data,
                    "market_type": market_type,
                    "fetched_at": int(time.time()),
                    "count": len(processed_data)
                }
            else:
                return {
                    "success": False,
                    "error": f"Binance API error: {response.status_code}",
                    "data": []
                }
                
        except Exception as e:
            logger.error(f"Error fetching crypto prices: {e}")
            return {
                "success": False,
                "error": str(e),
                "data": []
            }
    
    async def get_crypto_feed(self, category: str = "trending", limit: int = 20) -> Dict[str, Any]:
        """Get crypto market feed with trending/gainers/losers"""
        try:
            # Check cache first
            cache_key = f"feed_{category}_{limit}"
            if cache_key in self.cache:
                cached_data, timestamp = self.cache[cache_key]
                if time.time() - timestamp < self.cache_ttl:
                    return cached_data
            
            # Get market data from CoinGecko
            if category == "trending":
                url = f"{self.coingecko_base_url}/search/trending"
            elif category == "gainers":
                url = f"{self.coingecko_base_url}/coins/markets"
                params = {"vs_currency": "usd", "order": "price_change_percentage_24h_desc", "per_page": limit}
            elif category == "losers":
                url = f"{self.coingecko_base_url}/coins/markets"
                params = {"vs_currency": "usd", "order": "price_change_percentage_24h_asc", "per_page": limit}
            elif category == "volume":
                url = f"{self.coingecko_base_url}/coins/markets"
                params = {"vs_currency": "usd", "order": "volume_desc", "per_page": limit}
            else:
                url = f"{self.coingecko_base_url}/coins/markets"
                params = {"vs_currency": "usd", "order": "market_cap_desc", "per_page": limit}
            
            if category != "trending":
                response = requests.get(url, params=params, timeout=10)
            else:
                response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Process trending data
                if category == "trending":
                    coins = data.get("coins", [])
                    processed_data = []
                    for coin in coins[:limit]:
                        coin_data = coin.get("item", {})
                        processed_data.append({
                            "id": coin_data.get("id"),
                            "name": coin_data.get("name"),
                            "symbol": coin_data.get("symbol", "").upper(),
                            "market_cap_rank": coin_data.get("market_cap_rank"),
                            "thumb": coin_data.get("thumb"),
                            "price_change_percentage_24h": None,
                            "current_price": None,
                            "market_cap": None,
                            "total_volume": None
                        })
                else:
                    # Process market data
                    processed_data = []
                    for coin in data[:limit]:
                        processed_data.append({
                            "id": coin.get("id"),
                            "name": coin.get("name"),
                            "symbol": coin.get("symbol", "").upper(),
                            "market_cap_rank": coin.get("market_cap_rank"),
                            "thumb": coin.get("image"),
                            "price_change_percentage_24h": coin.get("price_change_percentage_24h"),
                            "current_price": coin.get("current_price"),
                            "market_cap": coin.get("market_cap"),
                            "total_volume": coin.get("total_volume")
                        })
                
                # Cache the result
                self.cache[cache_key] = (processed_data, time.time())
                
                return {
                    "success": True,
                    "data": processed_data,
                    "category": category,
                    "limit": limit,
                    "fetched_at": int(time.time()),
                    "count": len(processed_data)
                }
            else:
                return {
                    "success": False,
                    "error": f"CoinGecko API error: {response.status_code}",
                    "data": []
                }
                
        except Exception as e:
            logger.error(f"Error fetching crypto feed: {e}")
            return {
                "success": False,
                "error": str(e),
                "data": []
            }
    
    async def get_crypto_analysis(self, symbol: str, timeframe: str = "24h", analysis_type: str = "technical") -> Dict[str, Any]:
        """Get detailed crypto analysis"""
        try:
            # Get price data
            price_data = await self.get_crypto_prices([symbol])
            
            if not price_data["success"]:
                return price_data
            
            if not price_data["data"]:
                return {
                    "success": False,
                    "error": f"No data found for symbol {symbol}",
                    "data": {}
                }
            
            coin_data = price_data["data"][0]
            
            # Basic technical analysis
            analysis = {
                "symbol": symbol,
                "current_price": coin_data["price"],
                "change_24h": coin_data["change_24h"],
                "change_24h_pct": coin_data["change_24h_pct"],
                "volume": coin_data["volume"],
                "high_24h": coin_data["high_24h"],
                "low_24h": coin_data["low_24h"],
                "trend": coin_data["trend"],
                "analysis_type": analysis_type,
                "timeframe": timeframe,
                "technical_indicators": {
                    "rsi_signal": "overbought" if coin_data["change_24h_pct"] > 10 else "oversold" if coin_data["change_24h_pct"] < -10 else "neutral",
                    "volume_trend": "high" if coin_data["volume"] > 1000000 else "moderate" if coin_data["volume"] > 100000 else "low",
                    "price_position": "near_high" if coin_data["price"] > coin_data["high_24h"] * 0.95 else "near_low" if coin_data["price"] < coin_data["low_24h"] * 1.05 else "middle"
                },
                "recommendation": self._generate_recommendation(coin_data),
                "youtube_topics": self._generate_youtube_topics(symbol, coin_data)
            }
            
            return {
                "success": True,
                "data": analysis,
                "fetched_at": int(time.time())
            }
            
        except Exception as e:
            logger.error(f"Error in crypto analysis: {e}")
            return {
                "success": False,
                "error": str(e),
                "data": {}
            }
    
    def _generate_recommendation(self, coin_data: Dict[str, Any]) -> str:
        """Generate trading recommendation based on data"""
        change_pct = coin_data["change_24h_pct"]
        volume = coin_data["volume"]
        
        if change_pct > 5 and volume > 1000000:
            return "Strong buy signal - High volume with significant price increase"
        elif change_pct > 2:
            return "Buy signal - Positive momentum"
        elif change_pct < -5 and volume > 1000000:
            return "Strong sell signal - High volume with significant price decrease"
        elif change_pct < -2:
            return "Sell signal - Negative momentum"
        else:
            return "Hold - Sideways movement"
    
    def _generate_youtube_topics(self, symbol: str, coin_data: Dict[str, Any]) -> List[str]:
        """Generate YouTube search topics based on crypto data"""
        topics = []
        
        # Basic topics
        topics.append(f"{symbol} price analysis")
        topics.append(f"{symbol} trading strategy")
        
        # Trend-based topics
        if coin_data["trend"] == "bullish":
            topics.append(f"{symbol} bull run analysis")
            topics.append(f"{symbol} price prediction 2024")
        else:
            topics.append(f"{symbol} bear market analysis")
            topics.append(f"{symbol} support levels")
        
        # Volume-based topics
        if coin_data["volume"] > 1000000:
            topics.append(f"{symbol} high volume trading")
            topics.append(f"{symbol} whale activity")
        
        # Market cap rank topics
        if coin_data.get("market_cap_rank") and coin_data["market_cap_rank"] <= 10:
            topics.append(f"{symbol} top 10 cryptocurrency")
            topics.append(f"{symbol} institutional adoption")
        
        return topics[:5]  # Return top 5 topics

# Initialize crypto dashboard
crypto_dashboard = CryptoDashboard()

# Create FastAPI app for crypto features
crypto_app = FastAPI(
    title="Crypto Dashboard API",
    description="Real-time cryptocurrency market data and analysis",
    version="1.0.0"
)

# Add CORS middleware
crypto_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@crypto_app.get("/")
async def crypto_root():
    """Serve the crypto dashboard page"""
    return FileResponse("static/crypto_dashboard.html")

@crypto_app.get("/health")
async def crypto_health():
    """Health check for crypto dashboard"""
    return {"status": "healthy", "service": "Crypto Dashboard API"}

@crypto_app.post("/prices", response_model=CryptoResponse)
async def get_crypto_prices_endpoint(request: CryptoPriceRequest):
    """Get real-time crypto prices"""
    try:
        result = await crypto_dashboard.get_crypto_prices(
            symbols=request.symbols,
            market_type=request.market_type
        )
        
        return CryptoResponse(
            success=result["success"],
            message="Prices fetched successfully" if result["success"] else "Failed to fetch prices",
            data=result,
            error=result.get("error")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@crypto_app.post("/feed", response_model=CryptoResponse)
async def get_crypto_feed_endpoint(request: CryptoFeedRequest):
    """Get crypto market feed"""
    try:
        result = await crypto_dashboard.get_crypto_feed(
            category=request.category,
            limit=request.limit
        )
        
        return CryptoResponse(
            success=result["success"],
            message="Feed fetched successfully" if result["success"] else "Failed to fetch feed",
            data=result,
            error=result.get("error")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@crypto_app.post("/analysis", response_model=CryptoResponse)
async def get_crypto_analysis_endpoint(request: CryptoAnalysisRequest):
    """Get detailed crypto analysis"""
    try:
        result = await crypto_dashboard.get_crypto_analysis(
            symbol=request.symbol,
            timeframe=request.timeframe,
            analysis_type=request.analysis_type
        )
        
        return CryptoResponse(
            success=result["success"],
            message="Analysis completed successfully" if result["success"] else "Failed to complete analysis",
            data=result,
            error=result.get("error")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(crypto_app, host="0.0.0.0", port=5051, reload=True)
