#!/usr/bin/env python3
"""
Database HTML Cleanup Script
Removes redundant HTML tags while preserving important media content
"""

import sqlite3
import re
import os
from html.parser import HTMLParser
from datetime import datetime

class HTMLTagParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.important_content = []
        
    def handle_starttag(self, tag, attrs):
        self.tags.append(tag.lower())
        # Preserve important tags with their attributes
        if tag.lower() in ['img', 'video', 'audio', 'iframe', 'object', 'embed', 'source']:
            attr_str = ' '.join([f'{k}="{v}"' for k, v in attrs])
            if attr_str:
                self.important_content.append(f'<{tag} {attr_str}>')
            else:
                self.important_content.append(f'<{tag}>')
                
    def handle_endtag(self, tag):
        if tag.lower() in ['img', 'video', 'audio', 'iframe', 'object', 'embed', 'source']:
            if tag.lower() not in ['img', 'source']:  # These are self-closing
                self.important_content.append(f'</{tag}>')
        
    def handle_data(self, data):
        if data.strip():
            self.important_content.append(data)

def clean_html_content(content):
    """Clean HTML content while preserving important tags"""
    if not content or not isinstance(content, str):
        return content
    
    # Important tags that should be preserved (media content)
    important_tags = ['img', 'video', 'audio', 'iframe', 'object', 'embed', 'source']
    
    # Check if content has important tags
    has_important_tags = any(f'<{tag}' in content.lower() for tag in important_tags)
    
    if has_important_tags:
        # For content with important tags, parse carefully
        parser = HTMLTagParser()
        try:
            parser.feed(content)
            # If we have important content, preserve it but clean formatting
            if any(tag in parser.tags for tag in important_tags):
                # Extract just the important content and surrounding text
                # Remove only redundant structural tags
                cleaned = content
                # Remove specific redundant wrapper tags but keep media
                redundant_patterns = [
                    r'<div[^>]*class="lesson-content"[^>]*>',
                    r'</div>\s*$',
                    r'^\s*<div[^>]*>\s*',
                ]
                for pattern in redundant_patterns:
                    cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE | re.MULTILINE)
                
                return cleaned.strip()
        except Exception:
            pass
        
        # If parsing failed, return original content (safer)
        return content
    
    # For content without important tags, clean more aggressively
    # Remove all HTML tags and return clean text
    clean_text = re.sub(r'<[^>]+>', '', content)
    # Clean up extra whitespace
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    
    return clean_text

def backup_database():
    """Create a backup of the database before cleanup"""
    db_path = 'instance/riddlenet.db'
    backup_path = f'instance/riddlenet_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
    
    try:
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"✅ Database backed up to: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"❌ Failed to create backup: {e}")
        return None

def cleanup_database():
    """Clean up redundant HTML content in the database"""
    db_path = 'instance/riddlenet.db'
    
    if not os.path.exists(db_path):
        print("❌ Database not found!")
        return False
    
    # Create backup first
    backup_path = backup_database()
    if not backup_path:
        response = input("⚠️ Could not create backup. Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("❌ Operation cancelled.")
            return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Define tables and columns to clean
        tables_to_clean = {
            'lessons': ['content', 'description'],
            'simulations': ['description'],
            'class_assignments': ['description', 'instructions'],
            'class_materials': ['description'],
            'essay_response': ['feedback'],
            'tutorial_steps': ['content']
        }
        
        total_cleaned = 0
        total_preserved = 0
        
        print("🧹 Starting database HTML cleanup...")
        print("=" * 60)
        
        for table_name, columns in tables_to_clean.items():
            try:
                # Check if table exists
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
                if not cursor.fetchone():
                    print(f"⚠️ Table {table_name} not found, skipping...")
                    continue
                
                print(f"\n📋 Cleaning table: {table_name}")
                
                for column in columns:
                    # Check if column exists
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    table_columns = [row[1] for row in cursor.fetchall()]
                    
                    if column not in table_columns:
                        print(f"   ⚠️ Column {column} not found in {table_name}")
                        continue
                    
                    # Get records with HTML content
                    cursor.execute(f"SELECT id, {column} FROM {table_name} WHERE {column} IS NOT NULL AND {column} LIKE '%<%'")
                    records = cursor.fetchall()
                    
                    cleaned_count = 0
                    preserved_count = 0
                    
                    for record_id, content in records:
                        if content and isinstance(content, str) and '<' in content:
                            # Check if content has important tags
                            important_tags = ['img', 'video', 'audio', 'iframe', 'object', 'embed', 'source']
                            has_important_tags = any(f'<{tag}' in content.lower() for tag in important_tags)
                            
                            if has_important_tags:
                                print(f"   🛡️ Preserving media content in {table_name}.{column} (ID: {record_id})")
                                preserved_count += 1
                                total_preserved += 1
                                # For media content, only do minimal cleanup
                                cleaned_content = clean_html_content(content)
                                if cleaned_content != content:
                                    cursor.execute(f"UPDATE {table_name} SET {column} = ? WHERE id = ?", 
                                                 (cleaned_content, record_id))
                            else:
                                # Clean redundant HTML
                                cleaned_content = clean_html_content(content)
                                if cleaned_content != content:
                                    cursor.execute(f"UPDATE {table_name} SET {column} = ? WHERE id = ?", 
                                                 (cleaned_content, record_id))
                                    print(f"   🧹 Cleaned {table_name}.{column} (ID: {record_id})")
                                    cleaned_count += 1
                                    total_cleaned += 1
                    
                    if cleaned_count > 0 or preserved_count > 0:
                        print(f"   📊 {column}: {cleaned_count} cleaned, {preserved_count} preserved")
                
            except Exception as e:
                print(f"❌ Error cleaning table {table_name}: {e}")
                continue
        
        # Commit all changes
        conn.commit()
        
        print("\n" + "=" * 60)
        print("✅ CLEANUP COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"📊 Total records cleaned: {total_cleaned}")
        print(f"🛡️ Total records preserved: {total_preserved}")
        
        if backup_path:
            print(f"💾 Backup saved: {backup_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        return False
    finally:
        if conn:
            conn.close()

def verify_cleanup():
    """Verify the cleanup results"""
    print("\n🔍 Verifying cleanup results...")
    
    db_path = 'instance/riddlenet.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    tables_to_check = ['lessons', 'simulations']
    
    for table_name in tables_to_check:
        try:
            cursor.execute(f"SELECT id, content FROM {table_name} WHERE content IS NOT NULL AND content LIKE '%<%' LIMIT 5")
            records = cursor.fetchall()
            
            print(f"\n📋 {table_name.upper()} - Remaining HTML content:")
            
            if not records:
                print("   ✅ No HTML content found (fully cleaned)")
            else:
                for record_id, content in records:
                    # Check if it's important content
                    important_tags = ['img', 'video', 'audio', 'iframe', 'object', 'embed', 'source']
                    has_important_tags = any(f'<{tag}' in content.lower() for tag in important_tags)
                    
                    if has_important_tags:
                        print(f"   🛡️ ID {record_id}: Contains media content (preserved)")
                    else:
                        print(f"   ⚠️ ID {record_id}: Still has HTML tags")
                        print(f"      Sample: {content[:100]}...")
                        
        except Exception as e:
            print(f"   ❌ Error checking {table_name}: {e}")
    
    conn.close()

if __name__ == "__main__":
    print("🧹 DATABASE HTML CLEANUP TOOL")
    print("=" * 60)
    print("This tool will:")
    print("✅ Remove redundant HTML formatting tags")
    print("🛡️ Preserve important media content (images, videos)")
    print("💾 Create a backup before making changes")
    print()
    
    response = input("Do you want to proceed with the cleanup? (y/N): ")
    
    if response.lower() == 'y':
        success = cleanup_database()
        if success:
            verify_cleanup()
    else:
        print("❌ Operation cancelled.")