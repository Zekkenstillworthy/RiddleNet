file_path = r'c:\Users\gilbe\OneDrive\Desktop\RiddleNet - Copy (2) - Copy\templates\user\crimping-simulation.html'

# Read the file with Windows-1252 encoding and write as UTF-8
try:
    with open(file_path, 'r', encoding='windows-1252') as f:
        content = f.read()
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print('✅ Successfully converted crimping-simulation.html from Windows-1252 to UTF-8')
    
    # Verify it's now valid UTF-8
    with open(file_path, 'r', encoding='utf-8') as f:
        f.read()
    print('✅ Verified: File is now valid UTF-8')
    
except Exception as e:
    print(f'❌ Error: {e}')
