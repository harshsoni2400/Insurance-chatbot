#!/bin/bash

# NYVO Insurance Advisor Chatbot - Startup Script

echo "🚀 Starting NYVO Insurance Advisor Chatbot..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating from template..."
    cp .env.example .env
    echo "📝 Please edit .env and add your OPENAI_API_KEY"
    exit 1
fi

# Initialize database if needed
if [ ! -f "data/nyvo.db" ]; then
    echo "🗄️  Initializing database with sample data..."
    python scripts/seed_data.py
fi

# Create data directory if it doesn't exist
mkdir -p data

# Start the server
echo "🌐 Starting API server on http://localhost:8000"
echo "📖 API docs available at http://localhost:8000/docs"
echo ""
echo "To use the chatbot:"
echo "1. Open frontend/index.html in your browser"
echo "2. Or serve it: cd frontend && python -m http.server 3000"
echo ""
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
