# main.py
#!/usr/bin/env python3
"""
माझे दुकान - Shop Management System
Main entry point
"""

import sys
import os

# Add project directories to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'windows'))
sys.path.insert(0, os.path.join(current_dir, 'modules'))
sys.path.insert(0, os.path.join(current_dir, 'utils'))

# main.py च्या main() फंक्शनमध्ये खालील बदल करा:

def main():
    """Main application entry point"""
    print("🚀 माझे दुकान - Shop Management System")
    print("=" * 50)
    
    # Check license first
    try:
        from license import LicenseManager
        license_manager = LicenseManager()
        
        if not license_manager.validate_license():
            print("⚠️  License validation failed. Starting activation...")
            from windows.license_window import LicenseActivationWindow
            activation_window = LicenseActivationWindow(license_manager)
            activation_window.run()
            
            # Check again after activation
            if not license_manager.validate_license():
                print("❌ License activation failed. Exiting...")
                input("Press Enter to exit...")
                sys.exit(1)
        
        print("✅ License validated successfully")
        
    except ImportError as e:
        print(f"⚠️  License module not found: {e}")
        print("⚠️  Continuing without license check...")
    
    # Initialize database
    try:
        from database import DatabaseManager
        db = DatabaseManager()
        print("✅ Database initialized")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Initialize sales module (हे नवीन जोडा)
    try:
        from modules.sales import SalesModule
        sales_module = SalesModule(db, None)  # parent_app कालांतराने set केले जाईल
        print("✅ Sales module initialized")
    except Exception as e:
        print(f"❌ Sales module initialization failed: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Start login window
    try:
        from windows.login_window import LoginWindow
        login_window = LoginWindow(db)
        login_window.run()
    except Exception as e:
        print(f"❌ Application startup failed: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()