#!/bin/bash
# Script to properly restart RiddleNet on production with cache clearing

echo "🔄 Restarting RiddleNet Production Server..."
echo "================================================"

# Navigate to project directory
cd /opt/riddlenet || { echo "❌ Failed to navigate to /opt/riddlenet"; exit 1; }

echo "📦 Clearing Python cache files..."
# Remove all __pycache__ directories and .pyc files
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null
echo "✓ Cache cleared"

echo ""
echo "🔄 Restarting Gunicorn service..."
sudo systemctl restart riddlenet

echo ""
echo "⏳ Waiting for service to start..."
sleep 3

echo ""
echo "📊 Service status:"
sudo systemctl status riddlenet --no-pager -l | head -n 20

echo ""
echo "📝 Recent logs:"
sudo journalctl -u riddlenet --no-pager -n 30 | tail -n 20

echo ""
echo "================================================"
echo "✅ Restart complete!"
echo ""
echo "To monitor logs in real-time, run:"
echo "  sudo journalctl -u riddlenet -f"
