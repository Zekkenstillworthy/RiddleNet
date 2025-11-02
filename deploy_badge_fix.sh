#!/bin/bash
# MVP Badge Validation Fix - Production Deployment Script

echo "🚀 Deploying Badge Validation Fix to Production..."
echo "=================================================="

# Navigate to RiddleNet directory
cd ~/RiddleNet || exit 1

# Pull latest changes
echo "📥 Pulling latest changes from main..."
git pull origin main

# Check if pull was successful
if [ $? -eq 0 ]; then
    echo "✅ Code updated successfully"
else
    echo "❌ Failed to pull changes"
    exit 1
fi

# Restart the application using systemd or supervisor
echo "🔄 Restarting RiddleNet application..."

# Option 1: If using systemd
if systemctl is-active --quiet riddlenet; then
    sudo systemctl restart riddlenet
    echo "✅ RiddleNet service restarted (systemd)"
# Option 2: If using supervisor
elif supervisorctl status riddlenet > /dev/null 2>&1; then
    sudo supervisorctl restart riddlenet
    echo "✅ RiddleNet service restarted (supervisor)"
# Option 3: If using gunicorn directly
else
    echo "⚠️ Please restart the application manually"
    echo "   Suggested commands:"
    echo "   - pkill -f 'gunicorn.*run:app'"
    echo "   - gunicorn -c gunicorn.conf.py run:app"
fi

echo ""
echo "✅ Deployment Complete!"
echo "📋 Changes Applied:"
echo "   - Dashboard now validates badges against challenge completion"
echo "   - Only completed challenges show badges in 'Your Achievements'"
echo "   - Badge count now matches actual completed challenges"
echo ""
echo "🧪 Test the fix:"
echo "   1. Login to dashboard"
echo "   2. Verify 'Your Achievements' only shows badges for 100% complete challenges"
echo "   3. Check badge count matches challenge completion count"
