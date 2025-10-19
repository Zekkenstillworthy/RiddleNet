#!/usr/bin/env python3
"""
Update all template path references from 'admin/' to 'instructor/'
"""

import os
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DIRECTORIES_TO_PROCESS = [
    BASE_DIR / 'instructor',
    BASE_DIR / 'user',
    BASE_DIR / 'utils',
    BASE_DIR / 'services',
    BASE_DIR / 'templates',
    BASE_DIR / '__init__.py',
    BASE_DIR / 'application.py',
    BASE_DIR / 'run.py',
]

SKIP_FILES = {
    'update_template_paths.py',
    '__pycache__',
    '.pyc',
    '.git',
}

# Template path patterns to replace
TEMPLATE_PATTERNS = [
    (r"'admin/", "'instructor/"),
    (r'"admin/', '"instructor/'),
    (r'render_template\("admin/', 'render_template("instructor/'),
    (r"render_template\('admin/", "render_template('instructor/"),
]

def should_process_file(file_path):
    """Check if file should be processed"""
    for skip in SKIP_FILES:
        if skip in str(file_path):
            return False
    ext = file_path.suffix.lower()
    return ext in ['.py', '.html', '.js', '.json']

def process_file(file_path):
    """Process a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes = []
        
        for pattern, replacement in TEMPLATE_PATTERNS:
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                count = len(re.findall(pattern, content))
                changes.append(f"{pattern} ({count}x)")
                content = new_content
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ {file_path.relative_to(BASE_DIR)}")
            for change in changes:
                print(f"   {change}")
            return True
        return False
    
    except Exception as e:
        print(f"❌ Error: {file_path}: {e}")
        return False

def main():
    """Main execution"""
    print("=" * 80)
    print("Updating template paths from 'admin/' to 'instructor/'")
    print("=" * 80)
    print()
    
    files_updated = 0
    
    for directory in DIRECTORIES_TO_PROCESS:
        if not directory.exists():
            continue
        
        if directory.is_file():
            if should_process_file(directory):
                if process_file(directory):
                    files_updated += 1
        else:
            for file_path in directory.rglob('*'):
                if file_path.is_file() and should_process_file(file_path):
                    if process_file(file_path):
                        files_updated += 1
    
    print()
    print("=" * 80)
    print(f"Updated {files_updated} files")
    print("=" * 80)

if __name__ == '__main__':
    main()
