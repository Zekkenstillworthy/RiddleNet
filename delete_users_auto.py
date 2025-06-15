#!/usr/bin/env python3
"""
Script to safely delete user data for Zekken4 and Zekken2
"""

import sqlite3
import os

def delete_user_data():
    # Connect to the database
    db_path = os.path.join('instance', 'test.db')
    
    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Users to delete
        users_to_delete = ['Zekken4', 'Zekken2']
        user_ids_to_delete = [2, 3]  # Based on the table data shown
        
        print("Starting user data deletion...")
        
        # Delete from tables that reference user_id
        # Order matters due to foreign key constraints
        
        # 1. Delete from networking_progress
        for user_id in user_ids_to_delete:
            cursor.execute("DELETE FROM networking_progress WHERE user_id = ?", (user_id,))
            rows_affected = cursor.rowcount
            print(f"Deleted {rows_affected} networking_progress records for user_id {user_id}")
        
        # 2. Delete from networking2_progress  
        for user_id in user_ids_to_delete:
            cursor.execute("DELETE FROM networking2_progress WHERE user_id = ?", (user_id,))
            rows_affected = cursor.rowcount
            print(f"Deleted {rows_affected} networking2_progress records for user_id {user_id}")
        
        # 3. Delete from topic_progress
        for user_id in user_ids_to_delete:
            cursor.execute("DELETE FROM topic_progress WHERE user_id = ?", (user_id,))
            rows_affected = cursor.rowcount
            print(f"Deleted {rows_affected} topic_progress records for user_id {user_id}")
        
        # 4. Delete from troubleshooting_progress
        for user_id in user_ids_to_delete:
            cursor.execute("DELETE FROM troubleshooting_progress WHERE user_id = ?", (user_id,))
            rows_affected = cursor.rowcount
            print(f"Deleted {rows_affected} troubleshooting_progress records for user_id {user_id}")
        
        # 5. Delete from topology_progress
        for user_id in user_ids_to_delete:
            cursor.execute("DELETE FROM topology_progress WHERE user_id = ?", (user_id,))
            rows_affected = cursor.rowcount
            print(f"Deleted {rows_affected} topology_progress records for user_id {user_id}")
        
        # 6. Delete from essay_response
        for user_id in user_ids_to_delete:
            cursor.execute("DELETE FROM essay_response WHERE user_id = ?", (user_id,))
            rows_affected = cursor.rowcount
            print(f"Deleted {rows_affected} essay_response records for user_id {user_id}")
        
        # 7. Delete from essay_responses
        for user_id in user_ids_to_delete:
            cursor.execute("DELETE FROM essay_responses WHERE user_id = ?", (user_id,))
            rows_affected = cursor.rowcount
            print(f"Deleted {rows_affected} essay_responses records for user_id {user_id}")
        
        # 8. Delete from essay
        for user_id in user_ids_to_delete:
            cursor.execute("DELETE FROM essay WHERE user_id = ?", (user_id,))
            rows_affected = cursor.rowcount
            print(f"Deleted {rows_affected} essay records for user_id {user_id}")
        
        # 9. Delete from score
        for user_id in user_ids_to_delete:
            cursor.execute("DELETE FROM score WHERE user_id = ?", (user_id,))
            rows_affected = cursor.rowcount
            print(f"Deleted {rows_affected} score records for user_id {user_id}")
        
        # 10. Delete from activity_log
        for user_id in user_ids_to_delete:
            cursor.execute("DELETE FROM activity_log WHERE user_id = ?", (user_id,))
            rows_affected = cursor.rowcount
            print(f"Deleted {rows_affected} activity_log records for user_id {user_id}")
        
        # 11. Delete from activity_logs
        for user_id in user_ids_to_delete:
            cursor.execute("DELETE FROM activity_logs WHERE user_id = ?", (user_id,))
            rows_affected = cursor.rowcount
            print(f"Deleted {rows_affected} activity_logs records for user_id {user_id}")
        
        # 12. Delete from class_students
        for user_id in user_ids_to_delete:
            cursor.execute("DELETE FROM class_students WHERE user_id = ?", (user_id,))
            rows_affected = cursor.rowcount
            print(f"Deleted {rows_affected} class_students records for user_id {user_id}")
        
        # 13. Delete from user_classes
        for user_id in user_ids_to_delete:
            cursor.execute("DELETE FROM user_classes WHERE user_id = ?", (user_id,))
            rows_affected = cursor.rowcount
            print(f"Deleted {rows_affected} user_classes records for user_id {user_id}")
        
        # 14. Finally, delete from the main user table
        for user_id in user_ids_to_delete:
            cursor.execute("DELETE FROM user WHERE id = ?", (user_id,))
            rows_affected = cursor.rowcount
            print(f"Deleted {rows_affected} user record for user_id {user_id}")
        
        # 15. Also check and delete from users table (if different from user table)
        for user_id in user_ids_to_delete:
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            rows_affected = cursor.rowcount
            print(f"Deleted {rows_affected} users record for user_id {user_id}")
        
        # Commit all changes
        conn.commit()
        print("\n✓ All user data deleted successfully!")
        
        # Verify deletion
        print("\nVerifying deletion...")
        cursor.execute("SELECT id, username FROM user WHERE id IN (2, 3)")
        remaining_users = cursor.fetchall()
        
        if remaining_users:
            print(f"Warning: Some users still exist: {remaining_users}")
        else:
            print("✓ All specified users have been successfully deleted from the user table")
        
        cursor.execute("SELECT id, username FROM users WHERE id IN (2, 3)")
        remaining_users_alt = cursor.fetchall()
        
        if remaining_users_alt:
            print(f"Warning: Some users still exist in users table: {remaining_users_alt}")
        else:
            print("✓ All specified users have been successfully deleted from the users table")
    
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        conn.rollback()
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        conn.rollback()
    
    finally:
        conn.close()

if __name__ == "__main__":
    print("Deleting user data for Zekken4 and Zekken2...")
    delete_user_data()
