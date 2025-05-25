#!/usr/bin/env python3
import os
import re

def remove_git_conflicts(file_path):
    """Remove Git conflict markers from a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Pattern to match Git conflict markers and everything between them
        # This removes the HEAD section and keeps the incoming changes
        pattern = r'<<<<<<< HEAD.*?=======\n(.*?)\n>>>>>>> [a-f0-9]+'
        
        # Replace conflicts with just the incoming changes
        new_content = re.sub(pattern, r'\1', content, flags=re.DOTALL)
        
        # Also remove any remaining conflict markers
        new_content = re.sub(r'^<<<<<<< HEAD.*?$', '', new_content, flags=re.MULTILINE)
        new_content = re.sub(r'^=======.*?$', '', new_content, flags=re.MULTILINE)
        new_content = re.sub(r'^>>>>>>> [a-f0-9]+.*?$', '', new_content, flags=re.MULTILINE)
        
        if content != new_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Fixed conflicts in: {file_path}")
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def main():
    """Walk through the directory and fix conflicts in relevant files"""
    extensions = ['.py', '.js', '.css', '.html', '.md']
    
    for root, dirs, files in os.walk('.'):
        # Skip certain directories
        if any(skip in root for skip in ['__pycache__', '.git', 'env', 'venv', '.venv']):
            continue
            
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, file)
                remove_git_conflicts(file_path)

if __name__ == "__main__":
    main()
