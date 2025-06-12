#!/usr/bin/env python3
"""
Verification script for Module 6 fix in Networking 2
This script verifies that all Module 6 components are properly integrated
"""

def verify_module6_fix():
    """Verify that Module 6 is properly integrated"""
    print("🔍 Verifying Module 6 Integration in Networking 2...")
    print("=" * 60)
    
    success_count = 0
    total_tests = 5
    
    # Test 1: Check if Module 6 content exists in content file
    try:
        from networking2_updated_content import get_networking2_content
        content = get_networking2_content()
        
        if 'net2_6.1' in content:
            print("✅ Test 1 PASSED: Module 6 content exists in networking2_updated_content.py")
            success_count += 1
        else:
            print("❌ Test 1 FAILED: Module 6 content missing from networking2_updated_content.py")
    except Exception as e:
        print(f"❌ Test 1 ERROR: {e}")
    
    # Test 2: Check if Module 6 file exists
    import os
    module6_file = r"c:\Users\gilbe\OneDrive\Desktop\RiddleNet_Latest - Copy (6)\modules\Networking 2\ISLES-LSPU-Sample-Module-in-Networking-2-Module-6.txt"
    
    if os.path.exists(module6_file):
        print("✅ Test 2 PASSED: Module 6 file exists in file system")
        success_count += 1
    else:
        print("❌ Test 2 FAILED: Module 6 file missing from file system")
    
    # Test 3: Check if service recognizes Module 6
    try:
        from services.networking2_service import networking2_service
        modules = networking2_service.get_detailed_module_structure()
        
        if '6' in modules and modules['6']['title'] == 'Network Security and VPN':
            print("✅ Test 3 PASSED: Service recognizes Module 6 with correct title")
            success_count += 1
        else:
            print("❌ Test 3 FAILED: Service doesn't recognize Module 6 or has wrong title")
    except Exception as e:
        print(f"❌ Test 3 ERROR: {e}")
    
    # Test 4: Check if lesson content can be retrieved
    try:
        from services.networking2_service import networking2_service
        lesson = networking2_service.get_lesson_content('net2_6.1')
        
        if lesson and lesson.get('title') == 'Network Security and VPN' and lesson.get('content'):
            print("✅ Test 4 PASSED: Module 6 lesson content can be retrieved")
            success_count += 1
        else:
            print("❌ Test 4 FAILED: Module 6 lesson content cannot be retrieved or is incomplete")
    except Exception as e:
        print(f"❌ Test 4 ERROR: {e}")
    
    # Test 5: Check if all 7 modules exist in file system
    try:
        modules_dir = r"c:\Users\gilbe\OneDrive\Desktop\RiddleNet_Latest - Copy (6)\modules\Networking 2"
        module_files = [f for f in os.listdir(modules_dir) if f.startswith('ISLES-LSPU-Sample-Module-in-Networking-2-Module-') and f.endswith('.txt')]
        
        if len(module_files) == 7:
            print("✅ Test 5 PASSED: All 7 modules exist in file system")
            success_count += 1
        else:
            print(f"❌ Test 5 FAILED: Expected 7 modules, found {len(module_files)}")
    except Exception as e:
        print(f"❌ Test 5 ERROR: {e}")
    
    print("=" * 60)
    print(f"📊 VERIFICATION RESULTS: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("🎉 SUCCESS: Module 6 is fully integrated and working!")
        return True
    else:
        print("⚠️  WARNING: Some tests failed. Module 6 integration may be incomplete.")
        return False

def show_module6_content_summary():
    """Show a summary of Module 6 content"""
    try:
        from networking2_updated_content import get_networking2_content
        content = get_networking2_content()
        
        if 'net2_6.1' in content:
            lesson = content['net2_6.1']
            print("\n📚 MODULE 6 CONTENT SUMMARY:")
            print("=" * 40)
            print(f"Title: {lesson['title']}")
            print(f"Source File: {lesson.get('source_file', 'N/A')}")
            print("Topics covered:")
            print("- Network Security Fundamentals (CIA Triad)")
            print("- Firewall Technologies")
            print("- Virtual Private Networks (VPNs)")
            print("- Intrusion Detection Systems")
            print("- Security Best Practices")
        else:
            print("❌ Module 6 content not found")
    except Exception as e:
        print(f"❌ Error retrieving Module 6 content: {e}")

if __name__ == "__main__":
    # Run verification
    verification_passed = verify_module6_fix()
    
    # Show content summary
    show_module6_content_summary()
    
    # Final status
    print("\n" + "=" * 60)
    if verification_passed:
        print("🚀 READY: Networking 2 Module 6 is ready for use!")
        print("Users should now be able to see and access Module 6: Network Security and VPN")
    else:
        print("🔧 ACTION NEEDED: Please check the failed tests above")
