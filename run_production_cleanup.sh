#!/bin/bash
# Production Badge Cleanup Script
# Uploads cleanup script to server and executes it

echo "🚀 Starting production badge cleanup..."

# Upload cleanup script to server
echo "📤 Uploading cleanup script..."
scp -i riddlenetv1.pem production_badge_cleanup.py ubuntu@54.66.229.118:~/RiddleNet/

# Connect and run cleanup
echo "🔧 Running cleanup on production server..."
ssh -i riddlenetv1.pem ubuntu@54.66.229.118 << 'ENDSSH'
cd ~/RiddleNet
source venv/bin/activate
export FLASK_APP=application.py

echo "Running Flask shell cleanup..."
python3 << 'ENDPYTHON'
import sys
sys.path.insert(0, '/home/ubuntu/RiddleNet')

from application import application
with application.app_context():
    from production_badge_cleanup import cleanup_production_badges
    cleanup_production_badges()
ENDPYTHON

echo "✅ Cleanup complete!"
ENDSSH

echo "🎉 Production badge cleanup finished!"
