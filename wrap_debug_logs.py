"""
Wrap all [DEBUG] console.log statements with if(this.DEBUG_MODE) checks
"""
import re

filepath = 'static/js/collaboration-real-time.js'

with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
i = 0
changes_made = 0

while i < len(lines):
    line = lines[i]
    
    # Check if this is a console.log with [DEBUG] that's NOT already wrapped
    if '[DEBUG]' in line and 'console.' in line:
        # Check if the previous line is already an if(this.DEBUG_MODE) check
        if i > 0 and 'if (this.DEBUG_MODE)' in new_lines[-1]:
            # Already wrapped, just add the line
            new_lines.append(line)
            i += 1
            continue
        
        # Get indentation of current line
        indent_match = re.match(r'^(\s*)', line)
        indent = indent_match.group(1) if indent_match else ''
        
        # Look ahead to see if there are multiple consecutive debug logs
        consecutive_debug_lines = [line]
        j = i + 1
        while j < len(lines) and '[DEBUG]' in lines[j] and 'console.' in lines[j]:
            consecutive_debug_lines.append(lines[j])
            j += 1
        
        # If we found multiple lines, wrap them in a block
        if len(consecutive_debug_lines) > 1:
            new_lines.append(f'{indent}if (this.DEBUG_MODE) {{\n')
            for debug_line in consecutive_debug_lines:
                # Add extra indentation
                new_lines.append('    ' + debug_line)
            new_lines.append(f'{indent}}}\n')
            changes_made += len(consecutive_debug_lines)
            i = j
        else:
            # Single line - wrap inline
            # Extract the console.log statement
            console_match = re.search(r'(console\.(log|error|warn)\(.*?\);?)\s*$', line)
            if console_match:
                console_stmt = console_match.group(1)
                # Remove the console statement from the line and add wrapped version
                new_lines.append(f'{indent}if (this.DEBUG_MODE) {{ {console_stmt} }}\n')
                changes_made += 1
                i += 1
            else:
                new_lines.append(line)
                i += 1
    else:
        new_lines.append(line)
        i += 1

# Write back
with open(filepath, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f'✅ Wrapped {changes_made} debug console.log statements')
