import sqlite3, os
DB=os.path.join('instance','riddlenet.db')
conn=sqlite3.connect(DB)
cur=conn.cursor()

print("=== Admin Users in System ===")
try:
    # Get admin table structure first
    cols=[r[1] for r in cur.execute("PRAGMA table_info('admin')").fetchall()]
    print(f"Admin table columns: {cols}")
    print()
    
    # List all admins (without passwords for security)
    admins = cur.execute("SELECT id, username, email, role, created_at, last_login FROM admin").fetchall()
    
    if admins:
        print(f"Found {len(admins)} admin users:")
        print("-" * 80)
        for admin in admins:
            admin_id, username, email, role, created_at, last_login = admin
            print(f"ID: {admin_id}")
            print(f"Username: {username}")
            print(f"Email: {email or 'Not set'}")
            print(f"Role: {role or 'admin'}")
            print(f"Created: {created_at or 'Unknown'}")
            print(f"Last Login: {last_login or 'Never'}")
            print("-" * 40)
    else:
        print("No admin users found in the system.")
        
except Exception as e:
    print(f"Error querying admin table: {e}")
    # Try alternative admin_users table
    try:
        print("\nTrying admin_users table...")
        cols=[r[1] for r in cur.execute("PRAGMA table_info('admin_users')").fetchall()]
        print(f"Admin_users table columns: {cols}")
        
        admins = cur.execute("SELECT id, username, email, user_type, created_at, last_active FROM admin_users WHERE is_admin = 1").fetchall()
        
        if admins:
            print(f"Found {len(admins)} admin users in admin_users table:")
            print("-" * 80)
            for admin in admins:
                admin_id, username, email, user_type, created_at, last_active = admin
                print(f"ID: {admin_id}")
                print(f"Username: {username}")
                print(f"Email: {email or 'Not set'}")
                print(f"Type: {user_type}")
                print(f"Created: {created_at or 'Unknown'}")
                print(f"Last Active: {last_active or 'Never'}")
                print("-" * 40)
        else:
            print("No admin users found in admin_users table either.")
            
    except Exception as e2:
        print(f"Error with admin_users table: {e2}")

print("\n=== Security Note ===")
print("Passwords are hashed and not displayed for security reasons.")
print("If you need to reset a password, use the admin panel or create a new admin user.")

conn.close()
