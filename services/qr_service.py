"""
QR Code Service for RiddleNet
Handles QR code generation for simulation confirmation and file exports
"""

import qrcode
from io import BytesIO
import base64
from itsdangerous import URLSafeTimedSerializer
from flask import current_app, url_for
from datetime import datetime
import json


class QRCodeService:
    """Service for generating and managing QR codes"""
    
    def __init__(self):
        self.default_qr_config = {
            'version': 1,
            'error_correction': qrcode.constants.ERROR_CORRECT_L,
            'box_size': 10,
            'border': 4,
        }
    
    def generate_simulation_confirmation_qr(self, simulation_id, export_context=None):
        """
        Generate QR code for simulation confirmation page
        
        Args:
            simulation_id (int): ID of the simulation
            export_context (dict, optional): Additional context for file exports
            
        Returns:
            dict: Contains QR code data and metadata
        """
        try:
            # Create serializer for token generation
            serializer = URLSafeTimedSerializer(current_app.secret_key)
            
            # Prepare token data
            token_data = {
                'simulation_id': simulation_id,
                'generated_at': datetime.utcnow().isoformat(),
                'type': 'file_export' if export_context else 'standard'
            }
            
            # Add export context if provided (for file downloads)
            if export_context:
                token_data.update({
                    'exported_by': export_context.get('exported_by'),
                    'export_timestamp': export_context.get('exported_at'),
                    'file_version': export_context.get('version', '1.0'),
                    'verification_type': 'rnet_file'
                })
            
            # Generate token
            token = serializer.dumps(token_data, salt='simulation-confirm')
            
            # Build confirmation URL
            confirm_url = url_for('dynamic_simulations.confirm_simulation', 
                                 simulation_id=simulation_id, 
                                 token=token, 
                                 _external=True)
            
            # Generate QR code
            qr_data = self._create_qr_image(confirm_url)
            
            return {
                'success': True,
                'qr_code_base64': qr_data['base64'],
                'qr_code_url': qr_data['data_url'],
                'confirmation_url': confirm_url,
                'token': token,
                'metadata': {
                    'simulation_id': simulation_id,
                    'generated_at': datetime.utcnow().isoformat(),
                    'type': token_data['type'],
                    'export_context': export_context
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"Error generating QR code for simulation {simulation_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _create_qr_image(self, data, config=None):
        """
        Create QR code image from data
        
        Args:
            data (str): Data to encode in QR code
            config (dict, optional): QR code configuration
            
        Returns:
            dict: QR code image data
        """
        # Use provided config or default
        qr_config = config or self.default_qr_config.copy()
        
        # Create QR code
        qr = qrcode.QRCode(
            version=qr_config['version'],
            error_correction=qr_config['error_correction'],
            box_size=qr_config['box_size'],
            border=qr_config['border'],
        )
        
        qr.add_data(data)
        qr.make(fit=True)
        
        # Create QR code image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to bytes
        img_buffer = BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        img_bytes = img_buffer.getvalue()
        
        # Convert to base64
        base64_string = base64.b64encode(img_bytes).decode('utf-8')
        data_url = f"data:image/png;base64,{base64_string}"
        
        return {
            'bytes': img_bytes,
            'base64': base64_string,
            'data_url': data_url
        }
    
    def verify_qr_token(self, token, simulation_id):
        """
        Verify QR code token
        
        Args:
            token (str): Token to verify
            simulation_id (int): Expected simulation ID
            
        Returns:
            dict: Verification result
        """
        try:
            serializer = URLSafeTimedSerializer(current_app.secret_key)
            
            # Decode token (max age: 24 hours for file exports, 1 hour for standard)
            data = serializer.loads(token, salt='simulation-confirm', max_age=86400)
            
            # Verify simulation ID matches
            if data.get('simulation_id') != simulation_id:
                return {
                    'valid': False,
                    'error': 'Token simulation ID mismatch'
                }
            
            return {
                'valid': True,
                'data': data,
                'type': data.get('type', 'standard'),
                'export_context': {
                    'exported_by': data.get('exported_by'),
                    'export_timestamp': data.get('export_timestamp'),
                    'file_version': data.get('file_version'),
                    'verification_type': data.get('verification_type')
                } if data.get('type') == 'file_export' else None
            }
            
        except Exception as e:
            current_app.logger.warning(f"Token verification failed: {e}")
            return {
                'valid': False,
                'error': str(e)
            }
    
    def generate_file_embedded_qr(self, simulation_id, export_metadata):
        """
        Generate QR code specifically for embedding in exported files
        
        Args:
            simulation_id (int): Simulation ID
            export_metadata (dict): Export context and metadata
            
        Returns:
            dict: QR code data optimized for file embedding
        """
        # Generate QR code with export context
        qr_result = self.generate_simulation_confirmation_qr(
            simulation_id, 
            export_context=export_metadata
        )
        
        if qr_result['success']:
            # Add file-specific metadata
            qr_result['file_metadata'] = {
                'purpose': 'File verification and ownership proof',
                'instructions': 'Scan this QR code to verify simulation ownership and access confirmation page',
                'verification_url': qr_result['confirmation_url'],
                'generated_for_export': True
            }
        
        return qr_result


# Utility functions for backward compatibility
def generate_qr_code_for_simulation(simulation_id, export_context=None):
    """Convenience function for generating simulation QR codes"""
    service = QRCodeService()
    return service.generate_simulation_confirmation_qr(simulation_id, export_context)


def verify_simulation_qr_token(token, simulation_id):
    """Convenience function for verifying QR tokens"""
    service = QRCodeService()
    return service.verify_qr_token(token, simulation_id)