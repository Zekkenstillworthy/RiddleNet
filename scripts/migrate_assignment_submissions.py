#!/usr/bin/env python3
"""
Migration script to add assignment submission system
Adds submission settings to assignments and creates submission tables
"""

import sqlite3
import os
from datetime import datetime

def run_migration():
    db_path = 'instance/riddlenet.db'
    if not os.path.exists(db_path):
        print("❌ Database not found!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🚀 Starting assignment submission migration...")
        
        # 1. Add submission settings columns to class_assignments table
        print("📋 Adding submission settings to class_assignments...")
        
        submission_columns = [
            ('allow_file_uploads', 'BOOLEAN DEFAULT 1'),
            ('allowed_file_types', 'VARCHAR(500) DEFAULT "pdf,doc,docx,txt,jpg,png,zip"'),
            ('max_file_size_mb', 'INTEGER DEFAULT 10'),
            ('max_files', 'INTEGER DEFAULT 5'),
            ('allow_text_submission', 'BOOLEAN DEFAULT 1'),
            ('allow_late_submissions', 'BOOLEAN DEFAULT 1'),
            ('late_penalty_per_day', 'REAL DEFAULT 10.0'),
            ('allow_resubmission', 'BOOLEAN DEFAULT 1')
        ]
        
        # Check which columns already exist
        cursor.execute("PRAGMA table_info(class_assignments)")
        existing_columns = [row[1] for row in cursor.fetchall()]
        
        for column_name, column_def in submission_columns:
            if column_name not in existing_columns:
                try:
                    cursor.execute(f"ALTER TABLE class_assignments ADD COLUMN {column_name} {column_def}")
                    print(f"   ✅ Added {column_name}")
                except Exception as e:
                    print(f"   ⚠️  {column_name}: {e}")
            else:
                print(f"   📋 {column_name} already exists")
        
        # 2. Create assignment_submissions table
        print("📋 Creating assignment_submissions table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS assignment_submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                assignment_id INTEGER NOT NULL,
                student_id INTEGER NOT NULL,
                submission_text TEXT,
                submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(20) DEFAULT 'submitted',
                grade REAL,
                max_points INTEGER,
                feedback TEXT,
                graded_at DATETIME,
                graded_by INTEGER,
                is_late BOOLEAN DEFAULT 0,
                late_penalty_applied REAL DEFAULT 0.0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (assignment_id) REFERENCES class_assignments (id),
                FOREIGN KEY (student_id) REFERENCES users (id),
                FOREIGN KEY (graded_by) REFERENCES admin_users (id)
            )
        ''')
        print("   ✅ assignment_submissions table created")
        
        # 3. Create submission_attachments table
        print("📋 Creating submission_attachments table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS submission_attachments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                submission_id INTEGER NOT NULL,
                original_filename VARCHAR(255) NOT NULL,
                stored_filename VARCHAR(255) NOT NULL,
                file_path VARCHAR(500) NOT NULL,
                file_size INTEGER NOT NULL,
                mime_type VARCHAR(100) NOT NULL,
                is_valid BOOLEAN DEFAULT 1,
                validation_error VARCHAR(255),
                uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (submission_id) REFERENCES assignment_submissions (id)
            )
        ''')
        print("   ✅ submission_attachments table created")
        
        # 4. Create assignment_submission_history table
        print("📋 Creating assignment_submission_history table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS assignment_submission_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                submission_id INTEGER NOT NULL,
                action VARCHAR(50) NOT NULL,
                old_grade REAL,
                new_grade REAL,
                old_status VARCHAR(20),
                new_status VARCHAR(20),
                changed_by INTEGER NOT NULL,
                changed_by_type VARCHAR(10) NOT NULL,
                notes TEXT,
                changed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (submission_id) REFERENCES assignment_submissions (id)
            )
        ''')
        print("   ✅ assignment_submission_history table created")
        
        # 5. Create indexes for better performance
        print("📋 Creating indexes...")
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_submissions_assignment ON assignment_submissions(assignment_id)",
            "CREATE INDEX IF NOT EXISTS idx_submissions_student ON assignment_submissions(student_id)",
            "CREATE INDEX IF NOT EXISTS idx_submissions_status ON assignment_submissions(status)",
            "CREATE INDEX IF NOT EXISTS idx_attachments_submission ON submission_attachments(submission_id)",
            "CREATE INDEX IF NOT EXISTS idx_history_submission ON assignment_submission_history(submission_id)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        print("   ✅ Indexes created")
        
        # 6. Create uploads directory structure
        print("📋 Creating upload directories...")
        upload_dirs = [
            'static/uploads/assignments',
            'static/uploads/assignments/submissions'
        ]
        
        for directory in upload_dirs:
            os.makedirs(directory, exist_ok=True)
            print(f"   ✅ Created {directory}")
        
        # Commit all changes
        conn.commit()
        print("✅ Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        if 'conn' in locals():
            conn.rollback()
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    success = run_migration()
    if success:
        print("🎉 Assignment submission system is ready!")
    else:
        print("💥 Migration failed. Please check the errors above.")