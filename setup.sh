#!/bin/bash
# CrewAI-NutriPlanner Setup Script

echo "🤖 CrewAI-NutriPlanner Setup"
echo "============================"

# Check Python version
python_version=$(python3 --version 2>&1 | grep -o '[0-9]\+\.[0-9]\+')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
    echo "✅ Python $python_version detected (>= 3.8 required)"
else
    echo "❌ Python 3.8+ required. Current version: $python_version"
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Copy environment file
if [ ! -f .env ]; then
    echo "⚙️  Creating environment configuration..."
    cp .env.example .env
    echo "📝 Please edit .env file and add your Google Gemini API key"
    echo "   Get your free API key from: https://makersuite.google.com/app/apikey"
else
    echo "✅ Environment file already exists"
fi

# Validate setup
echo "🧪 Validating setup..."
python scripts/validate_setup.py

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your Google Gemini API key"
echo "2. Run: source venv/bin/activate"
echo "3. Run: python -m src.main"
echo ""
echo "📚 Documentation: https://github.com/Reevsay/CrewAI-NutriPlanner"