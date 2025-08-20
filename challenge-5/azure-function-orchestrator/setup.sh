#!/bin/bash
# Local development setup script for Insurance Claim Orchestrator

echo "🚀 Setting up Insurance Claim Orchestrator for local development..."

# Check Python version
echo "🐍 Checking Python version..."
python_version=$(python --version 2>&1)
if [[ $python_version == *"3.9"* ]] || [[ $python_version == *"3.10"* ]] || [[ $python_version == *"3.11"* ]]; then
    echo "✅ Python version compatible: $python_version"
else
    echo "❌ Python 3.9+ required. Current: $python_version"
    exit 1
fi

# Check if Functions Core Tools is installed
echo "⚡ Checking Azure Functions Core Tools..."
if command -v func &> /dev/null; then
    func_version=$(func --version)
    echo "✅ Functions Core Tools installed: $func_version"
else
    echo "❌ Azure Functions Core Tools not found. Please install it first:"
    echo "   npm install -g azure-functions-core-tools@4 --unsafe-perm true"
    exit 1
fi

# Create virtual environment
echo "🌍 Creating Python virtual environment..."
python -m venv venv

# Activate virtual environment
echo "🔄 Activating virtual environment..."
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Check if local.settings.json exists
echo "⚙️ Checking configuration..."
if [ ! -f "local.settings.json" ]; then
    echo "⚠️ local.settings.json not found. Creating template..."
    cp local.settings.json.template local.settings.json 2>/dev/null || echo "Please create local.settings.json from the template in README.md"
fi

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Update local.settings.json with your Azure credentials"
echo "2. Start the function: func start"
echo "3. Test health endpoint: curl http://localhost:7071/api/health"
echo ""
echo "🔗 Local endpoints:"
echo "   Health Check: http://localhost:7071/api/health"
echo "   Claim Processing: http://localhost:7071/api/claim"
echo "   Cosmos Test: http://localhost:7071/api/test-cosmos"
echo ""
echo "🎉 Ready for development!"
