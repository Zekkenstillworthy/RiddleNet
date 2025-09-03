#!/usr/bin/env python3
"""
Database HTML Content Inspector
Inspects the database for HTML content in text fields and identifies redundant HTML tags
"""

import sqlite3
import re
import os
from html.parser import HTMLParser
from collections import defaultdict

class HTMLTagParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.current_tag_content = []
        
    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        
    def handle_endtag(self, tag):
        pass
        
    def handle_data(self, data):
        # Store text content to check if it's meaningful
        self.current_tag_content.append(data.strip())

def inspect_database():
    """Inspect the database for HTML content"""
    db_path = 'instance/riddlenet.db'
    
    if not os.path.exists(db_path):
        print("❌ Database not found!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Define tables and columns that may contain HTML content
        tables_to_check = {
            'lessons': ['content', 'description'],
            'modules': ['content', 'description'], 
            'class_assignments': ['description', 'instructions'],
            'class_materials': ['description'],
            'class_announcements': ['content'],
            'simulations': ['description', 'tutorial_content'],
            'troubleshooting': ['description'],
            'tutorial_steps': ['content'],
            'question': ['question', 'answer', 'explanation'],
            'essay_response': ['question_text', 'response_text', 'feedback']
        }
        
        html_findings = defaultdict(list)
        total_records_checked = 0
        
        print("🔍 Inspecting database for HTML content...")
        print("=" * 60)
        
        for table_name, columns in tables_to_check.items():
            try:
                # Check if table exists
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
                if not cursor.fetchone():
                    print(f"⚠️ Table {table_name} not found, skipping...")
                    continue
                
                print(f"\n📋 Checking table: {table_name}")
                
                for column in columns:
                    # Check if column exists
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    table_columns = [row[1] for row in cursor.fetchall()]
                    
                    if column not in table_columns:
                        print(f"   ⚠️ Column {column} not found in {table_name}")
                        continue
                    
                    # Get records with non-null content
                    cursor.execute(f"SELECT id, {column} FROM {table_name} WHERE {column} IS NOT NULL AND {column} != ''")
                    records = cursor.fetchall()
                    
                    for record_id, content in records:
                        total_records_checked += 1
                        
                        if content and isinstance(content, str):
                            # Check for HTML tags
                            html_tags = re.findall(r'<[^>]+>', content)
                            
                            if html_tags:
                                # Parse HTML to identify tag types
                                parser = HTMLTagParser()
                                try:
                                    parser.feed(content)
                                    
                                    # Categorize tags
                                    important_tags = ['img', 'video', 'audio', 'iframe', 'object', 'embed', 'source']
                                    formatting_tags = ['p', 'div', 'span', 'strong', 'em', 'b', 'i', 'u']
                                    structural_tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li']
                                    redundant_tags = ['html', 'body', 'head', 'meta', 'title', 'style', 'script']
                                    
                                    found_important = any(tag in parser.tags for tag in important_tags)
                                    found_formatting = any(tag in parser.tags for tag in formatting_tags)
                                    found_structural = any(tag in parser.tags for tag in structural_tags) 
                                    found_redundant = any(tag in parser.tags for tag in redundant_tags)
                                    
                                    # Get text content without HTML
                                    text_content = re.sub(r'<[^>]+>', '', content).strip()
                                    
                                    html_findings[table_name].append({
                                        'id': record_id,
                                        'column': column,
                                        'content_length': len(content),
                                        'text_length': len(text_content),
                                        'html_tags': list(set(parser.tags)),
                                        'has_important_tags': found_important,
                                        'has_formatting_tags': found_formatting,
                                        'has_structural_tags': found_structural,
                                        'has_redundant_tags': found_redundant,
                                        'sample_content': content[:200] + '...' if len(content) > 200 else content
                                    })
                                    
                                except Exception as e:
                                    print(f"   ❌ Error parsing HTML in {table_name}.{column} record {record_id}: {e}")
                    
                    if records:
                        html_count = len([r for r in records if r[1] and '<' in str(r[1])])
                        print(f"   📊 {column}: {len(records)} total records, {html_count} with HTML")
                
            except Exception as e:
                print(f"❌ Error checking table {table_name}: {e}")
        
        # Generate report
        print("\n" + "=" * 60)
        print("📊 HTML CONTENT ANALYSIS REPORT")
        print("=" * 60)
        
        if not html_findings:
            print("✅ No HTML content found in database!")
            return
        
        total_html_records = sum(len(records) for records in html_findings.values())
        print(f"📈 Total records checked: {total_records_checked}")
        print(f"📈 Records with HTML content: {total_html_records}")
        
        for table_name, records in html_findings.items():
            print(f"\n📋 {table_name.upper()}:")
            
            for record in records:
                print(f"   🔍 ID {record['id']} ({record['column']}):")
                print(f"      📏 Content length: {record['content_length']} chars")
                print(f"      📝 Text length: {record['text_length']} chars")
                print(f"      🏷️ HTML tags: {', '.join(record['html_tags'])}")
                
                if record['has_important_tags']:
                    print(f"      ✅ Has important tags (media content)")
                if record['has_redundant_tags']:
                    print(f"      ⚠️ Has redundant tags (candidate for cleanup)")
                if record['has_formatting_tags'] and not record['has_important_tags']:
                    print(f"      🔄 Has only formatting tags (potential cleanup)")
                
                print(f"      📄 Sample: {record['sample_content'][:100]}...")
                print()
        
        # Summary recommendations
        print("\n" + "=" * 60)
        print("💡 CLEANUP RECOMMENDATIONS")
        print("=" * 60)
        
        cleanup_candidates = []
        preserve_candidates = []
        
        for table_name, records in html_findings.items():
            for record in records:
                if record['has_important_tags']:
                    preserve_candidates.append(f"{table_name}.{record['column']} (ID: {record['id']})")
                elif record['has_redundant_tags'] or (record['has_formatting_tags'] and not record['has_structural_tags']):
                    cleanup_candidates.append(f"{table_name}.{record['column']} (ID: {record['id']})")
        
        print(f"🛡️ PRESERVE (contains media/important content): {len(preserve_candidates)} records")
        for item in preserve_candidates[:5]:  # Show first 5
            print(f"   - {item}")
        if len(preserve_candidates) > 5:
            print(f"   ... and {len(preserve_candidates) - 5} more")
        
        print(f"\n🧹 CLEANUP CANDIDATES (redundant HTML): {len(cleanup_candidates)} records")
        for item in cleanup_candidates[:5]:  # Show first 5
            print(f"   - {item}")
        if len(cleanup_candidates) > 5:
            print(f"   ... and {len(cleanup_candidates) - 5} more")
        
    except Exception as e:
        print(f"❌ Error inspecting database: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    inspect_database()