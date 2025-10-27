#!/usr/bin/env python3
"""
Automated script to rename Admin to Instructor throughout the codebase.
This handles Python files, templates, and configuration files.

Run this after executing the SQL migration script.
"""

import os
import re
from pathlib import Path

# Directories to process
BASE_DIR = Path(__file__).parent.parent
DIRECTORIES_TO_PROCESS = [
    BASE_DIR / 'admin',
    BASE_DIR / 'user',
    BASE_DIR / 'utils',
    BASE_DIR / 'services',
    BASE_DIR / 'templates',
    BASE_DIR / 'socket_events.py',
    BASE_DIR / 'socket_manager.py',
    BASE_DIR / 'run.py',
]

# Files to skip
SKIP_FILES = {
    'rename_admin_to_instructor.py',
    'rename_admin_to_instructor.sql',
    '__pycache__',
    '.pyc',
    '.git',
}

# Replacement patterns (order matters!)
REPLACEMENTS = [
    # Model class names
    (r'\bAdminUser\b', 'InstructorUser'),
    (r'\bAdminPasswordReset\b', 'InstructorPasswordReset'),
    (r'\bAdminScore\b', 'InstructorScore'),
    (r'\bclass Admin\(', 'class Instructor('),
    (r'from admin\.models\.user import Admin\b', 'from admin.models.user import Instructor'),
    (r'from admin\.models\.user import AdminUser', 'from admin.models.user import InstructorUser'),
    (r'from admin\.models\.user import Admin,', 'from admin.models.user import Instructor,'),
    (r'from admin\.models\.user import AdminPasswordReset', 'from admin.models.user import InstructorPasswordReset'),
    
    # Table names
    (r"__tablename__ = 'admin_users'", "__tablename__ = 'instructor_users'"),
    (r"__tablename__ = 'admin'", "__tablename__ = 'instructor'"),
    (r"__tablename__ = 'admin_password_resets'", "__tablename__ = 'instructor_password_resets'"),
    
    # Foreign keys
    (r"admin_id", "instructor_id"),
    (r"'admin\.id'", "'instructor.id'"),
    (r'"admin"\.id', '"instructor".id'),
    
    # Session namespace
    (r"auth_namespace == 'admin'", "auth_namespace == 'instructor'"),
    (r"auth_namespace = 'admin'", "auth_namespace = 'instructor'"),
    (r"session\['auth_namespace'\] = 'admin'", "session['auth_namespace'] = 'instructor'"),
    (r'"auth_namespace": "admin"', '"auth_namespace": "instructor"'),
    
    # Routes and URL patterns
    (r"startswith\('/admin'\)", "startswith('/instructor')"),
    (r"startswith\(\"/admin\"\)", "startswith(\"/instructor\")"),
    (r"redirect\('/admin/'\)", "redirect('/instructor/')"),
    (r'redirect\("/admin/"\)', 'redirect("/instructor/")'),
    (r"url_for\('admin\.", "url_for('instructor."),
    (r'/admin/login', '/instructor/login'),
    
    # Comments and strings (be careful with these)
    (r'Admin user', 'Instructor user'),
    (r'admin user', 'instructor user'),
    (r'Admin model', 'Instructor model'),
    (r'admin model', 'instructor model'),
    (r'Admin route', 'Instructor route'),
    (r'admin route', 'instructor route'),
    (r'Admin privileges', 'Instructor privileges'),
    (r'admin privileges', 'instructor privileges'),
    (r'log in as admin', 'log in as instructor'),
    (r'Admin trying to access', 'Instructor trying to access'),
    (r'admin trying to access', 'instructor trying to access'),
    (r'Loaded admin user', 'Loaded instructor user'),
    (r'authenticated admin', 'authenticated instructor'),
    (r'Admin authentication', 'Instructor authentication'),
    (r'admin authentication', 'instructor authentication'),
    (r'Expected Admin', 'Expected Instructor'),
    (r'is_admin', 'is_instructor'),
    (r'is an Admin', 'is an Instructor'),
    
    # Database query patterns
    (r'Admin\.query', 'Instructor.query'),
    (r'isinstance\(.*?, Admin\)', lambda m: m.group(0).replace('Admin', 'Instructor')),
    
    # Template variables and filters
    (r'\{\{ admin\.', '{{ instructor.'),
    (r'\{% if admin', '{% if instructor'),
    (r'\{% for admin', '{% for instructor'),
    (r'admin_name', 'instructor_name'),
    (r'from_admin', 'from_instructor'),
    
    # Function and decorator names
    (r'admin_required', 'instructor_required'),
    (r'enforce_admin_namespace', 'enforce_instructor_namespace'),
    (r'_separate_admin_user_spaces', '_separate_instructor_user_spaces'),
    
    # Role values
    (r"role = 'admin'", "role = 'instructor'"),
    (r'role == "admin"', 'role == "instructor"'),
    (r"default='admin'", "default='instructor'"),
]

# Pattern to preserve (don't replace)
PRESERVE_PATTERNS = [
    r'# admin/',  # Directory references in comments
    r'from admin\.',  # Module imports
    r'import admin\.',
    r'admin/',  # Path references
    r'/admin/',
]

def should_process_file(file_path):
    """Check if file should be processed"""
    # Skip if in skip list
    for skip in SKIP_FILES:
        if skip in str(file_path):
            return False
    
    # Only process Python, HTML, JS, JSON, MD files
    ext = file_path.suffix.lower()
    return ext in ['.py', '.html', '.js', '.json', '.md', '.txt', '.sql']

def is_preserved(text, pos):
    """Check if position is in a preserved context"""
    # Check if we're in a path or module import
    line_start = text.rfind('\n', 0, pos) + 1
    line = text[line_start:text.find('\n', pos)]
    
    for pattern in PRESERVE_PATTERNS:
        if re.search(pattern, line):
            return True
    return False

def process_file(file_path):
    """Process a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes_made = []
        
        # Apply replacements
        for pattern, replacement in REPLACEMENTS:
            if callable(replacement):
                # Handle lambda replacements
                new_content = re.sub(pattern, replacement, content)
            else:
                new_content = re.sub(pattern, replacement, content)
            
            if new_content != content:
                count = len(re.findall(pattern, content))
                changes_made.append(f"{pattern} -> {replacement} ({count} times)")
                content = new_content
        
        # Only write if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[OK] Updated: {file_path.relative_to(BASE_DIR)}")
            for change in changes_made:
                print(f"   - {change}")
            return True
        
        return False
    
    except Exception as e:
        print(f"[ERROR] Error processing {file_path}: {e}")
        return False

def main():
    """Main execution"""
    print("=" * 80)
    print("Admin to Instructor Renaming Script")
    print("=" * 80)
    print()
    
    files_processed = 0
    files_updated = 0
    
    for directory in DIRECTORIES_TO_PROCESS:
        if not directory.exists():
            print(f"[WARNING]  Directory not found: {directory}")
            continue
        
        if directory.is_file():
            # Single file
            if should_process_file(directory):
                files_processed += 1
                if process_file(directory):
                    files_updated += 1
        else:
            # Directory - walk recursively
            for file_path in directory.rglob('*'):
                if file_path.is_file() and should_process_file(file_path):
                    files_processed += 1
                    if process_file(file_path):
                        files_updated += 1
    
    print()
    print("=" * 80)
    print(f"Summary: Processed {files_processed} files, updated {files_updated} files")
    print("=" * 80)
    print()
    print("Next steps:")
    print("1. Run the SQL migration: migrations/rename_admin_to_instructor.sql")
    print("2. Test the application thoroughly")
    print("3. Update any remaining hardcoded references manually")

if __name__ == '__main__':
    main()
