#!/bin/bash
# Fix Production Live Quiz Responses Table Schema
# This script adds the missing 'answered_at' column and other fields to production

set -e

echo "=================================================="
echo "🔧 PRODUCTION LIVE QUIZ RESPONSES TABLE FIX"
echo "=================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're on the production server
if [ ! -d "/home/ubuntu/RiddleNet" ]; then
    echo -e "${RED}[ERROR] Not on production server (expected /home/ubuntu/RiddleNet)${NC}"
    echo "Please run this script via SSH on your EC2 instance"
    exit 1
fi

cd /home/ubuntu/RiddleNet

echo -e "${YELLOW}📋 Step 1: Backing up database...${NC}"
# Create backup timestamp
BACKUP_TIMESTAMP=$(date +%Y%m%d_%H%M%S)
echo "Backup timestamp: $BACKUP_TIMESTAMP"

# Optional: Create database backup (uncomment if you have pg_dump access)
# pg_dump -h your-db-host -U your-db-user -d your-db-name > backup_$BACKUP_TIMESTAMP.sql

echo ""
echo -e "${YELLOW}📋 Step 2: Checking current schema...${NC}"
python3 << 'EOF'
import sys
sys.path.insert(0, '/home/ubuntu/RiddleNet')
from __init__ import create_app, db
from sqlalchemy import inspect

app = create_app()
with app.app_context():
    inspector = inspect(db.engine)
    
    if 'live_quiz_responses' not in inspector.get_table_names():
        print("[ERROR] live_quiz_responses table does not exist!")
        sys.exit(1)
    
    columns = {col['name'] for col in inspector.get_columns('live_quiz_responses')}
    
    print("\n📊 Current columns in live_quiz_responses:")
    for col in sorted(columns):
        print(f"  ✓ {col}")
    
    print("\n🔍 Checking for missing columns:")
    expected = ['answered_at', 'response_time', 'points_awarded', 'question_text', 'correct_answer', 'created_at']
    missing = [col for col in expected if col not in columns]
    
    if missing:
        print(f"\n❌ Missing columns: {', '.join(missing)}")
    else:
        print("\n✅ All expected columns are present!")
        sys.exit(0)
EOF

echo ""
echo -e "${YELLOW}📋 Step 3: Running migration...${NC}"
python3 migrations/011_update_live_quiz_responses_columns.py upgrade

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Migration completed successfully!${NC}"
    
    echo ""
    echo -e "${YELLOW}📋 Step 4: Verifying schema...${NC}"
    python3 << 'EOF'
import sys
sys.path.insert(0, '/home/ubuntu/RiddleNet')
from __init__ import create_app, db
from sqlalchemy import inspect

app = create_app()
with app.app_context():
    inspector = inspect(db.engine)
    columns = {col['name'] for col in inspector.get_columns('live_quiz_responses')}
    
    expected = ['answered_at', 'response_time', 'points_awarded', 'question_text', 'correct_answer', 'created_at']
    missing = [col for col in expected if col not in columns]
    
    if missing:
        print(f"\n❌ Still missing: {', '.join(missing)}")
        sys.exit(1)
    else:
        print("\n✅ All columns verified!")
        print("\n📊 Final schema:")
        for col in sorted(columns):
            print(f"  ✓ {col}")
EOF
    
    echo ""
    echo -e "${YELLOW}📋 Step 5: Restarting application...${NC}"
    sudo systemctl restart riddlenet
    
    echo ""
    echo -e "${GREEN}=================================================="
    echo "✅ PRODUCTION FIX COMPLETED SUCCESSFULLY"
    echo "==================================================${NC}"
    echo ""
    echo "The live_quiz_responses table now has all required columns."
    echo "Live Quiz answer submission should now work correctly."
    echo ""
    
else
    echo ""
    echo -e "${RED}❌ Migration failed!${NC}"
    echo "Please check the error messages above."
    exit 1
fi
