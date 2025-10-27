#!/usr/bin/env python3
"""
Migration script to add collaboration_settings column to simulations table
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from __init__ import create_app, db
from sqlalchemy import text

def add_collaboration_settings_column():
    """Add collaboration_settings JSON column to simulations table"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if column already exists
            with db.engine.connect() as connection:
                result = connection.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='simulations' AND column_name='collaboration_settings';
                """))
                
                if result.fetchone():
                    print("[OK] collaboration_settings column already exists")
                    return True
                
                # Add the column
                connection.execute(text("""
                    ALTER TABLE simulations 
                    ADD COLUMN collaboration_settings JSON DEFAULT '{}';
                """))
                
                connection.commit()
            
            print("[OK] Successfully added collaboration_settings column to simulations table")
            return True
            
        except Exception as e:
            print(f"[ERROR] Error adding collaboration_settings column: {str(e)}")
            return False

if __name__ == "__main__":
    success = add_collaboration_settings_column()
    sys.exit(0 if success else 1)