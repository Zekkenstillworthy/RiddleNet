@echo off
REM Production Badge Cleanup Script for Windows
REM Uploads cleanup script to server and executes it

echo 🚀 Starting production badge cleanup...

REM Upload cleanup script to server
echo 📤 Uploading cleanup script...
scp -i riddlenetv1.pem production_badge_cleanup.py ubuntu@54.66.229.118:~/RiddleNet/

REM Create temporary script for remote execution
echo cd ~/RiddleNet > temp_cleanup.sh
echo source venv/bin/activate >> temp_cleanup.sh
echo export FLASK_APP=application.py >> temp_cleanup.sh
echo python3 -c "import sys; sys.path.insert(0, '/home/ubuntu/RiddleNet'); from application import application; application.app_context().push(); from production_badge_cleanup import cleanup_production_badges; cleanup_production_badges()" >> temp_cleanup.sh

REM Upload and run the script
scp -i riddlenetv1.pem temp_cleanup.sh ubuntu@54.66.229.118:~/
ssh -i riddlenetv1.pem ubuntu@54.66.229.118 "bash ~/temp_cleanup.sh"

REM Cleanup
del temp_cleanup.sh

echo ✅ Production badge cleanup finished!
pause
