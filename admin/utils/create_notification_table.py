"""
Database migration script for notification history table
Run this to create the notification_history table
"""

import os
import sys
import sqlite3
from datetime import datetime

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_notification_history_table():
    """Create the notification_history table"""
    
    # Database path
    db_path = os.path.join('instance', 'test.db')
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create notification_history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notification_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_id INTEGER NOT NULL,
                sender_type VARCHAR(20) NOT NULL,
                sender_username VARCHAR(100) NOT NULL,
                notification_type VARCHAR(50) NOT NULL,
                title VARCHAR(200) NOT NULL,
                message TEXT NOT NULL,
                priority VARCHAR(20) NOT NULL,
                recipient_type VARCHAR(20) NOT NULL,
                recipient_count INTEGER DEFAULT 0,
                specific_user_id INTEGER,
                delivery_channel VARCHAR(20) NOT NULL,
                email_sent INTEGER DEFAULT 0,
                websocket_sent INTEGER DEFAULT 0,
                failed_deliveries INTEGER DEFAULT 0,
                status VARCHAR(20) DEFAULT 'sent',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                delivery_time REAL,
                template_data TEXT,
                error_details TEXT
            )
        """)
        
        # Create indexes for better performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_notification_history_created_at ON notification_history(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_notification_history_sender_id ON notification_history(sender_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_notification_history_type ON notification_history(notification_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_notification_history_priority ON notification_history(priority)")
        
        # Commit changes
        conn.commit()
        
        print("✅ notification_history table created successfully!")
        
        # Insert sample data for testing
        sample_data = [
            (1, 'admin', 'admin', 'system_update', 'System Maintenance Scheduled', 
             'Maintenance window scheduled for tonight 11 PM - 1 AM EST', 'high', 
             'all_users', 15, None, 'both', 10, 15, 0, 'sent', 
             datetime.now().isoformat(), 2.5, '{}', None),
            (1, 'admin', 'admin', 'security_alert', 'Security Update Applied', 
             'New security patches have been applied to the platform', 'normal', 
             'all_users', 15, None, 'websocket', 0, 15, 0, 'sent', 
             datetime.now().isoformat(), 1.2, '{}', None),
            (1, 'admin', 'admin', 'course_update', 'New Course Available', 
             'Advanced Network Security course is now available', 'normal', 
             'all_users', 15, None, 'both', 12, 15, 3, 'partial', 
             datetime.now().isoformat(), 3.1, '{}', 'Failed to send to 3 users')
        ]
        
        cursor.executemany("""
            INSERT INTO notification_history 
            (sender_id, sender_type, sender_username, notification_type, title, message, 
             priority, recipient_type, recipient_count, specific_user_id, delivery_channel, 
             email_sent, websocket_sent, failed_deliveries, status, created_at, 
             delivery_time, template_data, error_details)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_data)
        
        conn.commit()
        print("✅ Sample notification data inserted!")
        
        # Close connection
        conn.close()
        
    except Exception as e:
        print(f"❌ Error creating notification_history table: {e}")
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    create_notification_history_table()
