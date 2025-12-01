#!/bin/bash
# Run script untuk Windows Git Bash

echo "🕌 Kitab Imam Mazhab RAG AI"
echo "=========================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/Scripts/activate

# Check if dependencies are installed
if [ ! -f "venv/Scripts/flask" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Creating .env from template..."
    cp .env.example .env
    echo "⚠️ Please edit .env file with your API keys!"
    exit 1
fi

# Run the application
echo ""
echo "Starting server..."
echo "Press Ctrl+C to stop"
echo ""

python app.py
