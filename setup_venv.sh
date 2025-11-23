#!/bin/bash
# Quick setup script for emergency alert system

echo "🚀 Setting up virtual environment..."

# Remove old venv if exists
rm -rf venv

# Create new venv with system python3
python3 -m venv venv

# Activate venv
source venv/bin/activate

echo "📦 Installing dependencies..."

# Install packages
pip install --upgrade pip
pip install flask==3.0.0
pip install flask-cors==4.0.0
pip install openai-whisper
pip install torch
pip install google-generativeai

echo "✅ Setup complete!"
echo ""
echo "To run the server:"
echo "  source venv/bin/activate"
echo "  python integrated_server.py"
