"""
RNet File Encryption Utility
Provides encryption and decryption for .rnet files to prevent tampering
Uses AES-256 encryption with HMAC for integrity verification
"""

import json
import base64
import hashlib
import hmac
import os
from typing import Dict, Any, Tuple, Optional
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from datetime import datetime


class RNetEncryption:
    """Handles encryption/decryption of RNet files"""
    
    # Encryption key - In production, this should be in environment variables or secure key management
    # For now, using a consistent key. CHANGE THIS IN PRODUCTION!
    ENCRYPTION_KEY = b'RiddleNet_Secure_Key_2025_Change_Me!'  # 36 bytes, will be hashed to 32
    
    # HMAC key for integrity verification
    HMAC_KEY = b'RiddleNet_HMAC_Key_2025_Integrity!'  # 35 bytes, will be hashed to 32
    
    # File format version
    ENCRYPTED_FORMAT_VERSION = '2.0'
    
    @classmethod
    def _get_encryption_key(cls) -> bytes:
        """Get the encryption key (hashed to 32 bytes for AES-256)"""
        # Use environment variable if available, otherwise use default
        key_string = os.environ.get('RNET_ENCRYPTION_KEY', cls.ENCRYPTION_KEY.decode('utf-8'))
        return hashlib.sha256(key_string.encode()).digest()
    
    @classmethod
    def _get_hmac_key(cls) -> bytes:
        """Get the HMAC key (hashed to 32 bytes)"""
        key_string = os.environ.get('RNET_HMAC_KEY', cls.HMAC_KEY.decode('utf-8'))
        return hashlib.sha256(key_string.encode()).digest()
    
    @classmethod
    def encrypt_rnet_data(cls, rnet_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Encrypt RNet file data
        
        Args:
            rnet_data: Original RNet data dictionary
            
        Returns:
            Encrypted RNet data structure with integrity checks
        """
        try:
            # Convert data to JSON string
            json_str = json.dumps(rnet_data, ensure_ascii=False)
            json_bytes = json_str.encode('utf-8')
            
            # Generate random IV (Initialization Vector)
            iv = os.urandom(16)
            
            # Create cipher
            key = cls._get_encryption_key()
            cipher = Cipher(
                algorithms.AES(key),
                modes.CBC(iv),
                backend=default_backend()
            )
            encryptor = cipher.encryptor()
            
            # Apply PKCS7 padding
            padder = padding.PKCS7(128).padder()
            padded_data = padder.update(json_bytes) + padder.finalize()
            
            # Encrypt
            encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
            
            # Encode to base64 for JSON compatibility
            encrypted_b64 = base64.b64encode(encrypted_data).decode('utf-8')
            iv_b64 = base64.b64encode(iv).decode('utf-8')
            
            # Generate HMAC for integrity verification
            hmac_key = cls._get_hmac_key()
            h = hmac.new(hmac_key, encrypted_data + iv, hashlib.sha256)
            hmac_signature = base64.b64encode(h.digest()).decode('utf-8')
            
            # Create encrypted container
            encrypted_container = {
                'format': 'rnetfile_encrypted',
                'version': cls.ENCRYPTED_FORMAT_VERSION,
                'encrypted_at': datetime.utcnow().isoformat(),
                'encryption_metadata': {
                    'algorithm': 'AES-256-CBC',
                    'integrity_check': 'HMAC-SHA256',
                    'encoding': 'base64'
                },
                'encrypted_data': encrypted_b64,
                'iv': iv_b64,
                'integrity_signature': hmac_signature,
                # Keep some metadata visible for file identification
                'visible_metadata': {
                    'original_format': rnet_data.get('format', 'rnetfile'),
                    'original_version': rnet_data.get('version', '1.0'),
                    'simulation_title': rnet_data.get('simulation', {}).get('title', 'Unknown'),
                    'exported_by': rnet_data.get('exported_by', 'Unknown'),
                    'exported_at': rnet_data.get('exported_at', datetime.utcnow().isoformat())
                }
            }
            
            return encrypted_container
            
        except Exception as e:
            raise Exception(f"Encryption failed: {str(e)}")
    
    @classmethod
    def decrypt_rnet_data(cls, encrypted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decrypt RNet file data and verify integrity
        
        Args:
            encrypted_data: Encrypted RNet data structure
            
        Returns:
            Original RNet data dictionary
            
        Raises:
            ValueError: If integrity check fails or decryption fails
        """
        try:
            # Check if this is an encrypted file
            if encrypted_data.get('format') != 'rnetfile_encrypted':
                # If it's a plain rnetfile, return as-is (backward compatibility)
                if encrypted_data.get('format') == 'rnetfile':
                    return encrypted_data
                raise ValueError('Invalid encrypted RNet file format')
            
            # Check if this is client-side Base64 encryption (v2.0) or server-side AES (v2.0)
            version = encrypted_data.get('version', '1.0')
            encryption_metadata = encrypted_data.get('metadata', {})
            encryption_method = encryption_metadata.get('encryption_method', '')
            
            # Handle client-side Base64 obfuscation (from student exports)
            if encryption_method == 'client_base64_obfuscation':
                print("[DEBUG] Client-side Base64 encryption detected")
                encrypted_b64 = encrypted_data.get('encrypted_data')
                if not encrypted_b64:
                    raise ValueError('Missing encrypted_data field')
                
                try:
                    # Decode Base64
                    import urllib.parse
                    decoded_str = base64.b64decode(encrypted_b64).decode('utf-8')
                    print(f"[DEBUG] Base64 decoded, length: {len(decoded_str)}")
                    # Parse JSON
                    decrypted_data = json.loads(decoded_str)
                    print(f"[DEBUG] Decrypted data keys: {list(decrypted_data.keys())}")
                    print(f"[DEBUG] Decrypted format: {decrypted_data.get('format')}")
                    return decrypted_data
                except Exception as e:
                    print(f"[ERROR] Client-side decryption error: {str(e)}")
                    raise ValueError(f'Client-side decryption failed: {str(e)}')
            
            # Handle server-side AES-256 encryption (from instructor exports)
            # Extract encrypted components
            encrypted_b64 = encrypted_data.get('encrypted_data')
            iv_b64 = encrypted_data.get('iv')
            stored_signature = encrypted_data.get('integrity_signature')
            
            if not all([encrypted_b64, iv_b64, stored_signature]):
                raise ValueError('Missing required encryption fields for AES decryption')
            
            # Decode from base64
            encrypted_bytes = base64.b64decode(encrypted_b64)
            iv = base64.b64decode(iv_b64)
            
            # Verify HMAC signature (integrity check)
            hmac_key = cls._get_hmac_key()
            h = hmac.new(hmac_key, encrypted_bytes + iv, hashlib.sha256)
            computed_signature = base64.b64encode(h.digest()).decode('utf-8')
            
            if not hmac.compare_digest(computed_signature, stored_signature):
                raise ValueError('Integrity check failed - file has been tampered with!')
            
            # Decrypt
            key = cls._get_encryption_key()
            cipher = Cipher(
                algorithms.AES(key),
                modes.CBC(iv),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            
            padded_data = decryptor.update(encrypted_bytes) + decryptor.finalize()
            
            # Remove PKCS7 padding
            unpadder = padding.PKCS7(128).unpadder()
            json_bytes = unpadder.update(padded_data) + unpadder.finalize()
            
            # Parse JSON
            json_str = json_bytes.decode('utf-8')
            original_data = json.loads(json_str)
            
            return original_data
            
        except ValueError as e:
            # Re-raise ValueError with original message
            raise
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")
    
    @classmethod
    def is_encrypted(cls, data: Dict[str, Any]) -> bool:
        """
        Check if RNet data is encrypted
        
        Args:
            data: RNet data dictionary
            
        Returns:
            True if encrypted, False otherwise
        """
        return data.get('format') == 'rnetfile_encrypted'
    
    @classmethod
    def get_file_info(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get basic file information without decrypting
        
        Args:
            data: RNet data dictionary (encrypted or unencrypted)
            
        Returns:
            Dictionary with file information
        """
        if cls.is_encrypted(data):
            return {
                'encrypted': True,
                'format': data.get('format'),
                'version': data.get('version'),
                'encrypted_at': data.get('encrypted_at'),
                'metadata': data.get('visible_metadata', {}),
                'encryption_info': data.get('encryption_metadata', {})
            }
        else:
            return {
                'encrypted': False,
                'format': data.get('format'),
                'version': data.get('version'),
                'exported_at': data.get('exported_at'),
                'exported_by': data.get('exported_by'),
                'simulation_title': data.get('simulation', {}).get('title')
            }
    
    @classmethod
    def validate_integrity(cls, data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate file integrity without full decryption
        
        Args:
            data: RNet data dictionary
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            print(f"[DEBUG] validate_integrity called")
            print(f"[DEBUG] Data keys: {list(data.keys())}")
            print(f"[DEBUG] Format: {data.get('format')}")
            print(f"[DEBUG] Version: {data.get('version')}")
            
            if not cls.is_encrypted(data):
                return True, None
            
            # Check if this is client-side Base64 encryption (from student exports)
            encryption_metadata = data.get('metadata', {})
            print(f"[DEBUG] Metadata: {encryption_metadata}")
            encryption_method = encryption_metadata.get('encryption_method', '')
            print(f"[DEBUG] Encryption method: {encryption_method}")
            
            if encryption_method == 'client_base64_obfuscation':
                # Client-side encryption doesn't have HMAC, so just verify the data exists
                encrypted_b64 = data.get('encrypted_data')
                if not encrypted_b64:
                    return False, 'Missing encrypted_data field'
                # Client-side encryption is valid if it has encrypted_data
                return True, None
            
            # Server-side AES encryption validation
            encrypted_b64 = data.get('encrypted_data')
            iv_b64 = data.get('iv')
            stored_signature = data.get('integrity_signature')
            
            if not all([encrypted_b64, iv_b64, stored_signature]):
                return False, 'Missing required encryption fields for AES validation'
            
            # Decode and verify HMAC
            encrypted_bytes = base64.b64decode(encrypted_b64)
            iv = base64.b64decode(iv_b64)
            
            hmac_key = cls._get_hmac_key()
            h = hmac.new(hmac_key, encrypted_bytes + iv, hashlib.sha256)
            computed_signature = base64.b64encode(h.digest()).decode('utf-8')
            
            if not hmac.compare_digest(computed_signature, stored_signature):
                return False, 'Integrity check failed - file has been tampered with'
            
            return True, None
            
        except Exception as e:
            return False, f'Validation error: {str(e)}'


# Convenience functions
def encrypt_rnet_file(rnet_data: Dict[str, Any]) -> Dict[str, Any]:
    """Encrypt RNet file data"""
    return RNetEncryption.encrypt_rnet_data(rnet_data)


def decrypt_rnet_file(encrypted_data: Dict[str, Any]) -> Dict[str, Any]:
    """Decrypt RNet file data"""
    return RNetEncryption.decrypt_rnet_data(encrypted_data)


def is_encrypted_rnet(data: Dict[str, Any]) -> bool:
    """Check if RNet file is encrypted"""
    return RNetEncryption.is_encrypted(data)


def validate_rnet_integrity(data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """Validate RNet file integrity"""
    return RNetEncryption.validate_integrity(data)
