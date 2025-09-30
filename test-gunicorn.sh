#!/bin/bash
# Test script for RiddleNet Gunicorn setup
# Run this to test your application before deployment

echo "🧪 Testing RiddleNet Gunicorn Setup"
echo "==================================="

# Check if required files exist
echo "📋 Checking required files..."
required_files=("wsgi.py" "gunicorn.conf.py" "run.py" "requirements.txt")
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file exists"
    else
        echo "❌ $file missing"
        exit 1
    fi
done

# Check if Docker is available
if command -v docker &> /dev/null; then
    echo "✅ Docker is available"
    
    echo ""
    echo "🐳 Building Docker image for testing..."
    docker build -t riddlenet-test .
    
    echo ""
    echo "🚀 Starting RiddleNet with Gunicorn in Docker..."
    echo "   This will test the production configuration locally"
    echo "   The application will be available at: http://localhost:8000"
    echo ""
    echo "Press Ctrl+C to stop the test server"
    echo ""
    
    docker run --rm -p 8000:8000 --name riddlenet-test riddlenet-test
    
else
    echo "❌ Docker not available. Please install Docker to test the setup."
    echo ""
    echo "Alternative: Test on a Linux system with:"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    echo "  gunicorn --config gunicorn.conf.py wsgi:application"
fi