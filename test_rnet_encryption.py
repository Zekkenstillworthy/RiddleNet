"""
Test script for RNet file encryption
Run this to verify encryption/decryption works correctly
"""

import json
from datetime import datetime


def test_encryption():
    """Test RNet file encryption and decryption"""
    print("\n" + "="*70)
    print("🧪 RNet File Encryption Test")
    print("="*70 + "\n")
    
    # Import encryption utilities
    try:
        from utils.rnet_encryption import (
            encrypt_rnet_file, 
            decrypt_rnet_file,
            validate_rnet_integrity,
            is_encrypted_rnet,
            RNetEncryption
        )
        print("✅ Encryption module imported successfully\n")
    except ImportError as e:
        print(f"❌ Failed to import encryption module: {e}\n")
        return False
    
    # Create sample RNet data
    sample_rnet = {
        'format': 'rnetfile',
        'version': '1.0',
        'exported_at': datetime.utcnow().isoformat(),
        'exported_by': 'Test User',
        'simulation': {
            'id': 1,
            'title': 'Test Network Simulation',
            'description': 'A test simulation for encryption',
            'simulation_type': 'Troubleshooting',
            'difficulty': 'Beginner',
            'estimated_duration': 30,
            'step_definitions': [
                {'step': 1, 'instruction': 'Configure router', 'points': 10},
                {'step': 2, 'instruction': 'Test connectivity', 'points': 15}
            ],
            'validation_rules': {
                'required_commands': ['show ip route', 'ping'],
                'expected_output': 'Success'
            }
        },
        'verification': {
            'qr_code_included': False
        }
    }
    
    print("📝 Sample RNet data created")
    print(f"   Format: {sample_rnet['format']}")
    print(f"   Title: {sample_rnet['simulation']['title']}")
    print(f"   Steps: {len(sample_rnet['simulation']['step_definitions'])}\n")
    
    # Test 1: Encryption
    print("🔐 Test 1: Encrypting RNet data...")
    try:
        encrypted_data = encrypt_rnet_file(sample_rnet)
        print("✅ Encryption successful!")
        print(f"   Format: {encrypted_data.get('format')}")
        print(f"   Version: {encrypted_data.get('version')}")
        print(f"   Has encrypted_data: {bool(encrypted_data.get('encrypted_data'))}")
        print(f"   Has IV: {bool(encrypted_data.get('iv'))}")
        print(f"   Has signature: {bool(encrypted_data.get('integrity_signature'))}\n")
    except Exception as e:
        print(f"❌ Encryption failed: {e}\n")
        return False
    
    # Test 2: Format Detection
    print("🔍 Test 2: Detecting encrypted format...")
    if is_encrypted_rnet(encrypted_data):
        print("✅ Correctly identified as encrypted\n")
    else:
        print("❌ Failed to detect encryption\n")
        return False
    
    # Test 3: Integrity Validation
    print("🛡️ Test 3: Validating integrity...")
    is_valid, error_msg = validate_rnet_integrity(encrypted_data)
    if is_valid:
        print("✅ Integrity check passed\n")
    else:
        print(f"❌ Integrity check failed: {error_msg}\n")
        return False
    
    # Test 4: Decryption
    print("🔓 Test 4: Decrypting data...")
    try:
        decrypted_data = decrypt_rnet_file(encrypted_data)
        print("✅ Decryption successful!")
        print(f"   Format: {decrypted_data.get('format')}")
        print(f"   Title: {decrypted_data.get('simulation', {}).get('title')}\n")
    except Exception as e:
        print(f"❌ Decryption failed: {e}\n")
        return False
    
    # Test 5: Data Integrity
    print("🔎 Test 5: Verifying data integrity...")
    if decrypted_data == sample_rnet:
        print("✅ Decrypted data matches original perfectly!\n")
    else:
        print("❌ Decrypted data doesn't match original\n")
        print(f"Original keys: {list(sample_rnet.keys())}")
        print(f"Decrypted keys: {list(decrypted_data.keys())}\n")
        return False
    
    # Test 6: Tampering Detection
    print("🚨 Test 6: Testing tampering detection...")
    tampered_data = encrypted_data.copy()
    tampered_data['encrypted_data'] = tampered_data['encrypted_data'][:50] + 'X' + tampered_data['encrypted_data'][51:]
    
    is_valid, error_msg = validate_rnet_integrity(tampered_data)
    if not is_valid:
        print("✅ Tampering detected successfully!")
        print(f"   Error: {error_msg}\n")
    else:
        print("❌ Failed to detect tampering\n")
        return False
    
    # Test 7: Backward Compatibility
    print("🔄 Test 7: Testing backward compatibility...")
    try:
        legacy_result = decrypt_rnet_file(sample_rnet)
        if legacy_result == sample_rnet:
            print("✅ Legacy unencrypted files work correctly!\n")
        else:
            print("❌ Legacy file processing failed\n")
            return False
    except Exception as e:
        print(f"❌ Legacy file error: {e}\n")
        return False
    
    # Test 8: File Info
    print("📋 Test 8: Getting file info...")
    try:
        info = RNetEncryption.get_file_info(encrypted_data)
        print("✅ File info retrieved:")
        print(f"   Encrypted: {info.get('encrypted')}")
        print(f"   Simulation: {info.get('metadata', {}).get('simulation_title')}\n")
    except Exception as e:
        print(f"❌ File info error: {e}\n")
        return False
    
    # Test 9: Save and Load
    print("💾 Test 9: Testing file save/load cycle...")
    try:
        # Save encrypted file
        with open('test_encrypted.rnet', 'w') as f:
            json.dump(encrypted_data, f, indent=2)
        print("✅ Encrypted file saved")
        
        # Load and decrypt
        with open('test_encrypted.rnet', 'r') as f:
            loaded_data = json.load(f)
        
        decrypted_loaded = decrypt_rnet_file(loaded_data)
        
        if decrypted_loaded == sample_rnet:
            print("✅ Save/load cycle successful!\n")
        else:
            print("❌ Loaded data doesn't match\n")
            return False
        
        # Clean up
        import os
        os.remove('test_encrypted.rnet')
        print("✅ Test file cleaned up\n")
        
    except Exception as e:
        print(f"❌ Save/load error: {e}\n")
        return False
    
    # Summary
    print("="*70)
    print("🎉 ALL TESTS PASSED!")
    print("="*70)
    print("\n✅ Encryption works correctly")
    print("✅ Decryption works correctly")
    print("✅ Tampering is detected")
    print("✅ Backward compatibility maintained")
    print("✅ File I/O works properly")
    print("\n🚀 RNet encryption system is ready for production!\n")
    
    return True


def test_performance():
    """Test encryption/decryption performance"""
    print("\n" + "="*70)
    print("⚡ Performance Test")
    print("="*70 + "\n")
    
    from utils.rnet_encryption import encrypt_rnet_file, decrypt_rnet_file
    import time
    
    # Create test data
    test_data = {
        'format': 'rnetfile',
        'version': '1.0',
        'simulation': {
            'id': 1,
            'title': 'Performance Test',
            'step_definitions': [{'step': i, 'instruction': f'Step {i}'} for i in range(100)]
        }
    }
    
    # Test encryption speed
    start = time.time()
    for _ in range(10):
        encrypted = encrypt_rnet_file(test_data)
    encrypt_time = (time.time() - start) / 10
    
    print(f"🔐 Average encryption time: {encrypt_time*1000:.2f}ms")
    
    # Test decryption speed
    start = time.time()
    for _ in range(10):
        decrypted = decrypt_rnet_file(encrypted)
    decrypt_time = (time.time() - start) / 10
    
    print(f"🔓 Average decryption time: {decrypt_time*1000:.2f}ms")
    print(f"📊 Total round-trip time: {(encrypt_time + decrypt_time)*1000:.2f}ms\n")
    
    if (encrypt_time + decrypt_time) < 0.1:  # Less than 100ms
        print("✅ Performance is excellent! (< 100ms)\n")
        return True
    elif (encrypt_time + decrypt_time) < 0.5:  # Less than 500ms
        print("✅ Performance is good! (< 500ms)\n")
        return True
    else:
        print("⚠️ Performance is slow (> 500ms)\n")
        return False


if __name__ == '__main__':
    print("\n🔬 RNet Encryption Test Suite\n")
    
    # Run main tests
    if test_encryption():
        # Run performance test
        test_performance()
        print("="*70)
        print("✅ All tests completed successfully!")
        print("="*70 + "\n")
    else:
        print("\n" + "="*70)
        print("❌ Some tests failed - check output above")
        print("="*70 + "\n")
