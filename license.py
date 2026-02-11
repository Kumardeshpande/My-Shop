# license.py
import hashlib
import uuid
import base64
import json
import os
from datetime import datetime

class LicenseManager:
    def __init__(self):
        self.license_file = 'license.lic'
    
    def get_hardware_id(self):
        """Generate hardware ID based on system information"""
        try:
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                           for elements in range(0, 8*6, 8)][::-1])
            import platform
            computer_name = platform.node()
            processor = platform.processor()
            combined = f"{mac}{computer_name}{processor}"
            hardware_id = hashlib.sha256(combined.encode()).hexdigest()[:32].upper()
            formatted_id = '-'.join([hardware_id[i:i+5] for i in range(0, len(hardware_id), 5)])
            return formatted_id
        except:
            return hashlib.sha256(str(uuid.getnode()).encode()).hexdigest()[:32].upper()
    
    def generate_license_key(self, hardware_id):
        """Generate license key from hardware ID"""
        clean_hardware_id = hardware_id.replace('-', '')
        first_hash = hashlib.sha256(clean_hardware_id.encode()).hexdigest()
        license_key = hashlib.sha256(first_hash.encode()).hexdigest()[:32].upper()
        formatted_key = '-'.join([license_key[i:i+5] for i in range(0, len(license_key), 5)])
        return formatted_key
    
    def simple_encrypt(self, text):
        """Simple encryption using base64 and XOR"""
        text_bytes = text.encode()
        key = b'my_shop_license_key_2024'
        encrypted = bytearray()
        for i in range(len(text_bytes)):
            encrypted.append(text_bytes[i] ^ key[i % len(key)])
        return base64.b64encode(encrypted).decode()
    
    def simple_decrypt(self, encrypted_text):
        """Simple decryption"""
        try:
            encrypted_bytes = base64.b64decode(encrypted_text)
            key = b'my_shop_license_key_2024'
            decrypted = bytearray()
            for i in range(len(encrypted_bytes)):
                decrypted.append(encrypted_bytes[i] ^ key[i % len(key)])
            return decrypted.decode()
        except:
            return None
    
    def save_license(self, hardware_id, license_key):
        """Save license data with simple encryption"""
        try:
            license_data = {
                'hardware_id': hardware_id,
                'license_key': license_key,
                'activated_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'version': '1.1.0'
            }
            json_data = json.dumps(license_data)
            encrypted_data = self.simple_encrypt(json_data)
            signature = hashlib.md5(encrypted_data.encode()).hexdigest()
            final_data = f"{signature}:{encrypted_data}"
            with open(self.license_file, 'w') as f:
                f.write(final_data)
            return True
        except Exception as e:
            print(f"Save error: {e}")
            return False
    
    def load_license(self):
        """Load and decrypt license data"""
        try:
            if not os.path.exists(self.license_file):
                return None
            with open(self.license_file, 'r') as f:
                file_data = f.read().strip()
            if not file_data:
                return None
            if ':' not in file_data:
                return None
            signature, encrypted_data = file_data.split(':', 1)
            if hashlib.md5(encrypted_data.encode()).hexdigest() != signature:
                return None
            json_data = self.simple_decrypt(encrypted_data)
            if not json_data:
                return None
            license_data = json.loads(json_data)
            return license_data
        except:
            return None
    
    def validate_license(self):
        """Validate license"""
        try:
            license_data = self.load_license()
            if not license_data:
                return False
            current_hardware_id = self.get_hardware_id()
            if license_data['hardware_id'] != current_hardware_id:
                return False
            expected_key = self.generate_license_key(current_hardware_id)
            clean_expected = expected_key.replace('-', '').upper()
            clean_stored = license_data['license_key'].replace('-', '').replace(' ', '').upper()
            return clean_stored == clean_expected
        except:
            return False
    
    def check_license(self):
        """Check license and show activation window if needed"""
        if not self.validate_license():
            from windows.license_window import LicenseActivationWindow
            activation_window = LicenseActivationWindow(self)
            activation_window.run()
            return False
        return True