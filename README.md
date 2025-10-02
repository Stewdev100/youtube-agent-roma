# YouTube Agent Roma

An AI-powered YouTube content analysis and processing agent with a beautiful web interface.

## 🌟 Features

- **Real YouTube Search**: Search and discover YouTube videos with rich metadata
- **Beautiful Web UI**: Modern, responsive frontend interface
- **REST API**: Full-featured API with FastAPI
- **Multiple Audiences**: Support for beginners, intermediate, advanced users
- **Real-time Results**: Fast search with loading animations
- **Video Details**: Titles, channels, URLs, descriptions, publish dates

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/youtube-agent-roma.git
cd youtube-agent-roma
```

### 2. Set Up Environment
```bash
# Copy environment template
cp env.template .env

# Edit .env file and add your YouTube API key
# Get your API key from: https://console.developers.google.com/
```

### 3. Install Dependencies
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Get YouTube API Key
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable **YouTube Data API v3**
4. Create an **API Key** in Credentials
5. Add the key to your `.env` file

### 5. Run the Application
```bash
# Start the server
uvicorn app:app --reload --port 5050

# Open your browser to: http://localhost:5050
```

## Usage

### Running the main application:
```bash
python app.py
```

### Running specific operations:
```bash
python agents/yt_bundle/executors.py --operation search --query "python tutorial"
python agents/yt_bundle/executors.py --operation analyze
python agents/yt_bundle/executors.py --operation process
```

## Configuration

Edit `nodes.yaml` to configure:
- YouTube API settings
- Agent node parameters
- Logging preferences
- Security settings

## Project Structure

```
youtube-agent-roma/
├── app.py                 # Main application entry point
├── requirements.txt       # Python dependencies
├── nodes.yaml            # Configuration file
├── agents/               # Agent modules
│   ├── __init__.py
│   └── yt_bundle/        # YouTube bundle
│       ├── __init__.py
│       └── executors.py  # Main execution logic
└── prompts/              # Prompt templates
    └── sample_prompt.txt
```

## Development

The project is structured to be easily extensible. You can:
- Add new agent nodes in the `agents/` directory
- Create custom prompts in the `prompts/` directory
- Modify configuration in `nodes.yaml`

## License

See LICENSE file for details.
