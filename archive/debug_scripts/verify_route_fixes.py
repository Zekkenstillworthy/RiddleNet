"""
Verification Script for Session and Route Poisoning Fixes

This script helps verify that all route references are correct and 
session isolation is maintained.

Run this script to check for common issues before deployment.
"""

import re
from pathlib import Path

def check_template_routes():
    """Check templates for incorrect route references"""
    print("=" * 70)
    print("CHECKING TEMPLATE ROUTE REFERENCES")
    print("=" * 70)
    
    template_dir = Path('templates')
    issues = []
    
    # Patterns to check
    problematic_patterns = [
        (r"url_for\(['\"]admin\.dashboard['\"]", "admin.dashboard (should be class_controller.index or dashboard.*)"),
        (r"url_for\(['\"]admin\.list_simulations['\"]", "admin.list_simulations (no such endpoint)"),
        (r"redirect\(['\"]\/admin\/classes['\"]", "Hardcoded /admin/classes (should use url_for)"),
    ]
    
    for template_file in template_dir.rglob('*.html'):
        with open(template_file, 'r', encoding='utf-8') as f:
            content = f.read()
            line_number = 0
            for line in content.split('\n'):
                line_number += 1
                for pattern, description in problematic_patterns:
                    if re.search(pattern, line):
                        issues.append({
                            'file': str(template_file),
                            'line': line_number,
                            'issue': description,
                            'content': line.strip()
                        })
    
    if issues:
        print(f"\n❌ Found {len(issues)} potential issues:\n")
        for issue in issues:
            print(f"File: {issue['file']}")
            print(f"Line: {issue['line']}")
            print(f"Issue: {issue['issue']}")
            print(f"Content: {issue['content'][:100]}...")
            print("-" * 70)
    else:
        print("\n✅ No template route issues found!")
    
    return len(issues) == 0

def check_python_hardcoded_redirects():
    """Check Python files for hardcoded redirect paths"""
    print("\n" + "=" * 70)
    print("CHECKING PYTHON FILES FOR HARDCODED REDIRECTS")
    print("=" * 70)
    
    admin_dir = Path('admin')
    issues = []
    
    # Pattern to check
    hardcoded_redirect_pattern = r"redirect\(['\"]\/admin\/[^'\"]+['\"]"
    
    for py_file in admin_dir.rglob('*.py'):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                line_number = 0
                for line in content.split('\n'):
                    line_number += 1
                    if re.search(hardcoded_redirect_pattern, line) and 'url_for' not in line:
                        issues.append({
                            'file': str(py_file),
                            'line': line_number,
                            'content': line.strip()
                        })
        except (UnicodeDecodeError, PermissionError):
            # Skip files that can't be read (e.g., binary files, __pycache__)
            continue
    
    if issues:
        print(f"\n❌ Found {len(issues)} hardcoded redirects:\n")
        for issue in issues:
            print(f"File: {issue['file']}")
            print(f"Line: {issue['line']}")
            print(f"Content: {issue['content'][:100]}...")
            print("-" * 70)
    else:
        print("\n✅ No hardcoded redirect paths found!")
    
    return len(issues) == 0

def check_session_namespace_protection():
    """Check if critical admin routes have session namespace protection"""
    print("\n" + "=" * 70)
    print("CHECKING SESSION NAMESPACE PROTECTION")
    print("=" * 70)
    
    # Routes that should have protection
    critical_routes = [
        'admin/controllers/user_controller.py',
    ]
    
    protection_pattern = r"session\.get\(['\"]auth_namespace['\"]"
    
    results = []
    for route_file in critical_routes:
        file_path = Path(route_file)
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                has_protection = bool(re.search(protection_pattern, content))
                results.append({
                    'file': str(file_path),
                    'protected': has_protection
                })
        else:
            results.append({
                'file': str(file_path),
                'protected': False,
                'error': 'File not found'
            })
    
    all_protected = all(r['protected'] for r in results)
    
    for result in results:
        status = "✅" if result.get('protected') else "❌"
        print(f"{status} {result['file']}")
        if 'error' in result:
            print(f"   Error: {result['error']}")
    
    if all_protected:
        print("\n✅ All critical routes have session namespace protection!")
    else:
        print("\n❌ Some routes are missing session namespace protection!")
    
    return all_protected

def check_blueprint_registrations():
    """Verify blueprint names match usage in templates"""
    print("\n" + "=" * 70)
    print("CHECKING BLUEPRINT REGISTRATIONS")
    print("=" * 70)
    
    # Expected blueprints based on fixes
    expected_blueprints = {
        'class_controller': 'admin/controllers/class_controller.py',
        'dashboard': 'admin/controllers/dashboard_controller.py',
        'admin_simulation': 'admin/routes/simulation_routes.py',
        'admin_user': 'admin/controllers/user_controller.py',
    }
    
    found_blueprints = {}
    
    for bp_name, file_path in expected_blueprints.items():
        file_path_obj = Path(file_path)
        if file_path_obj.exists():
            with open(file_path_obj, 'r', encoding='utf-8') as f:
                content = f.read()
                # Look for Blueprint declaration
                pattern = rf"Blueprint\(['\"]({bp_name})['\"]"
                match = re.search(pattern, content)
                found_blueprints[bp_name] = bool(match)
        else:
            found_blueprints[bp_name] = None
    
    all_found = all(v for v in found_blueprints.values() if v is not None)
    
    for bp_name, found in found_blueprints.items():
        if found is None:
            print(f"❌ {bp_name}: File not found")
        elif found:
            print(f"✅ {bp_name}: Registered correctly")
        else:
            print(f"❌ {bp_name}: Not found in file")
    
    if all_found:
        print("\n✅ All expected blueprints are registered!")
    else:
        print("\n❌ Some blueprints are missing or incorrectly registered!")
    
    return all_found

def main():
    """Run all verification checks"""
    print("\n")
    print("*" * 70)
    print("SESSION AND ROUTE POISONING VERIFICATION")
    print("*" * 70)
    print("\n")
    
    results = {
        'template_routes': check_template_routes(),
        'hardcoded_redirects': check_python_hardcoded_redirects(),
        'session_protection': check_session_namespace_protection(),
        'blueprint_registration': check_blueprint_registrations(),
    }
    
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)
    
    total_checks = len(results)
    passed_checks = sum(1 for v in results.values() if v)
    
    for check_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {check_name.replace('_', ' ').title()}")
    
    print("\n" + "=" * 70)
    print(f"Result: {passed_checks}/{total_checks} checks passed")
    print("=" * 70)
    
    if passed_checks == total_checks:
        print("\n🎉 All verifications passed! Safe to deploy.")
        return 0
    else:
        print("\n⚠️  Some checks failed. Please review issues above.")
        return 1

if __name__ == '__main__':
    exit(main())
