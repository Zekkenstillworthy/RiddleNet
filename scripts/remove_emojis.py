"""
Remove emoji characters from Python files to fix Windows console encoding issues
"""

import os
import re

# Emoji mapping to ASCII equivalents
EMOJI_REPLACEMENTS = {
    # Cookies and authentication
    '[COOKIE]': '[COOKIE]',
    '[AUTH]': '[AUTH]',
    '[SHIELD]': '[SHIELD]',
    '[LOCK]': '[LOCK]',
    
    # Status indicators
    '[OK]': '[OK]',
    '[ERROR]': '[ERROR]',
    '[WARNING]': '[WARNING]',
    '[OK]': '[OK]',
    '[SKIP]': '[SKIP]',
    '[FAIL]': '[FAIL]',
    
    # Tools and configuration
    '[FIX]': '[FIX]',
    '[KEY]': '[KEY]',
    
    # Search and debugging
    '[DEBUG]': '[DEBUG]',
    '[USER]': '[USER]',
    '[PIN]': '[PIN]',
    '[PUZZLE]': '[PUZZLE]',
    
    # Notifications
    '[NOTIF]': '[NOTIF]',
    '[DATA]': '[DATA]',
    '[NOTE]': '[NOTE]',
    '[USERS]': '[USERS]',
    '[MSG]': '[MSG]',
}

def remove_emojis_from_file(filepath):
    """Remove emojis from a single file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes_made = 0
        
        # Replace each emoji
        for emoji, replacement in EMOJI_REPLACEMENTS.items():
            if emoji in content:
                count = content.count(emoji)
                content = content.replace(emoji, replacement)
                changes_made += count
                print(f"  - Replaced {count} occurrences of {emoji} with {replacement}")
        
        # Save if changes were made
        if changes_made > 0:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Updated {filepath} ({changes_made} changes)")
            return changes_made
        
        return 0
        
    except Exception as e:
        print(f"✗ Error processing {filepath}: {e}")
        return 0

def scan_directory(root_dir):
    """Scan directory for Python files and remove emojis"""
    total_files_processed = 0
    total_changes = 0
    
    # Skip these directories
    skip_dirs = {'__pycache__', '.git', 'node_modules', 'venv', '.venv', 'archive'}
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Remove skip directories from traversal
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]
        
        # Process Python files
        for filename in filenames:
            if filename.endswith('.py'):
                filepath = os.path.join(dirpath, filename)
                changes = remove_emojis_from_file(filepath)
                if changes > 0:
                    total_files_processed += 1
                    total_changes += changes
    
    return total_files_processed, total_changes

if __name__ == '__main__':
    # Get project root (parent of scripts directory)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    print(f"Scanning Python files in: {project_root}")
    print("-" * 60)
    
    files_processed, total_changes = scan_directory(project_root)
    
    print("-" * 60)
    print(f"\nSummary:")
    print(f"  Files modified: {files_processed}")
    print(f"  Total replacements: {total_changes}")
    print("\nServer should now start without Unicode encoding errors!")
