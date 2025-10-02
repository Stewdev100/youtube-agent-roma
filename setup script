#!/bin/bash

# YouTube Agent Roma - Setup Script

echo "🚀 Setting up YouTube Agent Roma..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p temp
mkdir -p cache

# Set up environment file
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file..."
    cat > .env << EOF
# YouTube Agent Roma - Environment Variables
# Get your API key from: https://console.developers.google.com/

YOUTUBE_API_KEY=your_youtube_api_key_here
EOF
    echo "📝 Please edit .env file and add your YouTube API key"
fi

echo "✅ Setup complete!"
echo ""
echo "To run the application:"
echo "  source venv/bin/activate"
echo "  python app.py --help"
echo ""
echo "Don't forget to:"
echo "  1. Edit .env file and add your YouTube API key"
echo "  2. Configure nodes.yaml if needed"

