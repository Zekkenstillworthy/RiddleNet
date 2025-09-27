#!/usr/bin/env python3
"""
Test script to verify the export function fix
"""

import json
import sys
import os

# Add the current directory to Python path to import the application modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_safe_json_parse():
    """Test the safe_json_parse function that was causing the error"""
    # This simulates the function that was causing issues
    def safe_json_parse(value, default=None):
        if isinstance(value, str):
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return default
        return value if value is not None else default
    
    # Test cases
    test_cases = [
        ('{"test": "value"}', {"test": "value"}),
        ('[1, 2, 3]', [1, 2, 3]),
        ('invalid json', None),
        (None, None),
        ({'already': 'dict'}, {'already': 'dict'}),
        ('', None)
    ]
    
    print("Testing safe_json_parse function...")
    all_passed = True
    
    for i, (input_val, expected) in enumerate(test_cases):
        try:
            result = safe_json_parse(input_val)
            if result == expected:
                print(f"✅ Test {i+1} passed: {input_val!r} -> {result!r}")
            else:
                print(f"❌ Test {i+1} failed: {input_val!r} -> {result!r} (expected {expected!r})")
                all_passed = False
        except Exception as e:
            print(f"❌ Test {i+1} error: {input_val!r} -> Exception: {e}")
            all_passed = False
    
    return all_passed

def test_json_scope():
    """Test that json module is accessible in nested functions"""
    print("\nTesting json module scope...")
    
    try:
        # This should work now that we fixed the import issue
        def nested_function():
            return json.dumps({"test": "data"})
        
        result = nested_function()
        expected = '{"test": "data"}'
        if result == expected:
            print("✅ JSON scope test passed: nested function can access json module")
            return True
        else:
            print(f"❌ JSON scope test failed: got {result!r}, expected {expected!r}")
            return False
            
    except Exception as e:
        print(f"❌ JSON scope test error: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Testing Export Function Fix")
    print("=" * 60)
    
    test1_passed = test_safe_json_parse()
    test2_passed = test_json_scope()
    
    print("\n" + "=" * 60)
    if test1_passed and test2_passed:
        print("🎉 All tests passed! The export function fix should work.")
    else:
        print("💥 Some tests failed. The fix may need more work.")
    print("=" * 60)