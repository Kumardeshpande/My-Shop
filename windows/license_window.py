# windows/license_window.py
import tkinter as tk
import sys
from license import LicenseManager
from datetime import datetime

class LicenseActivationWindow:
    def __init__(self, license_manager):
        self.license_manager = license_manager
        self.activation_window = tk.Tk()
        self.activation_window.title("सॉफ्टवेअर अ‍ॅक्टिव्हेशन")
        self.activation_window.geometry("700x600")
        self.activation_window.configure(bg='white')
        self.activation_window.resizable(False, False)
        self.center_window(self.activation_window)
        self.activation_window.grab_set()
        self.setup_ui()
    
    def center_window(self, window):
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_ui(self):
        main_frame = tk.Frame(self.activation_window, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)
        
        tk.Label(main_frame, text="सॉफ्टवेअर अ‍ॅक्टिव्हेशन", 
                font=('Arial', 20, 'bold'), bg='white', fg='#1a1a2e').pack(pady=(0, 30))
        
        hardware_id = self.license_manager.get_hardware_id()
        
        hardware_frame = tk.LabelFrame(main_frame, text="तुमचा Hardware ID", 
                                      bg='white', font=('Arial', 10, 'bold'))
        hardware_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(hardware_frame, text=hardware_id, bg='white', 
                font=('Courier New', 14, 'bold'), fg='#e94560').pack(pady=10, padx=10)
        
        copy_btn = tk.Button(hardware_frame, text="📋 Copy to Clipboard", 
                           bg='#3a86ff', fg='white',
                           font=('Arial', 10), 
                           command=lambda: self.copy_to_clipboard(hardware_id))
        copy_btn.pack(pady=(0, 10))
        
        instructions = tk.LabelFrame(main_frame, text="सूचना", 
                                    bg='white', font=('Arial', 10, 'bold'))
        instructions.pack(fill=tk.X, pady=(0, 20))
        
        instruction_text = """1. हा Hardware ID डेव्हलपरला पाठवा
2. डेव्हलपरकडून License Key मिळेल
3. खालील बॉक्समध्ये License Key टाका
4. 'Activate' बटण दाबा"""
        
        tk.Label(instructions, text=instruction_text, bg='white', 
                font=('Arial', 9), justify=tk.LEFT).pack(pady=10, padx=10)
        
        license_frame = tk.Frame(main_frame, bg='white')
        license_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(license_frame, text="License Key:", bg='white', 
                font=('Arial', 10)).pack(anchor='w', pady=(0, 5))
        
        self.license_key_entry = tk.Entry(license_frame, width=40, 
                                         font=('Courier New', 12))
        self.license_key_entry.pack(fill=tk.X, pady=(0, 10))
        
        button_frame = tk.Frame(main_frame, bg='white')
        button_frame.pack(fill=tk.X)
        
        activate_btn = tk.Button(button_frame, text="✅ Activate", 
                               bg='#0fcea7', fg='white',
                               font=('Arial', 12, 'bold'), 
                               command=self.activate_license,
                               width=15)
        activate_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        exit_btn = tk.Button(button_frame, text="❌ Exit", 
                           bg='#e94560', fg='white',
                           font=('Arial', 12), 
                           command=self.exit_app,
                           width=15)
        exit_btn.pack(side=tk.RIGHT)
        
        self.status_label = tk.Label(main_frame, text="", bg='white', 
                                    fg='#e94560', font=('Arial', 10))
        self.status_label.pack(pady=10)
        
        self.activation_window.bind('<Return>', lambda e: self.activate_license())
    
    def copy_to_clipboard(self, text):
        self.activation_window.clipboard_clear()
        self.activation_window.clipboard_append(text)
        self.status_label.config(text="Hardware ID clipboard मध्ये copy केला!")
    
    def activate_license(self):
        license_key = self.license_key_entry.get().strip()
        hardware_id = self.license_manager.get_hardware_id()
        
        if not license_key:
            self.status_label.config(text="कृपया License Key प्रविष्ट करा")
            return
        
        clean_license_key = license_key.replace('-', '').replace(' ', '')
        clean_hardware_id = hardware_id.replace('-', '').replace(' ', '')
        expected_key = self.license_manager.generate_license_key(hardware_id)
        clean_expected_key = expected_key.replace('-', '')
        
        if clean_license_key.upper() == clean_expected_key:
            if self.license_manager.save_license(hardware_id, license_key):
                self.status_label.config(text="✅ सॉफ्टवेअर यशस्वीरित्या activate केले!", fg='#0fcea7')
                self.activation_window.after(2000, self.activation_window.destroy)
            else:
                self.status_label.config(text="❌ License save करताना त्रुटी")
        else:
            self.status_label.config(text="❌ अवैध License Key")
    
    def exit_app(self):
        self.activation_window.destroy()
        sys.exit(0)
    
    def run(self):
        self.activation_window.mainloop()