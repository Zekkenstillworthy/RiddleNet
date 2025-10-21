file_path = r'c:\Users\gilbe\OneDrive\Desktop\RiddleNet - Copy (2) - Copy\templates\user\crimping-simulation.html'

# Read the file as binary
with open(file_path, 'rb') as f:
    content = f.read()

# Replace common Windows-1252 characters with UTF-8 equivalents
replacements = {
    bytes([0x91]): '''.encode('utf-8'),  # Left single quote
    bytes([0x92]): '''.encode('utf-8'),  # Right single quote
    bytes([0x93]): '"'.encode('utf-8'),  # Left double quote
    bytes([0x94]): '"'.encode('utf-8'),  # Right double quote
    bytes([0x95]): '•'.encode('utf-8'),  # Bullet
    bytes([0x96]): '–'.encode('utf-8'),  # En dash
    bytes([0x97]): '—'.encode('utf-8'),  # Em dash
    bytes([0x85]): '…'.encode('utf-8'),  # Ellipsis
}

fixed = content
count = 0
for bad_char, good_char in replacements.items():
    occurrences = fixed.count(bad_char)
    if occurrences > 0:
        print(f'Replacing {occurrences} occurrences of byte {hex(bad_char[0])}')
        fixed = fixed.replace(bad_char, good_char)
        count += occurrences

# Write the fixed content back
with open(file_path, 'wb') as f:
    f.write(fixed)

print(f'\n✅ Fixed {count} total invalid characters in crimping-simulation.html')
