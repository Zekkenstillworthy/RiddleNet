import re

# Read the file
with open('templates/admin/troubleshooting/edit_simulation.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and remove the large network functions block
# Remove from 'window.saveNetworkConfiguration' to just before the CLI functions
pattern = r'window\.saveNetworkConfiguration = function\(\) \{.*?(?=\s*// CLI Editor functions)'
new_content = re.sub(pattern, '', content, flags=re.DOTALL)

# Write back to file
with open('templates/admin/troubleshooting/edit_simulation.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('Successfully removed network configuration functions')