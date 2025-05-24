"""
Fix requirements.txt file to ensure correct packages for OTP email authentication
"""

import os

def fix_requirements():
    """Check and fix requirements.txt file"""
    required_packages = {
        'Flask-Mail': '0.10.0',
        'python-dotenv': '1.0.1',
        'Flask-Login': '0.6.3',
        'qrcode': '8.0'  # For backwards compatibility with TOTP QR codes
    }
    
    # Path to requirements file
    req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    
    # Read current requirements
    try:
        with open(req_path, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"requirements.txt file not found at {req_path}")
        return
    
    # Parse the requirements
    current_packages = {}
    for line in lines:
        line = line.strip()
        if not line or line.startswith('//') or line.startswith('#'):
            continue
        
        try:
            package, version = line.split('==')
            current_packages[package] = version
        except ValueError:
            # Skip lines that don't follow package==version format
            continue
    
    # Check for duplicates and missing packages
    duplicates = []
    missing = []
    for package, version in required_packages.items():
        if package not in current_packages:
            missing.append(f"{package}=={version}")
        elif current_packages.count(package) > 1:
            duplicates.append(package)
    
    # Report findings
    if not missing and not duplicates:
        print("✅ requirements.txt file looks good!")
        return
    
    print("Checking requirements.txt for OTP dependencies...")
    
    if missing:
        print(f"Missing packages: {', '.join(missing)}")
    
    if duplicates:
        print(f"Duplicate packages found: {', '.join(duplicates)}")
    
    # Fix the file if needed
    if missing or duplicates:
        # Add missing packages
        for package in missing:
            lines.append(f"{package}\n")
        
        # Remove duplicate entries, keeping the latest version
        if duplicates:
            new_lines = []
            processed_packages = set()
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('//') or line.startswith('#'):
                    new_lines.append(line + '\n')
                    continue
                
                try:
                    package, _ = line.split('==')
                    if package in processed_packages:
                        # Skip duplicate
                        continue
                    
                    # Override version with required version if in our list
                    if package in required_packages:
                        new_lines.append(f"{package}=={required_packages[package]}\n")
                    else:
                        new_lines.append(line + '\n')
                    
                    processed_packages.add(package)
                except ValueError:
                    # Keep lines that don't follow package==version format
                    new_lines.append(line + '\n')
            
            lines = new_lines
        
        # Write updated requirements
        with open(req_path, 'w') as f:
            f.writelines(lines)
        
        print("✅ requirements.txt has been updated!")

if __name__ == "__main__":
    fix_requirements()
