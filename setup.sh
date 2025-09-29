#!/bin/bash

# Iron Doom Jarvis Setup Script
# This script helps set up the bot for first-time use

echo "🤖 Iron Doom Jarvis Setup Script"
echo "================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3.8+ from https://python.org"
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not installed."
    exit 1
fi

echo "✅ pip found: $(pip3 --version)"

# Create virtual environment
echo ""
echo "📦 Setting up virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate || {
    echo "❌ Failed to activate virtual environment"
    exit 1
}

echo "✅ Virtual environment activated"

# Upgrade pip
echo ""
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "📚 Installing dependencies..."
pip install -r requirements.txt

echo "✅ Dependencies installed"

# Create .env file from template
if [ ! -f .env ]; then
    echo ""
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env file and add your API keys!"
    echo "   Required keys:"
    echo "   - DISCORD_TOKEN"
    echo "   - PRIMARY_CHANNEL_ID"
    echo "   Optional but recommended:"
    echo "   - NOTION_TOKEN"
    echo "   - YOUTUBE_API_KEY"
    echo "   - GOOGLE_BOOKS_API_KEY"
    echo "   - NEWS_API_KEY"
    echo "   - GITHUB_TOKEN"
else
    echo "✅ .env file already exists"
fi

# Create data directories
echo ""
echo "📁 Creating data directories..."
mkdir -p data logs
echo "✅ Data directories created"

# Initialize data files
echo ""
echo "🗃️ Initializing data files..."
python3 -c "
from utils.helpers import setup_config
setup_config()
print('✅ Data files initialized')
"

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Run: python3 iron_doom_jarvis.py"
echo ""
echo "For Docker deployment:"
echo "1. docker-compose up -d"
echo ""
echo "Need help? Check the README.md file!"
echo ""