import sqlite3
import os

# Connect to the database
db_path = 'instance/test.db'
print(f"Looking for database at: {db_path}")
print(f"Database exists: {os.path.exists(db_path)}")

if os.path.exists(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current users
        cursor.execute("SELECT id, username, profile_img FROM user")
        users = cursor.fetchall()
        
        print(f"Found {len(users)} users:")
        for user in users:
            print(f"ID: {user[0]}, Username: {user[1]}, Profile Image: {user[2]}")
        
        # Update the user with a profile image (assuming Gilbert is user ID 1)
        # Based on the file list, there's a Gilbert.jpg file
        if users:
            first_user = users[0]
            user_id = first_user[0]
            username = first_user[1]
            
            # Check if there's an image file matching the username
            possible_images = ['Gilbert.jpg', 'Me.jpg', 'gill.jpg']
            image_to_use = None
            
            for img in possible_images:
                img_path = f'static/img/{img}'
                print(f"Checking for image: {img_path} - exists: {os.path.exists(img_path)}")
                if os.path.exists(img_path):
                    image_to_use = img
                    break
            
            if image_to_use:
                print(f"Updating user {username} with profile image: {image_to_use}")
                cursor.execute("UPDATE user SET profile_img = ? WHERE id = ?", (image_to_use, user_id))
                conn.commit()
                print(f"Successfully updated user {username} with profile image: {image_to_use}")
                
                # Verify the update
                cursor.execute("SELECT id, username, profile_img FROM user WHERE id = ?", (user_id,))
                updated_user = cursor.fetchone()
                print(f"Verification - ID: {updated_user[0]}, Username: {updated_user[1]}, Profile Image: {updated_user[2]}")
            else:
                print("No suitable profile image found")
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"Database not found at {db_path}")
