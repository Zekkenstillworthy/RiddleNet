import os
import glob

templates_dir = r'c:\Users\gilbe\OneDrive\Desktop\RiddleNet - Copy (2) - Copy\templates'
bad_files = []

for file in glob.glob(os.path.join(templates_dir, '**/*.html'), recursive=True):
    try:
        with open(file, 'r', encoding='utf-8') as f:
            f.read()
    except UnicodeDecodeError as e:
        bad_files.append((file, str(e)))

print('Files with encoding issues:')
if bad_files:
    for f, e in bad_files:
        print(f'{f}:\n  {e}\n')
else:
    print('✅ No encoding issues found in template files')
