import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime, timedelta
import os
import subprocess
import sys
import tempfile
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from tkcalendar import DateEntry
import random
import string
import webbrowser
import shutil
import json
class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect('shop_management.db')
        self.cursor = self.conn.cursor()
        self.create_tables()
    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                barcode TEXT,
                name TEXT NOT NULL,
                category TEXT,
                purchase_price REAL DEFAULT 0,
                sale_price REAL DEFAULT 0,
                stock INTEGER DEFAULT 0,
                min_stock INTEGER DEFAULT 10,
                unit TEXT DEFAULT 'पीसी',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                phone TEXT,
                address TEXT,
                credit_balance REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS suppliers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                phone TEXT,
                address TEXT,
                credit_balance REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_no TEXT UNIQUE,
                customer_name TEXT,
                date TIMESTAMP,
                total_amount REAL DEFAULT 0,
                discount_amount REAL DEFAULT 0,
                discount_type TEXT DEFAULT '₹',
                paid_amount REAL DEFAULT 0,
                balance_amount REAL DEFAULT 0,
                payment_mode TEXT,
                status TEXT,
                transaction_type TEXT DEFAULT 'विक्री',
                note TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sale_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_id INTEGER,
                product_id INTEGER,
                product_name TEXT,
                quantity INTEGER,
                price REAL,
                total REAL,
                FOREIGN KEY (sale_id) REFERENCES sales (id)
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_no TEXT UNIQUE,
                supplier_name TEXT,
                date TIMESTAMP,
                total_amount REAL DEFAULT 0,
                paid_amount REAL DEFAULT 0,
                balance_amount REAL DEFAULT 0,
                payment_mode TEXT,
                status TEXT,
                transaction_type TEXT DEFAULT 'खरेदी',
                note TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS purchase_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                purchase_id INTEGER,
                product_id INTEGER,
                product_name TEXT,
                quantity INTEGER,
                price REAL,
                total REAL,
                FOREIGN KEY (purchase_id) REFERENCES purchases (id)
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS shop_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                shop_name TEXT DEFAULT 'माय शॉप',
                owner_name TEXT,
                address TEXT,
                phone TEXT,
                email TEXT,
                gst_no TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS backup_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                auto_backup INTEGER DEFAULT 0,
                backup_path TEXT,
                backup_interval_hours INTEGER DEFAULT 24,
                keep_days INTEGER DEFAULT 30,
                last_backup TIMESTAMP
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                full_name TEXT,
                user_type TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS print_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                header_text TEXT DEFAULT '',
                footer_text TEXT DEFAULT '',
                font_size INTEGER DEFAULT 10
            )
        ''')
        self.conn.commit()
        self.cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
        if self.cursor.fetchone()[0] == 0:
            self.cursor.execute("INSERT INTO users (username, password, full_name, user_type) VALUES ('admin', 'admin', 'Administrator', 'admin')")
            self.conn.commit()
import hashlib
import uuid
import base64
import json
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
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
            activation_window = LicenseActivationWindow(self)
            activation_window.run()
            return False
        return True
class LoginWindow:
    def __init__(self, db):
        self.db = db
        self.login_window = tk.Tk()
        self.login_window.title("माझे दुकान")
        self.login_window.geometry("450x350")
        self.login_window.configure(bg='white')
        self.center_window(self.login_window)
        self.setup_ui()
    def center_window(self, window):
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f'{width}x{height}+{x}+{y}')
    def setup_ui(self):
        main_frame = tk.Frame(self.login_window, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)
        tk.Label(main_frame, text="माझे दुकान", 
                font=('Arial', 24, 'bold'), bg='white', fg='#1a1a2e').pack(pady=(0, 30))
        form_frame = tk.Frame(main_frame, bg='white')
        form_frame.pack(fill=tk.BOTH, expand=True)
        tk.Label(form_frame, text="वापरकर्ता नाव:", bg='white', 
                font=('Arial', 12)).pack(anchor='w', pady=(0, 5))
        self.username_entry = tk.Entry(form_frame, font=('Arial', 12))
        self.username_entry.pack(fill=tk.X, pady=(0, 15))
        self.username_entry.insert(0, "admin")
        self.username_entry.bind('<Return>', lambda e: self.password_entry.focus())
        tk.Label(form_frame, text="पासवर्ड:", bg='white', 
                font=('Arial', 12)).pack(anchor='w', pady=(0, 5))
        self.password_entry = tk.Entry(form_frame, show="*", font=('Arial', 12))
        self.password_entry.pack(fill=tk.X, pady=(0, 20))
        self.password_entry.bind('<Return>', lambda e: self.login())
        button_frame = tk.Frame(form_frame, bg='white')
        button_frame.pack(fill=tk.X, pady=20)
        login_btn = tk.Button(button_frame, text="प्रवेश करा", bg='#0fcea7', fg='white',
                            font=('Arial', 12, 'bold'), command=self.login, height=2)
        login_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        close_btn = tk.Button(button_frame, text="बंद करा", bg='#e94560', fg='white',
                            font=('Arial', 12, 'bold'), command=self.login_window.destroy, height=2)
        close_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        self.status_label = tk.Label(form_frame, text="", bg='white', fg='#e94560', font=('Arial', 10))
        self.status_label.pack(pady=5)
        self.login_window.bind('<Return>', lambda e: self.login())
    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if not username or not password:
            self.status_label.config(text="कृपया वापरकर्ता नाव आणि पासवर्ड प्रविष्ट करा")
            return
        try:
            self.db.cursor.execute("SELECT password, user_type FROM users WHERE username = ?", (username,))
            result = self.db.cursor.fetchone()
            if result and result[0] == password:
                self.login_window.destroy()
                app = ShopManagementApp(username, result[1])
                app.run()
            else:
                self.status_label.config(text="अवैध वापरकर्ता नाव किंवा पासवर्ड")
        except Exception as e:
            self.status_label.config(text=f"लॉगिन त्रुटी: {str(e)}")
    def run(self):
        self.login_window.mainloop()
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
        instruction_text = """
1. हा Hardware ID डेव्हलपरला पाठवा
2. डेव्हलपरकडून License Key मिळेल
3. खालील बॉक्समध्ये License Key टाका
4. 'Activate' बटण दाबा
"""
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
class ShopManagementApp:
    def __init__(self, username, user_type):
        self.username = username
        self.user_type = user_type
        self.root = tk.Tk()
        self.db = DatabaseManager()
        self.load_shop_info()
        self.root.title(f"{self.shop_name} आवृत्ती १.१.०")
        self.root.geometry("1400x750")
        self.root.state('zoomed')
        self.current_tab = 0
        self.sale_cart = []
        self.current_customer_id = None
        self.last_sale_id = None
        self.purchase_cart = []
        self.current_supplier_id = None
        self.last_purchase_id = None
        self.setup_ui()
        self.update_time_display()
        self.root.bind('<Return>', self.focus_next_widget)
    def refresh_all_tabs(self):
        """Refresh all tabs when transaction completes"""
        if self.current_tab == 0:  # Dashboard tab
            self.update_dashboard_stats()  # येथे बदल
        elif self.current_tab == 1:  # Sales tab
            self.refresh_sales_tab()
        elif self.current_tab == 2:  # Purchases tab
            self.refresh_purchases_tab()
        elif self.current_tab == 3:  # Stock tab
            self.refresh_stock_tab()
        elif self.current_tab == 4:  # Accounts tab
            self.refresh_accounts_tab()
        elif self.current_tab == 5:  # Reports tab
            self.refresh_reports_tab()
        elif self.current_tab == 6:  # Settings tab
            self.refresh_settings_tab()
    def refresh_low_stock_panel(self):
        """Refresh low stock panel data"""
        if hasattr(self, 'low_stock_listbox'):
            self.low_stock_listbox.delete(0, tk.END)
            try:
                self.db.cursor.execute('''
                    SELECT name, stock, min_stock FROM products 
                    WHERE stock <= min_stock AND stock > 0
                    ORDER BY stock ASC
                    LIMIT 10
                ''')
                products = self.db.cursor.fetchall()
                for product in products:
                    name, stock, min_stock = product
                    self.low_stock_listbox.insert(tk.END, f"{name} - {stock} पीसी (किमान: {min_stock})")
            except:
                pass
    def refresh_high_credit_panel(self):
        """Refresh high credit panel data"""
        if hasattr(self, 'high_credit_listbox'):
            self.high_credit_listbox.delete(0, tk.END)
            try:
                self.db.cursor.execute('''
                    SELECT name, credit_balance FROM customers 
                    WHERE credit_balance > 0 AND name NOT LIKE 'CUST-%'
                    ORDER BY credit_balance DESC
                    LIMIT 10
                ''')
                customers = self.db.cursor.fetchall()
                for customer in customers:
                    name, credit = customer
                    self.high_credit_listbox.insert(tk.END, f"{name} - ₹{credit:,.2f}")
            except:
                pass
    def update_dashboard_stats(self):
        """Update dashboard statistics without destroying widgets"""
        try:
            if hasattr(self, 'stat_labels') and self.stat_labels:
                if "आजची विक्री" in self.stat_labels:
                    self.stat_labels["आजची विक्री"].config(text=f"₹{self.get_today_sales():,.2f}")
                if "आजची खरेदी" in self.stat_labels:
                    self.stat_labels["आजची खरेदी"].config(text=f"₹{self.get_today_purchases():,.2f}")
                if "एकूण स्टॉक" in self.stat_labels:
                    self.stat_labels["एकूण स्टॉक"].config(text=f"{self.get_total_stock()} आयटम्स")
                if "एकूण ग्राहक" in self.stat_labels:
                    self.stat_labels["एकूण ग्राहक"].config(text=f"{self.get_total_customers()} जण")
                if "एकूण उदारी" in self.stat_labels:
                    self.stat_labels["एकूण उदारी"].config(text=f"₹{self.get_total_credit():,.2f}")
                if "महिन्याची वाढ" in self.stat_labels:
                    self.stat_labels["महिन्याची वाढ"].config(text=f"+{self.get_monthly_growth():.1f}%")
        except Exception as e:
            print(f"Error updating dashboard stats: {e}")
        self.refresh_low_stock_panel()
        self.refresh_high_credit_panel()
    def load_shop_info(self):
        try:
            self.db.cursor.execute("SELECT shop_name FROM shop_info LIMIT 1")
            result = self.db.cursor.fetchone()
            self.shop_name = result[0] if result else "माय शॉप"
        except:
            self.shop_name = "माय शॉप"
    def focus_next_widget(self, event):
        event.widget.tk_focusNext().focus()
        return "break"
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    def setup_ui(self):
        main_container = tk.Frame(self.root, bg='white')
        main_container.pack(fill=tk.BOTH, expand=True)
        self.setup_title_bar(main_container)
        self.setup_main_area(main_container)
        self.setup_status_bar()
        self.root.bind('<Control-q>', lambda e: self.root.quit())
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    def setup_title_bar(self, parent):
        title_bar = tk.Frame(parent, bg='#1a1a2e', height=50)
        title_bar.pack(fill=tk.X, pady=(0, 2))
        left_frame = tk.Frame(title_bar, bg='#1a1a2e')
        left_frame.pack(side=tk.LEFT, padx=15)
        tk.Label(left_frame, text="🏪", bg='#1a1a2e', 
                fg='#e94560', font=('Arial', 24)).pack(side=tk.LEFT)
        shop_info = tk.Frame(left_frame, bg='#1a1a2e')
        shop_info.pack(side=tk.LEFT, padx=10)
        tk.Label(shop_info, text=self.shop_name, 
                bg='#1a1a2e', fg='white', 
                font=('Arial', 14, 'bold')).pack()
        tk.Label(shop_info, text="दुकान व्यवस्थापन सॉफ्टवेअर", 
                bg='#1a1a2e', fg='#e94560',
                font=('Arial', 12)).pack()
        center_frame = tk.Frame(title_bar, bg='#1a1a2e')
        center_frame.pack(side=tk.LEFT, expand=True)
        self.datetime_label = tk.Label(center_frame, 
                                      bg='#1a1a2e', fg='#f0a500',
                                      font=('Arial', 12))
        self.datetime_label.pack()
        right_frame = tk.Frame(title_bar, bg='#1a1a2e')
        right_frame.pack(side=tk.RIGHT, padx=15)
        tk.Label(right_frame, text=f"👤 {self.username}", 
                bg='#1a1a2e', fg='white',
                font=('Arial', 11)).pack(side=tk.RIGHT, padx=10)
    def setup_main_area(self, parent):
        notebook_frame = tk.Frame(parent, bg='white')
        notebook_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=0, pady=0)
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Custom.TNotebook', 
                       background='#16213e', 
                       borderwidth=0)
        style.configure('Custom.TNotebook.Tab', 
                       background='#0f3460', 
                       foreground='white',
                       padding=[15, 5],
                       font=('Arial', 10, 'bold'))
        style.map('Custom.TNotebook.Tab', 
                 background=[('selected', '#e94560')],
                 foreground=[('selected', 'white')])
        self.notebook = ttk.Notebook(notebook_frame, style='Custom.TNotebook')
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        self.create_tabs()
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_changed)
    def on_tab_changed(self, event):
        self.current_tab = self.notebook.index(self.notebook.select())
        if self.current_tab == 0:  # Dashboard
            self.update_dashboard_stats()  # येथे बदल
        elif self.current_tab == 1:  # Sales
            self.refresh_sales_tab()
        elif self.current_tab == 2:  # Purchases
            self.refresh_purchases_tab()
        elif self.current_tab == 3:  # Stock
            self.refresh_stock_tab()
        elif self.current_tab == 4:  # Accounts
            self.refresh_accounts_tab()
        elif self.current_tab == 5:  # Reports
            self.refresh_reports_tab()
        elif self.current_tab == 6:  # Settings
            self.refresh_settings_tab()
    def create_tabs(self):
        dashboard_frame = tk.Frame(self.notebook, bg='#f8f9fa')
        self.notebook.add(dashboard_frame, text="  डॅशबोर्ड  ")
        self.setup_dashboard_content(dashboard_frame)
        sales_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(sales_frame, text="  नवीन विक्री  ")
        self.setup_sales_content(sales_frame)
        purchase_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(purchase_frame, text="  नवीन खरेदी  ")
        self.setup_purchase_content(purchase_frame)
        stock_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(stock_frame, text="  स्टॉक व्यवस्थापन  ")
        self.setup_stock_content(stock_frame)
        accounts_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(accounts_frame, text="  खाते व्यवस्थापन  ")
        self.setup_accounts_content(accounts_frame)
        reports_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(reports_frame, text="  अहवाल  ")
        self.setup_reports_content(reports_frame)
        settings_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(settings_frame, text="  सेटिंग  ")
        self.setup_settings_content(settings_frame)
    def setup_dashboard_content(self, parent):
        main_container = tk.Frame(parent, bg='#f8f9fa')
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        main_container.grid_rowconfigure(0, weight=0)  # Header
        main_container.grid_rowconfigure(1, weight=1)  # Stats frame
        main_container.grid_rowconfigure(2, weight=2)  # Bottom container
        main_container.grid_columnconfigure(0, weight=1)
        header = tk.Frame(main_container, bg='#f8f9fa')
        header.grid(row=0, column=0, sticky='ew', pady=(0, 20))
        header.grid_columnconfigure(0, weight=1)
        tk.Label(header, text="डॅशबोर्ड", bg='#f8f9fa', 
                fg='#1a1a2e', font=('Arial', 24, 'bold')).pack(side=tk.LEFT)
        stats_frame = tk.Frame(main_container, bg='#f8f9fa')
        stats_frame.grid(row=1, column=0, sticky='nsew', pady=(0, 20))
        stats_frame.grid_rowconfigure(0, weight=1, uniform="stats_row")
        stats_frame.grid_rowconfigure(1, weight=1, uniform="stats_row")
        stats_frame.grid_columnconfigure(0, weight=1, uniform="stats_col")
        stats_frame.grid_columnconfigure(1, weight=1, uniform="stats_col")
        stats_frame.grid_columnconfigure(2, weight=1, uniform="stats_col")
        self.stats_frame = stats_frame
        self.stat_labels = {}
        stats = [
            ("💰", "आजची विक्री", f"₹{self.get_today_sales():,.2f}", "#e94560"),
            ("🛒", "आजची खरेदी", f"₹{self.get_today_purchases():,.2f}", "#0fcea7"),
            ("📦", "एकूण स्टॉक", f"{self.get_total_stock()} आयटम्स", "#f0a500"),
            ("👥", "एकूण ग्राहक", f"{self.get_total_customers()} जण", "#4cc9f0"),
            ("💳", "एकूण उदारी", f"₹{self.get_total_credit():,.2f}", "#7209b7"),
            ("📈", "महिन्याची वाढ", f"+{self.get_monthly_growth():.1f}%", "#3a86ff")
        ]
        for i, (icon, title, value, color) in enumerate(stats):
            card = self.create_stat_card(stats_frame, icon, title, value, color)
            card.grid(row=i//3, column=i%3, padx=5, pady=5, sticky='nsew')
        bottom_container = tk.Frame(main_container, bg='#f8f9fa')
        bottom_container.grid(row=2, column=0, sticky='nsew')
        bottom_container.grid_columnconfigure(0, weight=1, uniform="bottom_col")
        bottom_container.grid_columnconfigure(1, weight=1, uniform="bottom_col")
        bottom_container.grid_rowconfigure(0, weight=1)
        left_panel = tk.Frame(bottom_container, bg='#f8f9fa')
        left_panel.grid(row=0, column=0, sticky='nsew', padx=(0, 5))
        left_panel.grid_rowconfigure(0, weight=1)
        left_panel.grid_columnconfigure(0, weight=1)
        right_panel = tk.Frame(bottom_container, bg='#f8f9fa')
        right_panel.grid(row=0, column=1, sticky='nsew')
        right_panel.grid_rowconfigure(0, weight=1)
        right_panel.grid_columnconfigure(0, weight=1)
        self.setup_low_stock_panel(left_panel)
        self.setup_high_credit_panel(right_panel)
    def get_today_sales(self):
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            self.db.cursor.execute("SELECT SUM(total_amount) FROM sales WHERE DATE(date) = ?", (today,))
            result = self.db.cursor.fetchone()
            return result[0] or 0
        except:
            return 0
    def get_today_purchases(self):
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            self.db.cursor.execute("SELECT SUM(total_amount) FROM purchases WHERE DATE(date) = ?", (today,))
            result = self.db.cursor.fetchone()
            return result[0] or 0
        except:
            return 0
    def get_total_stock(self):
        try:
            self.db.cursor.execute("SELECT SUM(stock) FROM products")
            result = self.db.cursor.fetchone()
            return result[0] or 0
        except:
            return 0
    def get_total_customers(self):
        try:
            self.db.cursor.execute("SELECT COUNT(*) FROM customers WHERE name NOT LIKE 'CUST-%'")
            result = self.db.cursor.fetchone()
            return result[0] or 0
        except:
            return 0
    def get_total_credit(self):
        try:
            self.db.cursor.execute("SELECT SUM(credit_balance) FROM customers")
            result = self.db.cursor.fetchone()
            return result[0] or 0
        except:
            return 0
    def get_monthly_growth(self):
        try:
            current_month = datetime.now().strftime("%Y-%m")
            last_month = (datetime.now().replace(day=1) - timedelta(days=1)).strftime("%Y-%m")
            self.db.cursor.execute("SELECT SUM(total_amount) FROM sales WHERE strftime('%Y-%m', date) = ?", (current_month,))
            current = self.db.cursor.fetchone()[0] or 1
            self.db.cursor.execute("SELECT SUM(total_amount) FROM sales WHERE strftime('%Y-%m', date) = ?", (last_month,))
            last = self.db.cursor.fetchone()[0] or 1
            return ((current - last) / last) * 100
        except:
            return 12.5
    def create_stat_card(self, parent, icon, title, value, color):
        card = tk.Frame(parent, bg='white', relief=tk.RAISED, bd=1)
        card.grid_rowconfigure(0, weight=1)
        card.grid_columnconfigure(0, weight=0)  # Icon column
        card.grid_columnconfigure(1, weight=1)  # Content column
        icon_label = tk.Label(card, text=icon, bg='white', 
                             font=('Arial', 24), fg=color)
        icon_label.grid(row=0, column=0, padx=(15, 10), pady=15, sticky='nsw')
        content_frame = tk.Frame(card, bg='white')
        content_frame.grid(row=0, column=1, sticky='nsew', pady=15)
        content_frame.grid_rowconfigure(0, weight=0)  # Title
        content_frame.grid_rowconfigure(1, weight=1)  # Value
        content_frame.grid_columnconfigure(0, weight=1)
        tk.Label(content_frame, text=title, bg='white', 
                fg='#666', font=('Arial', 10)).grid(row=0, column=0, sticky='w')
        value_label = tk.Label(content_frame, text=value, bg='white', 
                              fg='#333', font=('Arial', 14, 'bold'))
        value_label.grid(row=1, column=0, sticky='w')
        self.stat_labels[title] = value_label
        if "आजची विक्री" in title:
            self.today_sales_label = value_label
        elif "आजची खरेदी" in title:
            self.today_purchases_label = value_label
        elif "एकूण स्टॉक" in title:
            self.total_stock_label = value_label
        elif "एकूण ग्राहक" in title:
            self.total_customers_label = value_label
        elif "एकूण उदारी" in title:
            self.total_credit_label = value_label
        elif "महिन्याची वाढ" in title:
            self.monthly_growth_label = value_label
        return card
    def setup_low_stock_panel(self, parent):
        panel = tk.Frame(parent, bg='white', relief=tk.RAISED, bd=1)
        panel.pack(fill=tk.BOTH, expand=True)
        panel.grid_rowconfigure(0, weight=0)  # Header
        panel.grid_rowconfigure(1, weight=1)  # Listbox
        panel.grid_columnconfigure(0, weight=1)
        header = tk.Label(panel, text="⚠️ कमी स्टॉक उत्पादने", 
                         bg='#fff3cd', fg='#856404',
                         font=('Arial', 12, 'bold'))
        header.grid(row=0, column=0, sticky='ew', padx=10, pady=10)
        listbox = tk.Listbox(panel, bg='white', font=('Arial', 10))
        listbox.grid(row=1, column=0, sticky='nsew', padx=10, pady=(0, 10))
        self.low_stock_listbox = listbox
        try:
            self.db.cursor.execute('''
                SELECT name, stock, min_stock FROM products 
                WHERE stock <= min_stock AND stock > 0
                ORDER BY stock ASC
                LIMIT 10
            ''')
            products = self.db.cursor.fetchall()
            for product in products:
                name, stock, min_stock = product
                listbox.insert(tk.END, f"{name} - {stock} पीस (किमान: {min_stock})")
        except:
            pass
    def setup_high_credit_panel(self, parent):
        panel = tk.Frame(parent, bg='white', relief=tk.RAISED, bd=1)
        panel.pack(fill=tk.BOTH, expand=True)
        panel.grid_rowconfigure(0, weight=0)  # Header
        panel.grid_rowconfigure(1, weight=1)  # Listbox
        panel.grid_columnconfigure(0, weight=1)
        header = tk.Label(panel, text="💳 उच्च उदारी ग्राहक", 
                         bg='#d4edda', fg='#155724',
                         font=('Arial', 12, 'bold'))
        header.grid(row=0, column=0, sticky='ew', padx=10, pady=10)
        listbox = tk.Listbox(panel, bg='white', font=('Arial', 10))
        listbox.grid(row=1, column=0, sticky='nsew', padx=10, pady=(0, 10))
        self.high_credit_listbox = listbox
        try:
            self.db.cursor.execute('''
                SELECT name, credit_balance FROM customers 
                WHERE credit_balance > 0 AND name NOT LIKE 'CUST-%'
                ORDER BY credit_balance DESC
                LIMIT 10
            ''')
            customers = self.db.cursor.fetchall()
            for customer in customers:
                name, credit = customer
                listbox.insert(tk.END, f"{name} - ₹{credit:,.2f}")
        except:
            pass
    def setup_sales_content(self, parent):
        main_container = tk.LabelFrame(parent, text="💰 नवीन विक्री", bg='white', font=('Arial', 12, 'bold'), bd=2, relief=tk.GROOVE)
        main_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        main_container.grid_rowconfigure(0, weight=0)  # हेडर फ्रेम
        main_container.grid_rowconfigure(1, weight=1)  # मुख्य फ्रेम
        main_container.grid_columnconfigure(0, weight=1)
        header_frame = tk.Frame(main_container, bg='white')
        header_frame.grid(row=0, column=0, sticky='ew', pady=(0, 15), padx=10)
        tk.Label(header_frame, text="💰 नवीन विक्री", 
                font=('Arial', 20, 'bold'), bg='white').pack(side=tk.LEFT)
        main_frame = tk.Frame(main_container, bg='white')
        main_frame.grid(row=1, column=0, sticky='nsew', padx=10, pady=10)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)  # डावा पॅनेल
        main_frame.grid_columnconfigure(1, weight=2)  # उजवा पॅनेल (जास्त जागा)
        left_panel = tk.LabelFrame(main_frame, text="उत्पादन माहिती", bg='white', font=('Arial', 10, 'bold'), bd=1, relief=tk.GROOVE)
        left_panel.grid(row=0, column=0, sticky='nsew', padx=(0, 10))
        for i in range(12):  # 12 रोसाठी (0-11)
            left_panel.grid_rowconfigure(i, weight=0)
        left_panel.grid_columnconfigure(0, weight=0)  # लेबल स्तंभ
        left_panel.grid_columnconfigure(1, weight=1)  # इंट्री/कॉम्बो स्तंभ
        tk.Label(left_panel, text="तारीख:", bg='white', font=('Arial', 10)).grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.sales_date_entry = DateEntry(left_panel, width=15, font=('Arial', 10), date_pattern='dd/mm/yyyy')
        self.sales_date_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        self.sales_date_entry.bind('<Return>', lambda e: self.customer_combo.focus())
        tk.Label(left_panel, text="ग्राहक:", bg='white', font=('Arial', 10)).grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.customer_combo = ttk.Combobox(left_panel, font=('Arial', 10))
        self.customer_combo.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        self.customer_combo.bind('<Return>', lambda e: self.barcode_search_entry.focus())
        self.customer_combo.bind('<FocusOut>', lambda e: self.add_customer_if_new())
        tk.Label(left_panel, text="बारकोड:", bg='white', font=('Arial', 10)).grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.barcode_search_entry = tk.Entry(left_panel, font=('Arial', 10))
        self.barcode_search_entry.grid(row=2, column=1, padx=5, pady=5, sticky='ew')
        self.barcode_search_entry.bind('<KeyRelease>', lambda e: self.auto_search_barcode())
        self.barcode_search_entry.bind('<Return>', lambda e: self.sales_category_combo.focus())
        tk.Label(left_panel, text="कॅटेगिरी:", bg='white', font=('Arial', 10)).grid(row=3, column=0, padx=5, pady=5, sticky='w')
        self.sales_category_combo = ttk.Combobox(left_panel, font=('Arial', 10))
        self.sales_category_combo.grid(row=3, column=1, padx=5, pady=5, sticky='ew')
        self.sales_category_combo.bind('<<ComboboxSelected>>', lambda e: self.load_products_by_category())
        self.sales_category_combo.bind('<Return>', lambda e: self.product_combo.focus())
        tk.Label(left_panel, text="उत्पादन:", bg='white', font=('Arial', 10)).grid(row=4, column=0, padx=5, pady=5, sticky='w')
        self.product_combo = ttk.Combobox(left_panel, font=('Arial', 10))
        self.product_combo.grid(row=4, column=1, padx=5, pady=5, sticky='ew')
        self.product_combo.bind('<<ComboboxSelected>>', lambda e: self.load_product_details())
        self.product_combo.bind('<Return>', lambda e: self.available_stock_label.focus())
        tk.Label(left_panel, text="उपलब्ध स्टॉक:", bg='white', font=('Arial', 10)).grid(row=5, column=0, padx=5, pady=5, sticky='w')
        self.available_stock_label = tk.Label(left_panel, text="0", bg='white', font=('Arial', 10))
        self.available_stock_label.grid(row=5, column=1, padx=5, pady=5, sticky='w')
        tk.Label(left_panel, text="खरेदी किंमत:", bg='white', font=('Arial', 10)).grid(row=6, column=0, padx=5, pady=5, sticky='w')
        self.purchase_price_label = tk.Label(left_panel, text="₹0.00", bg='white', font=('Arial', 10))
        self.purchase_price_label.grid(row=6, column=1, padx=5, pady=5, sticky='w')
        tk.Label(left_panel, text="विक्री किंमत:", bg='white', font=('Arial', 10)).grid(row=7, column=0, padx=5, pady=5, sticky='w')
        self.price_label = tk.Label(left_panel, text="₹0.00", bg='white', font=('Arial', 10))
        self.price_label.grid(row=7, column=1, padx=5, pady=5, sticky='w')
        tk.Label(left_panel, text="नग:", bg='white', font=('Arial', 10)).grid(row=8, column=0, padx=5, pady=5, sticky='w')
        self.quantity_entry = tk.Entry(left_panel, font=('Arial', 10))
        self.quantity_entry.grid(row=8, column=1, padx=5, pady=5, sticky='ew')
        self.quantity_entry.insert(0, "1")
        self.quantity_entry.bind('<KeyRelease>', lambda e: self.calculate_item_total())
        self.quantity_entry.bind('<Return>', lambda e: self.add_product_to_cart())
        tk.Label(left_panel, text="एकूण:", bg='white', font=('Arial', 10)).grid(row=9, column=0, padx=5, pady=5, sticky='w')
        self.item_total_label = tk.Label(left_panel, text="₹0.00", bg='white', font=('Arial', 10))
        self.item_total_label.grid(row=9, column=1, padx=5, pady=5, sticky='w')
        add_to_cart_btn = tk.Button(left_panel, text="➕ कार्टमध्ये ऍड", bg='#3a86ff', fg='white',
                                  font=('Arial', 10), command=self.add_product_to_cart)
        add_to_cart_btn.grid(row=10, column=0, columnspan=2, pady=10, sticky='ew')
        right_panel = tk.Frame(main_frame, bg='white')
        right_panel.grid(row=0, column=1, sticky='nsew')
        right_panel.grid_rowconfigure(0, weight=1)  # कार्ट फ्रेम
        right_panel.grid_rowconfigure(1, weight=0)  # बिल फ्रेम
        right_panel.grid_columnconfigure(0, weight=1)
        cart_frame = tk.LabelFrame(right_panel, text="विक्री कार्ट", bg='white', font=('Arial', 10, 'bold'), bd=1, relief=tk.GROOVE)
        cart_frame.grid(row=0, column=0, sticky='nsew', pady=(0, 10))
        cart_frame.grid_rowconfigure(0, weight=1)
        cart_frame.grid_columnconfigure(0, weight=1)
        columns = ('क्रमांक', 'उत्पादन', 'किंमत', 'प्रमाण', 'एकूण', 'काढा')
        self.cart_tree = ttk.Treeview(cart_frame, columns=columns, show='headings', height=10)
        column_widths = [50, 150, 80, 80, 100, 80]
        for i, (col, width) in enumerate(zip(columns, column_widths)):
            self.cart_tree.heading(col, text=col)
            self.cart_tree.column(col, width=width, anchor='center')
        self.cart_tree.bind('<Double-1>', self.delete_cart_item)
        scrollbar = ttk.Scrollbar(cart_frame, orient=tk.VERTICAL, command=self.cart_tree.yview)
        self.cart_tree.configure(yscrollcommand=scrollbar.set)
        self.cart_tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')
        bill_frame = tk.LabelFrame(right_panel, text="बिल माहिती", bg='white', font=('Arial', 10, 'bold'), bd=1, relief=tk.GROOVE)
        bill_frame.grid(row=1, column=0, sticky='ew')
        for i in range(7):  # 7 रोसाठी (0-6)
            bill_frame.grid_rowconfigure(i, weight=0)
        bill_frame.grid_columnconfigure(0, weight=0)  # लेबल स्तंभ
        bill_frame.grid_columnconfigure(1, weight=1)  # मूल्य स्तंभ
        tk.Label(bill_frame, text="एकूण बिल:", bg='white', font=('Arial', 11)).grid(row=0, column=0, padx=10, pady=5, sticky='w')
        self.total_amount_label = tk.Label(bill_frame, text="₹0.00", bg='white', font=('Arial', 11, 'bold'), fg='#0fcea7')
        self.total_amount_label.grid(row=0, column=1, padx=10, pady=5, sticky='w')
        tk.Label(bill_frame, text="सवलत:", bg='white', font=('Arial', 11)).grid(row=1, column=0, padx=10, pady=5, sticky='w')
        discount_frame = tk.Frame(bill_frame, bg='white')
        discount_frame.grid(row=1, column=1, padx=10, pady=5, sticky='w')
        discount_frame.grid_columnconfigure(0, weight=1)
        discount_frame.grid_columnconfigure(1, weight=0)
        self.discount_entry = tk.Entry(discount_frame, width=10, font=('Arial', 10))
        self.discount_entry.grid(row=0, column=0, sticky='ew')
        self.discount_entry.insert(0, "0")
        self.discount_entry.bind('<KeyRelease>', lambda e: self.calculate_sale_total())
        self.discount_entry.bind('<Return>', lambda e: self.discount_type.focus())
        self.discount_type = ttk.Combobox(discount_frame, values=['₹', '%'], width=5, state='readonly', font=('Arial', 10))
        self.discount_type.grid(row=0, column=1, padx=5, sticky='ew')
        self.discount_type.current(0)
        self.discount_type.bind('<<ComboboxSelected>>', lambda e: self.calculate_sale_total())
        self.discount_type.bind('<Return>', lambda e: self.final_total_label.focus())
        tk.Label(bill_frame, text="सवलतीनंतर बिल:", bg='white', font=('Arial', 11)).grid(row=2, column=0, padx=10, pady=5, sticky='w')
        self.final_total_label = tk.Label(bill_frame, text="₹0.00", bg='white', font=('Arial', 11, 'bold'), fg='#f0a500')
        self.final_total_label.grid(row=2, column=1, padx=10, pady=5, sticky='w')
        tk.Label(bill_frame, text="जमा रक्कम:", bg='white', font=('Arial', 11)).grid(row=3, column=0, padx=10, pady=5, sticky='w')
        self.paid_amount_entry = tk.Entry(bill_frame, width=15, font=('Arial', 10))
        self.paid_amount_entry.grid(row=3, column=1, padx=10, pady=5, sticky='ew')
        self.paid_amount_entry.bind('<KeyRelease>', lambda e: self.update_payment_mode())
        self.paid_amount_entry.bind('<Return>', lambda e: self.payment_mode.focus())
        tk.Label(bill_frame, text="बाकी रक्कम:", bg='white', font=('Arial', 11)).grid(row=4, column=0, padx=10, pady=5, sticky='w')
        self.balance_label = tk.Label(bill_frame, text="₹0.00", bg='white', font=('Arial', 11, 'bold'), fg='#7209b7')
        self.balance_label.grid(row=4, column=1, padx=10, pady=5, sticky='w')
        tk.Label(bill_frame, text="पेमेंट मोड:", bg='white', font=('Arial', 11)).grid(row=5, column=0, padx=10, pady=5, sticky='w')
        self.payment_mode = ttk.Combobox(bill_frame, values=['रोख', 'UPI', 'उदारी', 'आंशिक जमा'], width=15, state='readonly', font=('Arial', 10))
        self.payment_mode.grid(row=5, column=1, padx=10, pady=5, sticky='ew')
        self.payment_mode.current(0)
        self.payment_mode.bind('<Return>', lambda e: self.save_sale())
        button_frame = tk.Frame(bill_frame, bg='white')
        button_frame.grid(row=6, column=0, columnspan=2, pady=10, sticky='ew')
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        save_btn = tk.Button(button_frame, text="💰 विक्री नोंदवा", bg='#0fcea7', fg='white',
                           font=('Arial', 12, 'bold'), command=self.save_sale)
        save_btn.grid(row=0, column=0, padx=(0, 5), sticky='ew')
        clear_btn = tk.Button(button_frame, text="🗑️ कार्ट क्लिअर करा", bg='#e94560', fg='white',
                            font=('Arial', 12), command=self.clear_sale_cart)
        clear_btn.grid(row=0, column=1, padx=(5, 0), sticky='ew')
        self.load_categories_for_sale()
        self.load_customers_for_sale()
        self.generate_default_customer()
        self.calculate_sale_total()
    def refresh_sales_tab(self):
        self.load_categories_for_sale()
        self.load_customers_for_sale()
        self.generate_default_customer()
        self.clear_sale_cart()
    def load_categories_for_sale(self):
        try:
            self.db.cursor.execute("SELECT DISTINCT category FROM products WHERE category IS NOT NULL AND category != '' ORDER BY category")
            categories = [row[0] for row in self.db.cursor.fetchall()]
            self.sales_category_combo['values'] = categories
        except:
            self.sales_category_combo['values'] = []
    def load_products_by_category(self):
        category = self.sales_category_combo.get()
        if category:
            try:
                self.db.cursor.execute("SELECT name FROM products WHERE category = ? ORDER BY name", (category,))
                products = [row[0] for row in self.db.cursor.fetchall()]
                self.product_combo['values'] = products
            except:
                self.product_combo['values'] = []
        else:
            self.product_combo['values'] = []
    def load_product_details(self):
        product_name = self.product_combo.get()
        if product_name:
            try:
                self.db.cursor.execute("SELECT sale_price, stock, purchase_price FROM products WHERE name = ?", (product_name,))
                result = self.db.cursor.fetchone()
                if result:
                    price, stock, purchase_price = result
                    self.price_label.config(text=f"₹{price:.2f}")
                    self.purchase_price_label.config(text=f"₹{purchase_price:.2f}")
                    self.available_stock_label.config(text=str(stock))
                    self.calculate_item_total()
            except:
                pass
    def generate_default_customer(self):
        unique_id = datetime.now().strftime('%Y%m%d%H%M%S')
        customer_name = f"CUST-{unique_id}"
        self.customer_combo.set(customer_name)
    def auto_search_barcode(self):
        barcode = self.barcode_search_entry.get().strip()
        if barcode:
            try:
                self.db.cursor.execute("SELECT name FROM products WHERE barcode = ?", (barcode,))
                result = self.db.cursor.fetchone()
                if result:
                    product_name = result[0]
                    self.product_combo.set(product_name)
                    self.load_product_details()
            except:
                pass
    def calculate_item_total(self):
        try:
            price_text = self.price_label.cget("text").replace('₹', '')
            price = float(price_text)
            quantity = int(self.quantity_entry.get())
            total = price * quantity
            self.item_total_label.config(text=f"₹{total:.2f}")
        except:
            self.item_total_label.config(text="₹0.00")
    def add_product_to_cart(self):
        product_name = self.product_combo.get()
        if not product_name:
            self.show_messagebox("त्रुटी", "कृपया उत्पादन निवडा")
            return
        try:
            available_stock = int(self.available_stock_label.cget("text"))
            price_text = self.price_label.cget("text").replace('₹', '')
            price = float(price_text)
            quantity = int(self.quantity_entry.get())
            if quantity > available_stock:
                self.show_messagebox("त्रुटी", f"स्टॉक अपुरा! उपलब्ध: {available_stock}")
                return
            total = price * quantity
            cart_item = {
                'name': product_name,
                'price': price,
                'quantity': quantity,
                'total': total
            }
            self.sale_cart.append(cart_item)
            cart_values = (
                len(self.sale_cart),
                product_name,
                f"₹{price:.2f}",
                quantity,
                f"₹{total:.2f}",
                "❌ काढा"
            )
            self.cart_tree.insert('', tk.END, values=cart_values)
            self.calculate_sale_total()
            self.quantity_entry.delete(0, tk.END)
            self.quantity_entry.insert(0, "1")
            self.item_total_label.config(text="₹0.00")
            self.product_combo.set('')
            self.price_label.config(text="₹0.00")
            self.purchase_price_label.config(text="₹0.00")
            self.available_stock_label.config(text="0")
            self.barcode_search_entry.delete(0, tk.END)
        except ValueError:
            self.show_messagebox("त्रुटी", "कृपया वैध प्रमाण प्रविष्ट करा")
    def delete_cart_item(self, event):
        item = self.cart_tree.identify_row(event.y)
        column = self.cart_tree.identify_column(event.x)
        if item and column == '#6':
            selected_item = self.cart_tree.selection()[0]
            index = int(self.cart_tree.item(selected_item, 'values')[0]) - 1
            self.sale_cart.pop(index)
            self.cart_tree.delete(selected_item)
            self.refresh_cart_indexes()
            self.calculate_sale_total()
    def refresh_cart_indexes(self):
        for i, item in enumerate(self.cart_tree.get_children(), 1):
            values = list(self.cart_tree.item(item, 'values'))
            values[0] = i
            self.cart_tree.item(item, values=values)
    def calculate_sale_total(self):
        total = sum(item['total'] for item in self.sale_cart)
        discount_text = self.discount_entry.get()
        discount_type = self.discount_type.get()
        discount = 0
        try:
            if discount_text:
                if discount_type == '₹':
                    discount = float(discount_text)
                else:
                    discount = total * (float(discount_text) / 100)
        except:
            discount = 0
        final_total = total - discount
        self.total_amount_label.config(text=f"₹{total:.2f}")
        self.final_total_label.config(text=f"₹{final_total:.2f}")
        if self.sale_cart:
            current_paid = self.paid_amount_entry.get()
            try:
                current_paid_value = float(current_paid) if current_paid else 0
                if abs(current_paid_value - final_total) > 0.01:  # छोट्या फरकासाठी tolerance
                    self.paid_amount_entry.delete(0, tk.END)
                    self.paid_amount_entry.insert(0, str(final_total))
                    current_paid_value = final_total
            except:
                self.paid_amount_entry.delete(0, tk.END)
                self.paid_amount_entry.insert(0, str(final_total))
                current_paid_value = final_total
            balance = final_total - current_paid_value
            if balance < 0:
                balance = 0
            self.balance_label.config(text=f"₹{balance:.2f}")
            if current_paid_value == final_total:
                self.payment_mode.set('रोख')
            else:
                self.payment_mode.set('आंशिक जमा')
        else:
            self.paid_amount_entry.delete(0, tk.END)
            self.paid_amount_entry.insert(0, "0")
            self.balance_label.config(text="₹0.00")
            self.payment_mode.set('रोख')
    def update_payment_mode(self):
        paid_text = self.paid_amount_entry.get()
        final_total_text = self.final_total_label.cget("text").replace('₹', '').replace(',', '')
        try:
            paid = float(paid_text) if paid_text else 0
            final_total = float(final_total_text)
            if paid == final_total:
                self.payment_mode.set('रोख')
            elif paid == 0:
                self.payment_mode.set('उदारी')
            elif paid < final_total:
                self.payment_mode.set('आंशिक जमा')
            else:
                self.payment_mode.set('रोख')
            balance = final_total - paid
            if balance < 0:
                balance = 0
            self.balance_label.config(text=f"₹{balance:.2f}")
        except:
            self.payment_mode.set('रोख')
            self.balance_label.config(text="₹0.00")
    def save_sale(self):
        customer_name = self.customer_combo.get()
        payment_mode = self.payment_mode.get()
        if not customer_name:
            self.show_messagebox("त्रुटी", "कृपया ग्राहक नाव प्रविष्ट करा")
            return
        if not self.sale_cart:
            self.show_messagebox("त्रुटी", "कार्ट रिकामा आहे")
            return
        self.add_customer_if_new()   
        total = sum(item['total'] for item in self.sale_cart)
        discount_text = self.discount_entry.get()
        discount_type = self.discount_type.get()
        discount = 0
        try:
            if discount_text:
                if discount_type == '₹':
                    discount = float(discount_text)
                else:
                    discount = total * (float(discount_text) / 100)
        except:
            discount = 0
        final_total = total - discount
        paid_text = self.paid_amount_entry.get()
        try:
            paid = float(paid_text) if paid_text else 0
        except:
            paid = 0
        balance = final_total - paid
        if balance < 0:
            balance = 0
        if customer_name.startswith('CUST-') and balance > 0:
            self.show_messagebox("त्रुटी", "डिफॉल्ट ग्राहकाला उधारी देता येणार नाही")
            return
        try:
            invoice_no = f"SALE-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            if balance == 0:
                status = 'पूर्ण'
            elif paid == 0:
                status = 'उदारी'
            else:
                status = 'आंशिक जमा'
            self.db.cursor.execute('''
                INSERT INTO sales (invoice_no, customer_name, date, total_amount, 
                                 discount_amount, discount_type, paid_amount, 
                                 balance_amount, payment_mode, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                invoice_no,
                customer_name,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                total,
                discount,
                discount_type,
                paid,
                balance,
                payment_mode,
                status
            ))
            sale_id = self.db.cursor.lastrowid
            for item in self.sale_cart:
                self.db.cursor.execute("SELECT id FROM products WHERE name = ?", (item['name'],))
                product_result = self.db.cursor.fetchone()
                product_id = product_result[0] if product_result else None
                self.db.cursor.execute('''
                    INSERT INTO sale_items (sale_id, product_id, product_name, 
                                          quantity, price, total)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    sale_id,
                    product_id,
                    item['name'],
                    item['quantity'],
                    item['price'],
                    item['total']
                ))
                if product_id:
                    self.db.cursor.execute('''
                        UPDATE products SET stock = stock - ? WHERE id = ?
                    ''', (item['quantity'], product_id))
            if balance > 0:
                if not customer_name.startswith('CUST-'):
                    self.db.cursor.execute('''
                        UPDATE customers SET credit_balance = credit_balance + ? 
                        WHERE name = ?
                    ''', (balance, customer_name))
                else:
                    self.db.cursor.execute('''
                        UPDATE customers SET credit_balance = 0 
                        WHERE name = ?
                    ''', (customer_name,))
            self.db.conn.commit()
            self.last_sale_id = sale_id
            self.show_bill_print_window(invoice_no, customer_name, total, discount, final_total, paid, balance, payment_mode)
        except Exception as e:
            self.show_messagebox("त्रुटी", f"विक्री सेव त्रुटी: {str(e)}")
    def clear_sale_cart(self):
        self.sale_cart = []
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
        self.total_amount_label.config(text="₹0.00")
        self.final_total_label.config(text="₹0.00")
        self.balance_label.config(text="₹0.00")
        self.paid_amount_entry.delete(0, tk.END)
        self.paid_amount_entry.insert(0, "0")  # कार्ट रिकामा असल्यास 0
        self.discount_entry.delete(0, tk.END)
        self.discount_entry.insert(0, "0")
        self.discount_type.current(0)
        self.generate_default_customer()
        self.product_combo.set('')
        self.price_label.config(text="₹0.00")
        self.purchase_price_label.config(text="₹0.00")
        self.available_stock_label.config(text="0")
        self.quantity_entry.delete(0, tk.END)
        self.quantity_entry.insert(0, "1")
        self.item_total_label.config(text="₹0.00")
        self.sales_category_combo.set('')
        self.barcode_search_entry.delete(0, tk.END)
        self.payment_mode.set('रोख')  # डिफॉल्ट payment mode
    def show_bill_print_window(self, invoice_no, customer_name, total, discount, final_total, paid, balance, payment_mode):
        bill_window = tk.Toplevel(self.root)
        bill_window.title("बिल प्रिंट आणि पूर्वावलोकन")
        bill_window.geometry("500x700")  # 600x800 पासून 500x700 ला बदलले
        bill_window.configure(bg='#f0f0f0')
        bill_window.transient(self.root)
        bill_window.grab_set()
        self.center_dialog(bill_window)
        main_frame = tk.Frame(bill_window, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)  # padx 20 पासून 15 ला बदलले
        header_frame = tk.Frame(main_frame, bg='#ffffff', relief=tk.RAISED, bd=2)
        header_frame.pack(fill=tk.X, pady=(0, 10))  # pady 15 पासून 10 ला बदलले
        tk.Label(header_frame, text="📄 बिल पूर्वावलोकन", 
                bg='#ffffff', fg='#1a1a2e', 
                font=('Arial', 16, 'bold')).pack(pady=8)  # font size 18 पासून 16 ला बदलले
        preview_frame = tk.LabelFrame(main_frame, text="बिल तपशील", 
                                     bg='#ffffff', font=('Arial', 11, 'bold'),  # font size 12 पासून 11 ला बदलले
                                     bd=2, relief=tk.GROOVE)
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))  # pady 15 पासून 10 ला बदलले
        text_frame = tk.Frame(preview_frame, bg='#ffffff')
        text_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)  # padx 10 पासून 8 ला बदलले
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        bill_text = tk.Text(text_frame, bg='white', font=('Courier New', 10),  # font size 11 पासून 10 ला बदलले
                           height=20, yscrollcommand=scrollbar.set,  # height 25 पासून 20 ला बदलले
                           wrap=tk.WORD, relief=tk.FLAT, bd=1)
        bill_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=bill_text.yview)
        header_text = self.get_print_setting('header_text')
        footer_text = self.get_print_setting('footer_text')
        bill_content = "="*50 + "\n"  # 60 पासून 50 ला बदलले
        if header_text:
            bill_content += f"{header_text:^50}\n"
            bill_content += "="*50 + "\n"
        bill_content += f"{self.shop_name:^50}\n"
        bill_content += "="*50 + "\n"
        bill_content += f"{'बिल क्रमांक:':<18} {invoice_no}\n"  # 20 पासून 18 ला बदलले
        bill_content += f"{'तारीख:':<18} {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
        bill_content += f"{'ग्राहक:':<18} {customer_name}\n"
        bill_content += "-"*50 + "\n"
        bill_content += f"{'उत्पादन':<25} {'नग':<6} {'दर':<8} {'एकूण':<10}\n"  # column widths कमी केले
        bill_content += "-"*50 + "\n"
        for item in self.sale_cart:
            product_name = item['name'][:23]  # 28 पासून 23 ला बदलले
            quantity = str(item['quantity'])
            price = f"₹{item['price']:.2f}"
            item_total = f"₹{item['total']:.2f}"
            bill_content += f"{product_name:<25} {quantity:<6} {price:<8} {item_total:<10}\n"
        bill_content += "="*50 + "\n"
        bill_content += f"{'एकूण बिल:':<40} ₹{total:>10.2f}\n"  # 45 पासून 40 ला बदलले
        if discount > 0:
            bill_content += f"{'सवलत:':<40} ₹{discount:>10.2f}\n"
        bill_content += f"{'सवलतीनंतर बिल:':<40} ₹{final_total:>10.2f}\n"
        bill_content += f"{'जमा रक्कम:':<40} ₹{paid:>10.2f}\n"
        if balance > 0:
            bill_content += f"{'बाकी रक्कम:':<40} ₹{balance:>10.2f} (उधारी)\n"
        else:
            bill_content += f"{'बाकी रक्कम:':<40} ₹{balance:>10.2f}\n"
        bill_content += f"{'पेमेंट मोड:':<40} {payment_mode:>10}\n"
        bill_content += "="*50 + "\n"
        if footer_text:
            bill_content += f"{footer_text:^50}\n"
            bill_content += "="*50 + "\n"
        bill_content += f"{'धन्यवाद! पुन्हा भेट द्या!':^50}\n"
        bill_content += "="*50 + "\n"
        bill_text.insert(tk.END, bill_content)
        bill_text.tag_configure("header", foreground="#1a1a2e", font=('Courier New', 10, 'bold'))
        bill_text.tag_configure("total", foreground="#e94560", font=('Courier New', 10, 'bold'))
        bill_text.tag_configure("balance", foreground="#7209b7", font=('Courier New', 10, 'bold'))
        bill_text.tag_configure("thanks", foreground="#0fcea7", font=('Courier New', 10, 'bold'))
        lines = bill_content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith("=") or "बिल क्रमांक:" in line or "बिल पूर्वावलोकन" in line:
                bill_text.tag_add("header", f"{i+1}.0", f"{i+1}.end")
            elif "एकूण बिल:" in line or "सवलतीनंतर बिल:" in line:
                bill_text.tag_add("total", f"{i+1}.0", f"{i+1}.end")
            elif "बाकी रक्कम:" in line and "उधारी" in line:
                bill_text.tag_add("balance", f"{i+1}.0", f"{i+1}.end")
            elif "धन्यवाद" in line:
                bill_text.tag_add("thanks", f"{i+1}.0", f"{i+1}.end")
        bill_text.config(state=tk.DISABLED)
        status_frame = tk.Frame(main_frame, bg='#ffffff', relief=tk.RAISED, bd=1)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        tk.Label(status_frame, text=f"📋 एकूण उत्पादने: {len(self.sale_cart)} | 💰 एकूण रक्कम: ₹{final_total:.2f}", 
                bg='#ffffff', fg='#333333', font=('Arial', 10)).pack(pady=6)  # font size 11 पासून 10 ला बदलले
        button_frame = tk.Frame(main_frame, bg='#f0f0f0')
        button_frame.pack(fill=tk.X)
        button_subframe = tk.Frame(button_frame, bg='#f0f0f0')
        button_subframe.pack(expand=True)
        print_btn = tk.Button(button_subframe, text="🖨️ प्रिंट करा", bg='#0fcea7', fg='white',
                            font=('Arial', 11, 'bold'), padx=15, pady=8,  # padx 20 पासून 15 ला, pady 10 पासून 8 ला बदलले
                            command=lambda: self.print_bill_pdf(invoice_no, customer_name, total, discount, final_total, paid, balance, payment_mode, bill_window))
        print_btn.pack(side=tk.LEFT, padx=5)
        close_btn = tk.Button(button_subframe, text="✕ बंद करा", bg='#e94560', fg='white',
                            font=('Arial', 11, 'bold'), padx=15, pady=8,
                            command=lambda: self.close_bill_window(bill_window))
        close_btn.pack(side=tk.LEFT, padx=5)
        bill_window.bind('<Escape>', lambda e: self.close_bill_window(bill_window))
        bill_window.bind('<Return>', lambda e: self.print_bill_pdf(invoice_no, customer_name, total, discount, final_total, paid, balance, payment_mode, bill_window))
        bill_window.bind('<Control-p>', lambda e: self.print_bill_pdf(invoice_no, customer_name, total, discount, final_total, paid, balance, payment_mode, bill_window))
        print_btn.focus_set()
        bill_window.focus_set()
    def print_bill_pdf(self, invoice_no, customer_name, total, discount, final_total, paid, balance, payment_mode, bill_window):
        try:
            temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
            pdf_path = temp_file.name
            c = canvas.Canvas(pdf_path, pagesize=(3.5*inch, 11*inch))
            font_size_val = self.get_print_setting('font_size')
            if not font_size_val:
                font_size_val = 10
            c.setFont("Helvetica-Bold", font_size_val + 2)  # +3 पासून +2 ला बदलले
            y = 10.5*inch
            header_text = self.get_print_setting('header_text')
            if header_text:
                c.drawCentredString(1.75*inch, y, header_text)
                y -= 0.2*inch  # 0.25 पासून 0.2 ला बदलले
                c.setLineWidth(0.8)  # 1 पासून 0.8 ला बदलले
                c.line(0.5*inch, y, 3.0*inch, y)
                y -= 0.2*inch
            c.drawCentredString(1.75*inch, y, self.shop_name)
            y -= 0.2*inch
            c.setLineWidth(0.8)
            c.line(0.5*inch, y, 3.0*inch, y)
            y -= 0.25*inch
            c.setFont("Helvetica", font_size_val)
            c.drawString(0.5*inch, y, f"बिल क्रमांक: {invoice_no}")
            y -= 0.18*inch  # 0.2 पासून 0.18 ला बदलले
            c.drawString(0.5*inch, y, f"तारीख: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
            y -= 0.18*inch
            c.drawString(0.5*inch, y, f"ग्राहक: {customer_name}")
            y -= 0.18*inch
            c.setLineWidth(0.4)  # 0.5 पासून 0.4 ला बदलले
            c.line(0.5*inch, y, 3.0*inch, y)
            y -= 0.2*inch
            c.setFont("Helvetica-Bold", font_size_val)
            c.drawString(0.5*inch, y, "उत्पादन")
            c.drawString(2.2*inch, y, "नग")
            c.drawString(2.5*inch, y, "दर")
            c.drawRightString(3.0*inch, y, "एकूण")
            y -= 0.18*inch
            c.setLineWidth(0.25)  # 0.3 पासून 0.25 ला बदलले
            c.line(0.5*inch, y, 3.0*inch, y)
            y -= 0.18*inch
            c.setFont("Helvetica", font_size_val - 1)
            for item in self.sale_cart:
                if y < 1.5*inch:
                    c.showPage()
                    c.setFont("Helvetica", font_size_val - 1)
                    y = 10.5*inch
                product_name = item['name'][:18]  # 20 पासून 18 ला बदलले
                c.drawString(0.5*inch, y, product_name)
                c.drawString(2.2*inch, y, f"x{item['quantity']}")
                c.drawString(2.5*inch, y, f"₹{item['price']:.2f}")
                c.drawRightString(3.0*inch, y, f"₹{item['total']:.2f}")
                y -= 0.18*inch  # 0.2 पासून 0.18 ला बदलले
            y -= 0.18*inch
            c.setLineWidth(0.8)
            c.line(0.5*inch, y, 3.0*inch, y)
            y -= 0.2*inch
            c.setFont("Helvetica", font_size_val)
            c.drawString(0.5*inch, y, "एकूण बिल:")
            c.drawRightString(3.0*inch, y, f"₹{total:.2f}")
            y -= 0.18*inch
            if discount > 0:
                c.drawString(0.5*inch, y, "सवलत:")
                c.drawRightString(3.0*inch, y, f"₹{discount:.2f}")
                y -= 0.18*inch
            c.setFont("Helvetica-Bold", font_size_val + 1)
            c.drawString(0.5*inch, y, "सवलतीनंतर बिल:")
            c.drawRightString(3.0*inch, y, f"₹{final_total:.2f}")
            y -= 0.18*inch
            c.setFont("Helvetica", font_size_val)
            c.drawString(0.5*inch, y, f"जमा रक्कम: ₹{paid:.2f}")
            y -= 0.18*inch
            if balance > 0:
                c.setFont("Helvetica-Bold", font_size_val)
                c.drawString(0.5*inch, y, f"बाकी रक्कम: ₹{balance:.2f}")
                c.setFont("Helvetica", font_size_val - 1)
                c.drawString(0.5*inch, y-0.12*inch, "(उधारी)")  # 0.15 पासून 0.12 ला बदलले
                y -= 0.3*inch  # 0.35 पासून 0.3 ला बदलले
            else:
                c.drawString(0.5*inch, y, f"बाकी रक्कम: ₹{balance:.2f}")
                y -= 0.18*inch
            c.drawString(0.5*inch, y, f"पेमेंट: {payment_mode}")
            y -= 0.25*inch
            c.setLineWidth(0.8)
            c.line(0.5*inch, y, 3.0*inch, y)
            y -= 0.2*inch
            footer_text = self.get_print_setting('footer_text')
            if footer_text:
                c.setFont("Helvetica", font_size_val - 1)
                c.drawCentredString(1.75*inch, y, footer_text)
                y -= 0.18*inch
                c.setLineWidth(0.4)
                c.line(0.5*inch, y, 3.0*inch, y)
                y -= 0.18*inch
            c.setFont("Helvetica-Oblique", font_size_val)
            c.drawCentredString(1.75*inch, y, "धन्यवाद! पुन्हा भेट द्या!")
            c.save()
            if sys.platform == "win32":
                os.startfile(pdf_path, "print")
            elif sys.platform == "darwin":
                subprocess.Popen(['open', pdf_path])
            else:
                subprocess.Popen(['xdg-open', pdf_path])
            self.close_bill_window(bill_window)
        except Exception as e:
            self.show_messagebox("त्रुटी", f"बिल प्रिंट त्रुटी: {str(e)}")
    def close_bill_window(self, bill_window):
        bill_window.destroy()
        self.clear_sale_cart() 
    def get_print_setting(self, key):
        try:
            self.db.cursor.execute("SELECT " + key + " FROM print_settings LIMIT 1")
            result = self.db.cursor.fetchone()
            if result:
                return result[0]
        except:
            pass
        return None
    def load_customers_for_sale(self):
        try:
            self.db.cursor.execute("SELECT name FROM customers WHERE name NOT LIKE 'CUST-%' ORDER BY name")
            customers = [row[0] for row in self.db.cursor.fetchall()]
            self.customer_combo['values'] = customers
        except:
            self.customer_combo['values'] = []
    def add_customer_if_new(self):
        """जर ग्राहक नाव नवीन असेल तर customers टेबलमध्ये जोडा"""
        customer_name = self.customer_combo.get().strip()
        if not customer_name:
            return
        if customer_name.startswith('CUST-'):
            return
        current_values = list(self.customer_combo['values'])
        if customer_name in current_values:
            return
        try:
            self.db.cursor.execute('''
                INSERT INTO customers (name, phone, address, credit_balance, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                customer_name,
                '',
                '',
                0,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            self.db.conn.commit()
            self.load_customers_for_sale()
        except Exception as e:
            print(f"ग्राहक जोड त्रुटी: {str(e)}")
    def setup_purchase_content(self, parent):
        main_container = tk.LabelFrame(parent, text="🛒 नवीन खरेदी", bg='white', font=('Arial', 12, 'bold'), bd=2, relief=tk.GROOVE)
        main_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        main_container.grid_rowconfigure(0, weight=0)  # हेडर फ्रेम
        main_container.grid_rowconfigure(1, weight=1)  # मुख्य फ्रेम
        main_container.grid_columnconfigure(0, weight=1)
        header_frame = tk.Frame(main_container, bg='white')
        header_frame.grid(row=0, column=0, sticky='ew', pady=(0, 15), padx=10)
        tk.Label(header_frame, text="🛒 नवीन खरेदी", 
                font=('Arial', 20, 'bold'), bg='white').pack(side=tk.LEFT)
        main_frame = tk.Frame(main_container, bg='white')
        main_frame.grid(row=1, column=0, sticky='nsew', padx=10, pady=10)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)  # डावा पॅनेल
        main_frame.grid_columnconfigure(1, weight=2)  # उजवा पॅनेल (जास्त जागा)
        left_panel = tk.Frame(main_frame, bg='white')
        left_panel.grid(row=0, column=0, sticky='nsew', padx=(0, 10))
        left_panel.grid_rowconfigure(0, weight=0)  # पुरवठादार फ्रेम
        left_panel.grid_rowconfigure(1, weight=1)  # उत्पादन फ्रेम
        left_panel.grid_columnconfigure(0, weight=1)
        supplier_frame = tk.LabelFrame(left_panel, text="पुरवठादार माहिती", bg='white', font=('Arial', 10, 'bold'), bd=1, relief=tk.GROOVE)
        supplier_frame.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        for i in range(4):  # 4 रोसाठी
            supplier_frame.grid_rowconfigure(i, weight=0)
        supplier_frame.grid_columnconfigure(0, weight=0)  # लेबल स्तंभ
        supplier_frame.grid_columnconfigure(1, weight=1)  # इंट्री स्तंभ
        supplier_frame.grid_columnconfigure(2, weight=0)  # बटण स्तंभ
        tk.Label(supplier_frame, text="पुरवठादार:", bg='white', font=('Arial', 10)).grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.supplier_combo = ttk.Combobox(supplier_frame, font=('Arial', 10))
        self.supplier_combo.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        self.supplier_combo.bind('<<ComboboxSelected>>', lambda e: self.load_supplier_info())
        self.supplier_combo.bind('<Return>', lambda e: self.purchase_category_combo.focus())
        new_supplier_btn = tk.Button(supplier_frame, text="+ नवीन", bg='#0fcea7', fg='white',
                                    font=('Arial', 9), command=self.add_new_supplier_purchase)
        new_supplier_btn.grid(row=0, column=2, padx=5, pady=5)
        tk.Label(supplier_frame, text="फोन:", bg='white', font=('Arial', 10)).grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.supplier_phone_label = tk.Label(supplier_frame, text="", bg='white', font=('Arial', 10))
        self.supplier_phone_label.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        tk.Label(supplier_frame, text="उधारी:", bg='white', font=('Arial', 10)).grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.supplier_credit_label = tk.Label(supplier_frame, text="₹0.00", bg='white', font=('Arial', 10, 'bold'), fg='#e94560')
        self.supplier_credit_label.grid(row=2, column=1, padx=5, pady=5, sticky='w')
        product_frame = tk.LabelFrame(left_panel, text="उत्पादन माहिती", bg='white', font=('Arial', 10, 'bold'), bd=1, relief=tk.GROOVE)
        product_frame.grid(row=1, column=0, sticky='nsew')
        for i in range(12):  # 12 रोसाठी (0-11)
            product_frame.grid_rowconfigure(i, weight=0)
        product_frame.grid_columnconfigure(0, weight=0)  # लेबल स्तंभ
        product_frame.grid_columnconfigure(1, weight=1)  # इंट्री स्तंभ
        row_counter = 0
        tk.Label(product_frame, text="कॅटेगिरी:", bg='white', font=('Arial', 10)).grid(row=row_counter, column=0, padx=5, pady=5, sticky='w')
        self.purchase_category_combo = ttk.Combobox(product_frame, font=('Arial', 10))
        self.purchase_category_combo.grid(row=row_counter, column=1, padx=5, pady=5, sticky='ew')
        self.purchase_category_combo.bind('<<ComboboxSelected>>', lambda e: self.load_purchase_products_by_category())
        self.purchase_category_combo.bind('<Return>', lambda e: self.purchase_product_combo.focus())
        row_counter += 1
        tk.Label(product_frame, text="उत्पादन:", bg='white', font=('Arial', 10)).grid(row=row_counter, column=0, padx=5, pady=5, sticky='w')
        self.purchase_product_combo = ttk.Combobox(product_frame, font=('Arial', 10))
        self.purchase_product_combo.grid(row=row_counter, column=1, padx=5, pady=5, sticky='ew')
        self.purchase_product_combo.bind('<<ComboboxSelected>>', lambda e: self.load_purchase_product_details())
        self.purchase_product_combo.bind('<Return>', lambda e: self.purchase_barcode_entry.focus())
        row_counter += 1
        tk.Label(product_frame, text="बारकोड:", bg='white', font=('Arial', 10)).grid(row=row_counter, column=0, padx=5, pady=5, sticky='w')
        self.purchase_barcode_entry = tk.Entry(product_frame, font=('Arial', 10))
        self.purchase_barcode_entry.grid(row=row_counter, column=1, padx=5, pady=5, sticky='ew')
        self.purchase_barcode_entry.bind('<Return>', lambda e: self.current_stock_label.focus())
        row_counter += 1
        tk.Label(product_frame, text="सध्याचा स्टॉक:", bg='white', font=('Arial', 10)).grid(row=row_counter, column=0, padx=5, pady=5, sticky='w')
        self.current_stock_label = tk.Label(product_frame, text="0", bg='white', font=('Arial', 10))
        self.current_stock_label.grid(row=row_counter, column=1, padx=5, pady=5, sticky='w')
        row_counter += 1
        tk.Label(product_frame, text="खरेदी किंमत:", bg='white', font=('Arial', 10)).grid(row=row_counter, column=0, padx=5, pady=5, sticky='w')
        self.purchase_price_entry = tk.Entry(product_frame, font=('Arial', 10))
        self.purchase_price_entry.grid(row=row_counter, column=1, padx=5, pady=5, sticky='ew')
        self.purchase_price_entry.bind('<Return>', lambda e: self.sale_price_entry.focus())
        row_counter += 1
        tk.Label(product_frame, text="विक्री किंमत:", bg='white', font=('Arial', 10)).grid(row=row_counter, column=0, padx=5, pady=5, sticky='w')
        self.sale_price_entry = tk.Entry(product_frame, font=('Arial', 10))
        self.sale_price_entry.grid(row=row_counter, column=1, padx=5, pady=5, sticky='ew')
        self.sale_price_entry.bind('<Return>', lambda e: self.purchase_quantity_entry.focus())
        row_counter += 1
        tk.Label(product_frame, text="खरेदी नग:", bg='white', font=('Arial', 10)).grid(row=row_counter, column=0, padx=5, pady=5, sticky='w')
        self.purchase_quantity_entry = tk.Entry(product_frame, font=('Arial', 10))
        self.purchase_quantity_entry.grid(row=row_counter, column=1, padx=5, pady=5, sticky='ew')
        self.purchase_quantity_entry.insert(0, "1")
        self.purchase_quantity_entry.bind('<KeyRelease>', lambda e: self.calculate_purchase_item_total())
        self.purchase_quantity_entry.bind('<Return>', lambda e: self.purchase_item_total_label.focus())
        row_counter += 1
        tk.Label(product_frame, text="एकूण किंमत:", bg='white', font=('Arial', 10)).grid(row=row_counter, column=0, padx=5, pady=5, sticky='w')
        self.purchase_item_total_label = tk.Label(product_frame, text="₹0.00", bg='white', font=('Arial', 10))
        self.purchase_item_total_label.grid(row=row_counter, column=1, padx=5, pady=5, sticky='w')
        row_counter += 1
        add_product_btn = tk.Button(product_frame, text="➕ कार्टमध्ये ऍड", bg='#3a86ff', fg='white',
                                  font=('Arial', 10), command=self.add_product_to_purchase_cart)
        add_product_btn.grid(row=row_counter, column=0, columnspan=2, pady=10, sticky='ew')
        right_panel = tk.Frame(main_frame, bg='white')
        right_panel.grid(row=0, column=1, sticky='nsew')
        right_panel.grid_rowconfigure(0, weight=1)  # कार्ट फ्रेम
        right_panel.grid_rowconfigure(1, weight=0)  # बिल फ्रेम
        right_panel.grid_columnconfigure(0, weight=1)
        cart_frame = tk.LabelFrame(right_panel, text="खरेदी कार्ट", bg='white', font=('Arial', 10, 'bold'), bd=1, relief=tk.GROOVE)
        cart_frame.grid(row=0, column=0, sticky='nsew', pady=(0, 10))
        cart_frame.grid_rowconfigure(0, weight=1)
        cart_frame.grid_columnconfigure(0, weight=1)
        columns = ('क्रमांक', 'उत्पादन', 'खरेदी किं.', 'विक्री किं.', 'प्रमाण', 'एकूण', 'काढा')
        self.purchase_cart_tree = ttk.Treeview(cart_frame, columns=columns, show='headings', height=10)
        column_widths = [50, 150, 80, 80, 60, 80, 60]
        for i, (col, width) in enumerate(zip(columns, column_widths)):
            self.purchase_cart_tree.heading(col, text=col)
            self.purchase_cart_tree.column(col, width=width, anchor='center')
        self.purchase_cart_tree.bind('<Double-1>', self.delete_purchase_cart_item)
        scrollbar = ttk.Scrollbar(cart_frame, orient=tk.VERTICAL, command=self.purchase_cart_tree.yview)
        self.purchase_cart_tree.configure(yscrollcommand=scrollbar.set)
        self.purchase_cart_tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')
        bill_frame = tk.LabelFrame(right_panel, text="बिल माहिती", bg='white', font=('Arial', 10, 'bold'), bd=1, relief=tk.GROOVE)
        bill_frame.grid(row=1, column=0, sticky='ew')
        for i in range(6):  # 6 रोसाठी (0-5)
            bill_frame.grid_rowconfigure(i, weight=0)
        bill_frame.grid_columnconfigure(0, weight=0)  # लेबल स्तंभ
        bill_frame.grid_columnconfigure(1, weight=1)  # मूल्य स्तंभ
        tk.Label(bill_frame, text="एकूण रक्कम:", bg='white', font=('Arial', 11)).grid(row=0, column=0, padx=10, pady=5, sticky='w')
        self.purchase_total_label = tk.Label(bill_frame, text="₹0.00", bg='white', font=('Arial', 11, 'bold'), fg='#0fcea7')
        self.purchase_total_label.grid(row=0, column=1, padx=10, pady=5, sticky='w')
        tk.Label(bill_frame, text="जमा रक्कम:", bg='white', font=('Arial', 11)).grid(row=1, column=0, padx=10, pady=5, sticky='w')
        self.purchase_paid_entry = tk.Entry(bill_frame, font=('Arial', 10))
        self.purchase_paid_entry.grid(row=1, column=1, padx=10, pady=5, sticky='ew')
        self.purchase_paid_entry.insert(0, "0")
        self.purchase_paid_entry.bind('<KeyRelease>', self.calculate_purchase_total)
        self.purchase_paid_entry.bind('<Return>', lambda e: self.purchase_payment_mode.focus())
        tk.Label(bill_frame, text="उर्वरित:", bg='white', font=('Arial', 11)).grid(row=2, column=0, padx=10, pady=5, sticky='w')
        self.purchase_balance_label = tk.Label(bill_frame, text="₹0.00", bg='white', font=('Arial', 11, 'bold'), fg='#7209b7')
        self.purchase_balance_label.grid(row=2, column=1, padx=10, pady=5, sticky='w')
        tk.Label(bill_frame, text="पेमेंट मोड:", bg='white', font=('Arial', 11)).grid(row=3, column=0, padx=10, pady=5, sticky='w')
        self.purchase_payment_mode = ttk.Combobox(bill_frame, values=['रोख', 'बँक ट्रान्सफर', 'चेक', 'उदारी', 'आंशिक जमा'], 
                                                 state='readonly', font=('Arial', 10))
        self.purchase_payment_mode.grid(row=3, column=1, padx=10, pady=5, sticky='ew')
        self.purchase_payment_mode.current(0)
        self.purchase_payment_mode.bind('<<ComboboxSelected>>', self.update_payment_mode_based_on_paid)
        self.purchase_payment_mode.bind('<Return>', lambda e: self.save_purchase())
        button_frame = tk.Frame(bill_frame, bg='white')
        button_frame.grid(row=4, column=0, columnspan=2, pady=10, sticky='ew')
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        save_btn = tk.Button(button_frame, text="💰 खरेदी नोंदवा", bg='#0fcea7', fg='white',
                           font=('Arial', 12, 'bold'), command=self.save_purchase)
        save_btn.grid(row=0, column=0, padx=(0, 5), sticky='ew')
        clear_btn = tk.Button(button_frame, text="🗑️ कार्ट क्लिअर", bg='#e94560', fg='white',
                            font=('Arial', 12), command=self.clear_purchase_cart)
        clear_btn.grid(row=0, column=1, padx=(5, 0), sticky='ew')
        self.load_suppliers_for_purchase()
        self.load_categories_for_purchase()
    def calculate_purchase_total(self, event=None):
        total = sum(item['total'] for item in self.purchase_cart)
        paid_text = self.purchase_paid_entry.get()
        try:
            paid = float(paid_text) if paid_text else 0
        except:
            paid = 0
        if self.purchase_cart and paid == 0:
            paid = total
            self.purchase_paid_entry.delete(0, tk.END)
            self.purchase_paid_entry.insert(0, str(total))
        balance = total - paid
        if balance < 0:
            balance = 0
        self.purchase_total_label.config(text=f"₹{total:.2f}")
        self.purchase_balance_label.config(text=f"₹{balance:.2f}")
        if paid < total:
            self.purchase_payment_mode.set('आंशिक जमा')
        elif paid == total and total > 0:
            self.purchase_payment_mode.set('रोख')
        else:
            self.purchase_payment_mode.set('रोख')
    def update_payment_mode_based_on_paid(self, event=None):
        """जेव्हा पेमेंट मोड बदलला जातो तेव्हा जमा रक्कम अपडेट करा"""
        payment_mode = self.purchase_payment_mode.get()
        total_text = self.purchase_total_label.cget("text").replace('₹', '').replace(',', '')
        try:
            total = float(total_text) if total_text else 0
            if payment_mode == 'उदारी':
                self.purchase_paid_entry.delete(0, tk.END)
                self.purchase_paid_entry.insert(0, "0")
            elif payment_mode == 'रोख':
                self.purchase_paid_entry.delete(0, tk.END)
                self.purchase_paid_entry.insert(0, str(total))
            elif payment_mode == 'आंशिक जमा':
                partial_amount = total / 2
                self.purchase_paid_entry.delete(0, tk.END)
                self.purchase_paid_entry.insert(0, str(partial_amount))
            self.calculate_purchase_total()
        except:
            pass
    def refresh_purchases_tab(self):
        """Refresh purchases tab data"""
        self.load_suppliers_for_purchase()
        self.load_categories_for_purchase()
        self.clear_purchase_cart()
        self.load_supplier_info()
    def load_suppliers_for_purchase(self):
        try:
            self.db.cursor.execute("SELECT name FROM suppliers ORDER BY name")
            suppliers = [row[0] for row in self.db.cursor.fetchall()]
            self.supplier_combo['values'] = suppliers
            if suppliers:
                self.supplier_combo.current(0)
                self.load_supplier_info()
        except:
            self.supplier_combo['values'] = []
    def load_supplier_info(self):
        supplier_name = self.supplier_combo.get()
        if not supplier_name:
            return
        try:
            self.db.cursor.execute("SELECT phone, credit_balance FROM suppliers WHERE name = ?", (supplier_name,))
            result = self.db.cursor.fetchone()
            if result:
                phone, credit = result
                self.supplier_phone_label.config(text=phone if phone else "-")
                self.supplier_credit_label.config(text=f"₹{credit:.2f}")
            else:
                self.supplier_phone_label.config(text="-")
                self.supplier_credit_label.config(text="₹0.00")
        except:
            pass
    def load_categories_for_purchase(self):
        try:
            self.db.cursor.execute("SELECT DISTINCT category FROM products WHERE category IS NOT NULL AND category != '' ORDER BY category")
            categories = [row[0] for row in self.db.cursor.fetchall()]
            self.purchase_category_combo['values'] = categories
        except:
            self.purchase_category_combo['values'] = []
    def load_purchase_products_by_category(self):
        category = self.purchase_category_combo.get()
        if category:
            try:
                self.db.cursor.execute("SELECT name FROM products WHERE category = ? ORDER BY name", (category,))
                products = [row[0] for row in self.db.cursor.fetchall()]
                self.purchase_product_combo['values'] = products
            except:
                self.purchase_product_combo['values'] = []
        else:
            self.purchase_product_combo['values'] = []
    def load_purchase_product_details(self):
        product_name = self.purchase_product_combo.get()
        if product_name:
            try:
                self.db.cursor.execute("SELECT barcode, stock, purchase_price, sale_price FROM products WHERE name = ?", (product_name,))
                result = self.db.cursor.fetchone()
                if result:
                    barcode, stock, purchase_price, sale_price = result
                    self.purchase_barcode_entry.delete(0, tk.END)
                    self.purchase_barcode_entry.insert(0, barcode if barcode else "")
                    self.current_stock_label.config(text=str(stock))
                    self.purchase_price_entry.delete(0, tk.END)
                    self.purchase_price_entry.insert(0, str(purchase_price))
                    self.sale_price_entry.delete(0, tk.END)
                    self.sale_price_entry.insert(0, str(sale_price))
                    self.calculate_purchase_item_total()
            except:
                pass
    def calculate_purchase_item_total(self):
        try:
            purchase_price = float(self.purchase_price_entry.get())
            quantity = int(self.purchase_quantity_entry.get())
            total = purchase_price * quantity
            self.purchase_item_total_label.config(text=f"₹{total:.2f}")
        except:
            self.purchase_item_total_label.config(text="₹0.00")
    def add_product_to_purchase_cart(self):
        product_name = self.purchase_product_combo.get()
        barcode = self.purchase_barcode_entry.get()
        purchase_price_text = self.purchase_price_entry.get()
        sale_price_text = self.sale_price_entry.get()
        quantity_text = self.purchase_quantity_entry.get()
        if not product_name:
            self.show_messagebox("त्रुटी", "कृपया उत्पादन निवडा")
            return
        try:
            purchase_price = float(purchase_price_text)
            sale_price = float(sale_price_text)
            quantity = int(quantity_text)
            total = purchase_price * quantity
            cart_item = {
                'name': product_name,
                'barcode': barcode,
                'purchase_price': purchase_price,
                'sale_price': sale_price,
                'quantity': quantity,
                'total': total,
                'category': self.purchase_category_combo.get()
            }
            self.purchase_cart.append(cart_item)
            cart_values = (
                len(self.purchase_cart),
                product_name,
                f"₹{purchase_price:.2f}",
                f"₹{sale_price:.2f}",
                quantity,
                f"₹{total:.2f}",
                "❌ काढा"
            )
            self.purchase_cart_tree.insert('', tk.END, values=cart_values)
            self.purchase_quantity_entry.delete(0, tk.END)
            self.purchase_quantity_entry.insert(0, "1")
            self.purchase_item_total_label.config(text="₹0.00")
            self.purchase_product_combo.set('')
            self.purchase_barcode_entry.delete(0, tk.END)
            self.current_stock_label.config(text="0")
            self.purchase_price_entry.delete(0, tk.END)
            self.sale_price_entry.delete(0, tk.END)
            self.update_paid_amount_for_cash()
        except ValueError:
            self.show_messagebox("त्रुटी", "कृपया वैध संख्या प्रविष्ट करा")
    def update_paid_amount_for_cash(self):
        """डिफॉल्ट रोख व्यवहारासाठी जमा रक्कम सेट करा"""
        total = sum(item['total'] for item in self.purchase_cart)
        if total > 0:
            self.purchase_payment_mode.set('रोख')
            self.purchase_paid_entry.delete(0, tk.END)
            self.purchase_paid_entry.insert(0, str(total))
            self.calculate_purchase_total()    
    def delete_purchase_cart_item(self, event):
        item = self.purchase_cart_tree.identify_row(event.y)
        column = self.purchase_cart_tree.identify_column(event.x)
        if item and column == '#7':
            selected_item = self.purchase_cart_tree.selection()[0]
            index = int(self.purchase_cart_tree.item(selected_item, 'values')[0]) - 1
            self.purchase_cart.pop(index)
            self.purchase_cart_tree.delete(selected_item)
            self.refresh_purchase_cart_indexes()
            self.calculate_purchase_total()
    def refresh_purchase_cart_indexes(self):
        for i, item in enumerate(self.purchase_cart_tree.get_children(), 1):
            values = list(self.purchase_cart_tree.item(item, 'values'))
            values[0] = i
            self.purchase_cart_tree.item(item, values=values)
    def clear_purchase_cart(self):
        self.purchase_cart = []
        for item in self.purchase_cart_tree.get_children():
            self.purchase_cart_tree.delete(item)
        self.purchase_total_label.config(text="₹0.00")
        self.purchase_balance_label.config(text="₹0.00")
        self.purchase_paid_entry.delete(0, tk.END)
        self.purchase_paid_entry.insert(0, "0")
        self.purchase_payment_mode.set('रोख')
    def save_purchase(self):
        supplier_name = self.supplier_combo.get()
        payment_mode = self.purchase_payment_mode.get()
        if not supplier_name:
            self.show_messagebox("त्रुटी", "कृपया पुरवठादार निवडा")
            return
        if not self.purchase_cart:
            self.show_messagebox("त्रुटी", "कार्ट रिकामा आहे")
            return
        total = sum(item['total'] for item in self.purchase_cart)
        paid_text = self.purchase_paid_entry.get()
        try:
            paid = float(paid_text) if paid_text else 0
        except:
            paid = 0
        balance = total - paid
        if balance < 0:
            self.show_messagebox("त्रुटी", "जमा रक्कम एकूण रक्कमपेक्षा जास्त असू शकत नाही")
            return
        try:
            invoice_no = f"PUR-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            self.db.cursor.execute('''
                INSERT INTO purchases (invoice_no, supplier_name, date, total_amount, 
                                     paid_amount, balance_amount, payment_mode, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                invoice_no,
                supplier_name,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                total,
                paid,
                balance,
                payment_mode,
                'पूर्ण' if balance == 0 else 'उदारी'
            ))
            purchase_id = self.db.cursor.lastrowid
            for item in self.purchase_cart:
                self.db.cursor.execute("SELECT id FROM products WHERE name = ?", (item['name'],))
                product_result = self.db.cursor.fetchone()
                if product_result:
                    product_id = product_result[0]
                    self.db.cursor.execute('''
                        UPDATE products SET 
                        purchase_price = ?,
                        sale_price = ?,
                        stock = stock + ?,
                        barcode = COALESCE(?, barcode),
                        category = COALESCE(?, category)
                        WHERE id = ?
                    ''', (item['purchase_price'], item['sale_price'], item['quantity'], 
                          item['barcode'], item['category'], product_id))
                else:
                    self.db.cursor.execute('''
                        INSERT INTO products (name, purchase_price, sale_price, stock, min_stock, 
                                            barcode, category, unit, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        item['name'],
                        item['purchase_price'],
                        item['sale_price'],
                        item['quantity'],
                        10,
                        item['barcode'],
                        item['category'],
                        "पीसी",
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ))
                    product_id = self.db.cursor.lastrowid
                self.db.cursor.execute('''
                    INSERT INTO purchase_items (purchase_id, product_id, product_name, 
                                              quantity, price, total)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    purchase_id,
                    product_id,
                    item['name'],
                    item['quantity'],
                    item['purchase_price'],
                    item['total']
                ))
            if payment_mode in ['उदारी', 'आंशिक जमा'] or balance > 0:
                self.db.cursor.execute('''
                    UPDATE suppliers SET credit_balance = credit_balance + ? 
                    WHERE name = ?
                ''', (balance, supplier_name))
            self.db.conn.commit()
            self.last_purchase_id = purchase_id
            self.show_messagebox("यशस्वी", f"खरेदी यशस्वीरित्या नोंदवली!\nबिल क्रमांक: {invoice_no}")
            self.clear_purchase_cart()
            self.load_supplier_info()
        except Exception as e:
            self.show_messagebox("त्रुटी", f"खरेदी सेव त्रुटी: {str(e)}")
    def add_new_supplier_purchase(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("नवीन पुरवठादार")
        dialog.geometry("400x250")
        dialog.configure(bg='white')
        dialog.transient(self.root)
        dialog.grab_set()
        self.center_dialog(dialog)
        tk.Label(dialog, text="नवीन पुरवठादार माहिती", font=('Arial', 14, 'bold'), bg='white').pack(pady=10)
        form_frame = tk.Frame(dialog, bg='white')
        form_frame.pack(pady=10, padx=20)
        tk.Label(form_frame, text="नाव*:", bg='white', font=('Arial', 10)).grid(row=0, column=0, padx=5, pady=5, sticky='w')
        name_entry = tk.Entry(form_frame, width=30, font=('Arial', 10))
        name_entry.grid(row=0, column=1, padx=5, pady=5)
        name_entry.bind('<Return>', lambda e: phone_entry.focus())
        tk.Label(form_frame, text="फोन:", bg='white', font=('Arial', 10)).grid(row=1, column=0, padx=5, pady=5, sticky='w')
        phone_entry = tk.Entry(form_frame, width=30, font=('Arial', 10))
        phone_entry.grid(row=1, column=1, padx=5, pady=5)
        phone_entry.bind('<Return>', lambda e: address_entry.focus())
        tk.Label(form_frame, text="पत्ता:", bg='white', font=('Arial', 10)).grid(row=2, column=0, padx=5, pady=5, sticky='w')
        address_entry = tk.Entry(form_frame, width=30, font=('Arial', 10))
        address_entry.grid(row=2, column=1, padx=5, pady=5)
        address_entry.bind('<Return>', lambda e: save_supplier())
        def save_supplier():
            name = name_entry.get().strip()
            if not name:
                self.show_messagebox("त्रुटी", "कृपया पुरवठादाराचे नाव प्रविष्ट करा")
                return
            try:
                self.db.cursor.execute('''
                    INSERT INTO suppliers (name, phone, address, credit_balance, created_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    name,
                    phone_entry.get(),
                    address_entry.get(),
                    0,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ))
                self.db.conn.commit()
                dialog.destroy()
                self.load_suppliers_for_purchase()
                self.supplier_combo.set(name)
                self.load_supplier_info()
            except Exception as e:
                self.show_messagebox("त्रुटी", f"पुरवठादार जोड त्रुटी: {str(e)}")
        button_frame = tk.Frame(dialog, bg='white')
        button_frame.pack(pady=20)
        save_btn = tk.Button(button_frame, text="💾 सेव्ह करा", bg='#0fcea7', fg='white',
                           font=('Arial', 10), command=save_supplier)
        save_btn.pack(side=tk.LEFT, padx=10)
        cancel_btn = tk.Button(button_frame, text="रद्द करा", bg='#e94560', fg='white',
                             font=('Arial', 10), command=dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=10)
    def setup_stock_content(self, parent):
        main_container = tk.Frame(parent, bg='white')
        main_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        main_container.grid_rowconfigure(0, weight=0)  # हेडर फ्रेम
        main_container.grid_rowconfigure(1, weight=1)  # मुख्य फ्रेम
        main_container.grid_columnconfigure(0, weight=1)
        header_frame = tk.Frame(main_container, bg='white')
        header_frame.grid(row=0, column=0, sticky='ew', pady=(0, 15), padx=10)
        tk.Label(header_frame, text="📦 स्टॉक व्यवस्थापन", 
                font=('Arial', 20, 'bold'), bg='white').pack(side=tk.LEFT)
        self.stock_notebook = ttk.Notebook(main_container)
        self.stock_notebook.grid(row=1, column=0, sticky='nsew', padx=10, pady=10)
        stock_tab = tk.Frame(self.stock_notebook, bg='white')
        self.stock_notebook.add(stock_tab, text="स्टॉक")
        stock_tab.grid_rowconfigure(0, weight=1)
        stock_tab.grid_columnconfigure(0, weight=1)
        self.setup_stock_tab(stock_tab)
        category_tab = tk.Frame(self.stock_notebook, bg='white')
        self.stock_notebook.add(category_tab, text="कॅटेगरी - बारकोड")
        category_tab.grid_rowconfigure(0, weight=1)
        category_tab.grid_columnconfigure(0, weight=1)
        self.setup_category_tab(category_tab)
    def refresh_stock_tab(self):
        """Refresh stock tab data"""
        self.load_stock_categories()
        self.load_stock_by_category()
        self.load_category_details()
        self.load_all_products_for_search()
        self.load_barcode_products()
    def setup_stock_tab(self, parent):
        main_frame = tk.Frame(parent, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        search_frame = tk.Frame(main_frame, bg='white')
        search_frame.pack(fill=tk.X, pady=(0, 15))
        tk.Label(search_frame, text="उत्पादन शोधा:", bg='white', 
                font=('Arial', 10)).pack(side=tk.LEFT)
        self.stock_search_entry = tk.Entry(search_frame, width=30, font=('Arial', 10))
        self.stock_search_entry.pack(side=tk.LEFT, padx=5)
        self.stock_search_entry.bind('<Return>', lambda e: self.search_stock())
        search_btn = tk.Button(search_frame, text="🔍 शोधा", bg='#3a86ff', fg='white',
                              font=('Arial', 10), command=self.search_stock)
        search_btn.pack(side=tk.LEFT, padx=5)
        new_product_btn = tk.Button(search_frame, text="+ नवीन उत्पादन", bg='#0fcea7', fg='white',
                                   font=('Arial', 10), command=self.add_new_product)
        new_product_btn.pack(side=tk.LEFT, padx=5)
        refresh_btn = tk.Button(search_frame, text="🔄 रिफ्रेश", bg='#f0a500', fg='white',
                               font=('Arial', 10), command=self.load_stock_by_category)
        refresh_btn.pack(side=tk.LEFT, padx=5)
        tk.Label(search_frame, text="कॅटेगिरी:", bg='white', font=('Arial', 10)).pack(side=tk.LEFT, padx=(20,5))
        self.stock_category_combo = ttk.Combobox(search_frame, width=20, font=('Arial', 10))
        self.stock_category_combo.pack(side=tk.LEFT, padx=5)
        self.stock_category_combo.bind('<<ComboboxSelected>>', lambda e: self.load_stock_by_category())
        table_frame = tk.Frame(main_frame, bg='white')
        table_frame.pack(fill=tk.BOTH, expand=True)
        columns = ('क्रमांक', 'उत्पादन', 'बारकोड', 'कॅटेगिरी', 'खरेदी किं.', 'विक्री किं.', 'स्टॉक', 'किमान', 'एकूण किंमत', 'एडिट', 'डिलीट')
        self.stock_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        column_widths = [50, 150, 100, 100, 80, 80, 60, 60, 100, 60, 60]
        for i, (col, width) in enumerate(zip(columns, column_widths)):
            self.stock_tree.heading(col, text=col)
            if i in [0, 4, 5, 6, 7, 8]:
                self.stock_tree.column(col, width=width, anchor='e')
            elif i in [9, 10]:
                self.stock_tree.column(col, width=width, anchor='center')
            else:
                self.stock_tree.column(col, width=width, anchor='w')
        self.stock_tree.bind('<Double-1>', self.edit_stock_item)
        scrollbar_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.stock_tree.yview)
        scrollbar_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.stock_tree.xview)
        self.stock_tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        self.stock_tree.grid(row=0, column=0, sticky='nsew')
        scrollbar_y.grid(row=0, column=1, sticky='ns')
        scrollbar_x.grid(row=1, column=0, sticky='ew')
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        self.load_stock_categories()
        self.load_stock_by_category()
    def load_stock_categories(self):
        try:
            self.db.cursor.execute("SELECT DISTINCT category FROM products WHERE category IS NOT NULL AND category != '' ORDER BY category")
            categories = [row[0] for row in self.db.cursor.fetchall()]
            self.stock_category_combo['values'] = ['सर्व'] + categories
            self.stock_category_combo.current(0)
        except:
            pass
    def load_stock_by_category(self):
        category = self.stock_category_combo.get()
        for item in self.stock_tree.get_children():
            self.stock_tree.delete(item)
        try:
            if category == 'सर्व' or not category:
                self.db.cursor.execute('''
                    SELECT id, name, barcode, category, purchase_price, sale_price, stock, min_stock
                    FROM products 
                    ORDER BY category, name
                ''')
            else:
                self.db.cursor.execute('''
                    SELECT id, name, barcode, category, purchase_price, sale_price, stock, min_stock
                    FROM products 
                    WHERE category = ?
                    ORDER BY name
                ''', (category,))
            products = self.db.cursor.fetchall()
            for i, product in enumerate(products, 1):
                product_id, name, barcode, category, purchase_price, sale_price, stock, min_stock = product
                total_value = purchase_price * stock
                values = (
                    i,
                    name,
                    barcode if barcode else "-",
                    category if category else "-",
                    f"₹{purchase_price:.2f}",
                    f"₹{sale_price:.2f}",
                    stock,
                    min_stock,
                    f"₹{total_value:.2f}",
                    "✏️",
                    "🗑️"
                )
                self.stock_tree.insert('', tk.END, values=values, tags=(f'product_{product_id}',))
        except:
            pass
    def edit_stock_item(self, event):
        item = self.stock_tree.identify_row(event.y)
        column = self.stock_tree.identify_column(event.x)
        if not item:
            return
        values = self.stock_tree.item(item, 'values')
        product_name = values[1]
        if column == '#11':
            confirm = messagebox.askyesno("डिलीट", f"तुम्हाला '{product_name}' डिलीट करायचे आहे का?")
            if confirm:
                self.delete_stock_item(product_name)
        elif column == '#10':
            self.edit_stock_details(product_name)
    def delete_stock_item(self, product_name):
        try:
            self.db.cursor.execute("DELETE FROM sale_items WHERE product_name = ?", (product_name,))
            self.db.cursor.execute("DELETE FROM products WHERE name = ?", (product_name,))
            self.db.conn.commit()
            self.load_stock_by_category()
        except:
            pass
    def edit_stock_details(self, product_name):
        try:
            self.db.cursor.execute('''
                SELECT id, name, barcode, category, purchase_price, sale_price, stock, min_stock, unit
                FROM products WHERE name = ?
            ''', (product_name,))
            product = self.db.cursor.fetchone()
            if not product:
                return
            dialog = tk.Toplevel(self.root)
            dialog.title("उत्पादन एडिट")
            dialog.geometry("500x400")
            dialog.configure(bg='white')
            dialog.transient(self.root)
            dialog.grab_set()
            self.center_dialog(dialog)
            tk.Label(dialog, text="उत्पादन माहिती एडिट", font=('Arial', 14, 'bold'), bg='white').pack(pady=10)
            form_frame = tk.Frame(dialog, bg='white')
            form_frame.pack(pady=10, padx=20)
            tk.Label(form_frame, text="उत्पादन नाव:", bg='white', font=('Arial', 10)).grid(row=0, column=0, padx=5, pady=5, sticky='w')
            name_entry = tk.Entry(form_frame, width=30, font=('Arial', 10))
            name_entry.grid(row=0, column=1, padx=5, pady=5)
            name_entry.insert(0, product[1])
            name_entry.bind('<Return>', lambda e: barcode_entry.focus())
            tk.Label(form_frame, text="बारकोड:", bg='white', font=('Arial', 10)).grid(row=1, column=0, padx=5, pady=5, sticky='w')
            barcode_entry = tk.Entry(form_frame, width=30, font=('Arial', 10))
            barcode_entry.grid(row=1, column=1, padx=5, pady=5)
            barcode_entry.insert(0, product[2] if product[2] else "")
            barcode_entry.bind('<Return>', lambda e: category_entry.focus())
            tk.Label(form_frame, text="कॅटेगिरी:", bg='white', font=('Arial', 10)).grid(row=2, column=0, padx=5, pady=5, sticky='w')
            category_entry = tk.Entry(form_frame, width=30, font=('Arial', 10))
            category_entry.grid(row=2, column=1, padx=5, pady=5)
            category_entry.insert(0, product[3] if product[3] else "")
            category_entry.bind('<Return>', lambda e: purchase_price_entry.focus())
            tk.Label(form_frame, text="खरेदी किंमत:", bg='white', font=('Arial', 10)).grid(row=3, column=0, padx=5, pady=5, sticky='w')
            purchase_price_entry = tk.Entry(form_frame, width=30, font=('Arial', 10))
            purchase_price_entry.grid(row=3, column=1, padx=5, pady=5)
            purchase_price_entry.insert(0, str(product[4]))
            purchase_price_entry.bind('<Return>', lambda e: sale_price_entry.focus())
            tk.Label(form_frame, text="विक्री किंमत:", bg='white', font=('Arial', 10)).grid(row=4, column=0, padx=5, pady=5, sticky='w')
            sale_price_entry = tk.Entry(form_frame, width=30, font=('Arial', 10))
            sale_price_entry.grid(row=4, column=1, padx=5, pady=5)
            sale_price_entry.insert(0, str(product[5]))
            sale_price_entry.bind('<Return>', lambda e: stock_entry.focus())
            tk.Label(form_frame, text="स्टॉक:", bg='white', font=('Arial', 10)).grid(row=5, column=0, padx=5, pady=5, sticky='w')
            stock_entry = tk.Entry(form_frame, width=30, font=('Arial', 10))
            stock_entry.grid(row=5, column=1, padx=5, pady=5)
            stock_entry.insert(0, str(product[6]))
            stock_entry.bind('<Return>', lambda e: min_stock_entry.focus())
            tk.Label(form_frame, text="किमान स्टॉक:", bg='white', font=('Arial', 10)).grid(row=6, column=0, padx=5, pady=5, sticky='w')
            min_stock_entry = tk.Entry(form_frame, width=30, font=('Arial', 10))
            min_stock_entry.grid(row=6, column=1, padx=5, pady=5)
            min_stock_entry.insert(0, str(product[7]))
            min_stock_entry.bind('<Return>', lambda e: unit_entry.focus())
            tk.Label(form_frame, text="युनिट:", bg='white', font=('Arial', 10)).grid(row=7, column=0, padx=5, pady=5, sticky='w')
            unit_entry = tk.Entry(form_frame, width=30, font=('Arial', 10))
            unit_entry.grid(row=7, column=1, padx=5, pady=5)
            unit_entry.insert(0, product[8] if product[8] else "पीसी")
            unit_entry.bind('<Return>', lambda e: save_changes())
            def save_changes():
                try:
                    self.db.cursor.execute('''
                        UPDATE products SET 
                        name = ?, barcode = ?, category = ?, purchase_price = ?, 
                        sale_price = ?, stock = ?, min_stock = ?, unit = ?
                        WHERE id = ?
                    ''', (
                        name_entry.get(),
                        barcode_entry.get() if barcode_entry.get() else None,
                        category_entry.get() if category_entry.get() else None,
                        float(purchase_price_entry.get()),
                        float(sale_price_entry.get()),
                        int(stock_entry.get()),
                        int(min_stock_entry.get()),
                        unit_entry.get(),
                        product[0]
                    ))
                    self.db.conn.commit()
                    dialog.destroy()
                    self.load_stock_by_category()
                except Exception as e:
                    self.show_messagebox("त्रुटी", f"अपडेट त्रुटी: {str(e)}")
            button_frame = tk.Frame(dialog, bg='white')
            button_frame.pack(pady=20)
            save_btn = tk.Button(button_frame, text="💾 सेव्ह करा", bg='#0fcea7', fg='white',
                               font=('Arial', 10), command=save_changes)
            save_btn.pack(side=tk.LEFT, padx=10)
            cancel_btn = tk.Button(button_frame, text="रद्द करा", bg='#e94560', fg='white',
                                 font=('Arial', 10), command=dialog.destroy)
            cancel_btn.pack(side=tk.LEFT, padx=10)
        except Exception as e:
            self.show_messagebox("त्रुटी", f"एडिट त्रुटी: {str(e)}")
    def search_stock(self):
        search_text = self.stock_search_entry.get().strip()
        category = self.stock_category_combo.get()
        if not search_text:
            self.load_stock_by_category()
            return
        for item in self.stock_tree.get_children():
            self.stock_tree.delete(item)
        try:
            if category == 'सर्व' or not category:
                self.db.cursor.execute('''
                    SELECT id, name, barcode, category, purchase_price, sale_price, stock, min_stock
                    FROM products 
                    WHERE name LIKE ? OR barcode LIKE ? OR category LIKE ?
                    ORDER BY category, name
                ''', (f'%{search_text}%', f'%{search_text}%', f'%{search_text}%'))
            else:
                self.db.cursor.execute('''
                    SELECT id, name, barcode, category, purchase_price, sale_price, stock, min_stock
                    FROM products 
                    WHERE (name LIKE ? OR barcode LIKE ?) AND category = ?
                    ORDER BY name
                ''', (f'%{search_text}%', f'%{search_text}%', category))
            products = self.db.cursor.fetchall()
            for i, product in enumerate(products, 1):
                product_id, name, barcode, category, purchase_price, sale_price, stock, min_stock = product
                total_value = purchase_price * stock
                values = (
                    i,
                    name,
                    barcode if barcode else "-",
                    category if category else "-",
                    f"₹{purchase_price:.2f}",
                    f"₹{sale_price:.2f}",
                    stock,
                    min_stock,
                    f"₹{total_value:.2f}",
                    "✏️",
                    "🗑️"
                )
                self.stock_tree.insert('', tk.END, values=values, tags=(f'product_{product_id}',))
        except:
            pass
    def add_new_product(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("नवीन उत्पादन")
        dialog.geometry("500x400")
        dialog.configure(bg='white')
        dialog.transient(self.root)
        dialog.grab_set()
        self.center_dialog(dialog)
        tk.Label(dialog, text="नवीन उत्पादन माहिती", font=('Arial', 14, 'bold'), bg='white').pack(pady=10)
        form_frame = tk.Frame(dialog, bg='white')
        form_frame.pack(pady=10, padx=20)
        tk.Label(form_frame, text="उत्पादन नाव*:", bg='white', font=('Arial', 10)).grid(row=0, column=0, padx=5, pady=5, sticky='w')
        name_entry = tk.Entry(form_frame, width=30, font=('Arial', 10))
        name_entry.grid(row=0, column=1, padx=5, pady=5)
        name_entry.bind('<Return>', lambda e: barcode_entry.focus())
        tk.Label(form_frame, text="बारकोड:", bg='white', font=('Arial', 10)).grid(row=1, column=0, padx=5, pady=5, sticky='w')
        barcode_entry = tk.Entry(form_frame, width=30, font=('Arial', 10))
        barcode_entry.grid(row=1, column=1, padx=5, pady=5)
        barcode_entry.bind('<Return>', lambda e: category_entry.focus())
        tk.Label(form_frame, text="कॅटेगिरी:", bg='white', font=('Arial', 10)).grid(row=2, column=0, padx=5, pady=5, sticky='w')
        category_entry = tk.Entry(form_frame, width=30, font=('Arial', 10))
        category_entry.grid(row=2, column=1, padx=5, pady=5)
        category_entry.bind('<Return>', lambda e: purchase_price_entry.focus())
        tk.Label(form_frame, text="खरेदी किंमत:", bg='white', font=('Arial', 10)).grid(row=3, column=0, padx=5, pady=5, sticky='w')
        purchase_price_entry = tk.Entry(form_frame, width=30, font=('Arial', 10))
        purchase_price_entry.grid(row=3, column=1, padx=5, pady=5)
        purchase_price_entry.insert(0, "0")
        purchase_price_entry.bind('<Return>', lambda e: sale_price_entry.focus())
        tk.Label(form_frame, text="विक्री किंमत:", bg='white', font=('Arial', 10)).grid(row=4, column=0, padx=5, pady=5, sticky='w')
        sale_price_entry = tk.Entry(form_frame, width=30, font=('Arial', 10))
        sale_price_entry.grid(row=4, column=1, padx=5, pady=5)
        sale_price_entry.insert(0, "0")
        sale_price_entry.bind('<Return>', lambda e: stock_entry.focus())
        tk.Label(form_frame, text="स्टॉक:", bg='white', font=('Arial', 10)).grid(row=5, column=0, padx=5, pady=5, sticky='w')
        stock_entry = tk.Entry(form_frame, width=30, font=('Arial', 10))
        stock_entry.grid(row=5, column=1, padx=5, pady=5)
        stock_entry.insert(0, "0")
        stock_entry.bind('<Return>', lambda e: min_stock_entry.focus())
        tk.Label(form_frame, text="किमान स्टॉक:", bg='white', font=('Arial', 10)).grid(row=6, column=0, padx=5, pady=5, sticky='w')
        min_stock_entry = tk.Entry(form_frame, width=30, font=('Arial', 10))
        min_stock_entry.grid(row=6, column=1, padx=5, pady=5)
        min_stock_entry.insert(0, "10")
        min_stock_entry.bind('<Return>', lambda e: unit_entry.focus())
        tk.Label(form_frame, text="युनिट:", bg='white', font=('Arial', 10)).grid(row=7, column=0, padx=5, pady=5, sticky='w')
        unit_entry = tk.Entry(form_frame, width=30, font=('Arial', 10))
        unit_entry.grid(row=7, column=1, padx=5, pady=5)
        unit_entry.insert(0, "पीसी")
        unit_entry.bind('<Return>', lambda e: save_product())
        def save_product():
            name = name_entry.get().strip()
            if not name:
                self.show_messagebox("त्रुटी", "कृपया उत्पादनाचे नाव प्रविष्ट करा")
                return
            try:
                self.db.cursor.execute('''
                    INSERT INTO products (barcode, name, category, purchase_price, 
                                        sale_price, stock, min_stock, unit, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    barcode_entry.get() if barcode_entry.get() else None,
                    name,
                    category_entry.get() if category_entry.get() else None,
                    float(purchase_price_entry.get()),
                    float(sale_price_entry.get()),
                    int(stock_entry.get()),
                    int(min_stock_entry.get()),
                    unit_entry.get(),
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ))
                self.db.conn.commit()
                dialog.destroy()
                self.load_stock_by_category()
            except Exception as e:
                self.show_messagebox("त्रुटी", f"उत्पादन जोड त्रुटी: {str(e)}")
        button_frame = tk.Frame(dialog, bg='white')
        button_frame.pack(pady=20)
        save_btn = tk.Button(button_frame, text="💾 सेव्ह करा", bg='#0fcea7', fg='white',
                           font=('Arial', 10), command=save_product)
        save_btn.pack(side=tk.LEFT, padx=10)
        cancel_btn = tk.Button(button_frame, text="रद्द करा", bg='#e94560', fg='white',
                             font=('Arial', 10), command=dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=10)
    def setup_category_tab(self, parent):
        main_frame = tk.Frame(parent, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        left_frame = tk.Frame(main_frame, bg='white')
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        add_category_frame = tk.LabelFrame(left_frame, text="नवीन कॅटेगिरी जोडा", bg='white', font=('Arial', 10, 'bold'))
        add_category_frame.pack(fill=tk.X, pady=(0, 10))
        tk.Label(add_category_frame, text="नवीन कॅटेगिरी नाव:", bg='white', font=('Arial', 10)).pack(side=tk.LEFT, padx=10, pady=10)
        self.new_category_entry = tk.Entry(add_category_frame, width=25, font=('Arial', 10))
        self.new_category_entry.pack(side=tk.LEFT, padx=5, pady=10)
        self.new_category_entry.bind('<Return>', lambda e: self.add_category())
        add_btn = tk.Button(add_category_frame, text="➕ जोडा", bg='#0fcea7', fg='white',
                          font=('Arial', 10), command=self.add_category)
        add_btn.pack(side=tk.LEFT, padx=10, pady=10)
        details_frame = tk.LabelFrame(left_frame, text="कॅटेगिरी विवरण", bg='white', font=('Arial', 10, 'bold'))
        details_frame.pack(fill=tk.BOTH, expand=True)
        columns = ('कॅटेगिरी', 'उत्पादन संख्या', 'एकूण किंमत', 'एडिट', 'डिलीट')
        self.category_tree = ttk.Treeview(details_frame, columns=columns, show='headings', height=15)
        column_widths = [150, 120, 120, 60, 60]
        for i, (col, width) in enumerate(zip(columns, column_widths)):
            self.category_tree.heading(col, text=col)
            if i in [3, 4]:
                self.category_tree.column(col, width=width, anchor='center')
            else:
                self.category_tree.column(col, width=width, anchor='w')
        self.category_tree.bind('<Double-1>', self.handle_category_tree_double_click)
        scrollbar_y = ttk.Scrollbar(details_frame, orient=tk.VERTICAL, command=self.category_tree.yview)
        scrollbar_x = ttk.Scrollbar(details_frame, orient=tk.HORIZONTAL, command=self.category_tree.xview)
        self.category_tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        self.category_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        right_frame = tk.Frame(main_frame, bg='white')
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        barcode_frame = tk.LabelFrame(right_frame, text="बारकोड व्यवस्थापन", bg='white', font=('Arial', 10, 'bold'))
        barcode_frame.pack(fill=tk.BOTH, expand=True)
        filter_frame = tk.Frame(barcode_frame, bg='white')
        filter_frame.pack(fill=tk.X, padx=10, pady=10)
        tk.Label(filter_frame, text="बारकोड फिल्टर:", bg='white', font=('Arial', 10)).pack(side=tk.LEFT)
        self.barcode_filter_combo = ttk.Combobox(filter_frame, values=['सर्व', 'बारकोड असलेले', 'बारकोड नसलेले'], 
                                                width=15, font=('Arial', 10), state='readonly')
        self.barcode_filter_combo.pack(side=tk.LEFT, padx=5)
        self.barcode_filter_combo.current(0)
        self.barcode_filter_combo.bind('<<ComboboxSelected>>', lambda e: self.load_barcode_products())
        search_frame = tk.Frame(barcode_frame, bg='white')
        search_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        tk.Label(search_frame, text="उत्पादन शोधा:", bg='white', font=('Arial', 10)).pack(side=tk.LEFT)
        self.product_search_combo = ttk.Combobox(search_frame, width=25, font=('Arial', 10))
        self.product_search_combo.pack(side=tk.LEFT, padx=5)
        self.product_search_combo.bind('<KeyRelease>', self.search_products_for_barcode)
        self.product_search_combo.bind('<<ComboboxSelected>>', self.load_product_for_barcode)
        self.barcode_entry_cat = tk.Entry(search_frame, width=20, font=('Arial', 10))
        self.barcode_entry_cat.pack(side=tk.LEFT, padx=5)
        self.barcode_entry_cat.insert(0, "")
        generate_btn = tk.Button(search_frame, text="🔢 जनरेट", bg='#3a86ff', fg='white',
                               font=('Arial', 10), command=self.generate_barcode)
        generate_btn.pack(side=tk.LEFT, padx=5)
        save_btn = tk.Button(search_frame, text="💾 सेव्ह", bg='#0fcea7', fg='white',
                           font=('Arial', 10), command=self.save_barcode)
        save_btn.pack(side=tk.LEFT, padx=5)
        print_btn = tk.Button(search_frame, text="🖨️ प्रिंट", bg='#f0a500', fg='white',
                            font=('Arial', 10), command=self.print_barcode)
        print_btn.pack(side=tk.LEFT, padx=5)
        barcode_list_frame = tk.Frame(barcode_frame, bg='white')
        barcode_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        barcode_columns = ('उत्पादन', 'बारकोड', 'कॅटेगिरी')
        self.barcode_tree = ttk.Treeview(barcode_list_frame, columns=barcode_columns, show='headings', height=15)
        for col in barcode_columns:
            self.barcode_tree.heading(col, text=col)
            self.barcode_tree.column(col, width=150, anchor='w')
        barcode_scrollbar = ttk.Scrollbar(barcode_list_frame, orient=tk.VERTICAL, command=self.barcode_tree.yview)
        self.barcode_tree.configure(yscrollcommand=barcode_scrollbar.set)
        self.barcode_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        barcode_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.load_category_details()
        self.load_all_products_for_search()
        self.load_barcode_products()
    def search_products_for_barcode(self, event):
        search_text = self.product_search_combo.get().strip()
        if len(search_text) < 2:
            return
        try:
            self.db.cursor.execute("SELECT name FROM products WHERE name LIKE ? ORDER BY name LIMIT 10", 
                                  (f'%{search_text}%',))
            products = [row[0] for row in self.db.cursor.fetchall()]
            self.product_search_combo['values'] = products
        except:
            pass
    def load_product_for_barcode(self, event):
        product_name = self.product_search_combo.get()
        if product_name:
            try:
                self.db.cursor.execute("SELECT barcode FROM products WHERE name = ?", (product_name,))
                result = self.db.cursor.fetchone()
                if result:
                    barcode = result[0]
                    self.barcode_entry_cat.delete(0, tk.END)
                    self.barcode_entry_cat.insert(0, barcode if barcode else "")
            except:
                pass
    def load_all_products_for_search(self):
        try:
            self.db.cursor.execute("SELECT name FROM products ORDER BY name")
            products = [row[0] for row in self.db.cursor.fetchall()]
            self.product_search_combo['values'] = products
        except:
            pass
    def generate_barcode(self):
        barcode = ''.join(random.choices(string.digits, k=13))
        self.barcode_entry_cat.delete(0, tk.END)
        self.barcode_entry_cat.insert(0, barcode)
    def save_barcode(self):
        product_name = self.product_search_combo.get()
        barcode = self.barcode_entry_cat.get().strip()
        if not product_name:
            self.show_messagebox("त्रुटी", "कृपया उत्पादन निवडा")
            return
        if not barcode:
            self.show_messagebox("त्रुटी", "कृपया बारकोड प्रविष्ट करा")
            return
        try:
            self.db.cursor.execute("SELECT name FROM products WHERE barcode = ? AND name != ?", (barcode, product_name))
            existing_product = self.db.cursor.fetchone()
            if existing_product:
                self.show_messagebox("त्रुटी", f"हा बारकोड आधीच '{existing_product[0]}' या उत्पादनासाठी वापरला आहे")
                return
            self.db.cursor.execute("UPDATE products SET barcode = ? WHERE name = ?", (barcode, product_name))
            self.db.conn.commit()
            self.barcode_entry_cat.delete(0, tk.END)
            self.product_search_combo.set('')
            self.load_barcode_products()
        except Exception as e:
            self.show_messagebox("त्रुटी", f"बारकोड सेव त्रुटी: {str(e)}")
    def print_barcode(self):
        product_name = self.product_search_combo.get()
        barcode = self.barcode_entry_cat.get().strip()
        if not product_name or not barcode:
            self.show_messagebox("त्रुटी", "कृपया उत्पादन आणि बारकोड निवडा")
            return
        try:
            from reportlab.lib.pagesizes import A6
            temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
            pdf_path = temp_file.name
            c = canvas.Canvas(pdf_path, pagesize=A6)
            width, height = A6
            c.setFont("Helvetica-Bold", 14)
            c.drawString(20, height - 40, self.shop_name)
            c.setFont("Helvetica", 10)
            c.drawString(20, height - 70, product_name[:30])
            c.setFont("Helvetica-Bold", 20)
            c.drawString(20, height - 110, barcode)
            c.setFont("Helvetica", 8)
            c.drawString(20, height - 130, f"किंमत: ₹{self.get_product_price(product_name):.2f}")
            c.save()
            if sys.platform == "win32":
                os.startfile(pdf_path, "print")
            elif sys.platform == "darwin":
                subprocess.Popen(['open', pdf_path])
            else:
                subprocess.Popen(['xdg-open', pdf_path])
        except Exception as e:
            self.show_messagebox("त्रुटी", f"बारकोड प्रिंट त्रुटी: {str(e)}")
    def get_product_price(self, product_name):
        try:
            self.db.cursor.execute("SELECT sale_price FROM products WHERE name = ?", (product_name,))
            result = self.db.cursor.fetchone()
            if result:
                return result[0]
        except:
            pass
        return 0.0
    def handle_category_tree_double_click(self, event):
        item = self.category_tree.identify_row(event.y)
        column = self.category_tree.identify_column(event.x)
        if not item:
            return
        values = self.category_tree.item(item, 'values')
        category_name = values[0]
        if column == '#4':
            confirm = messagebox.askyesno("डिलीट", f"तुम्हाला '{category_name}' कॅटेगिरी डिलीट करायची आहे का?")
            if confirm:
                self.delete_category(category_name)
        elif column == '#3':
            new_name = tk.simpledialog.askstring("कॅटेगिरी नाव बदला", "नवीन नाव प्रविष्ट करा:", initialvalue=category_name)
            if new_name and new_name != category_name:
                self.edit_category(category_name, new_name)
    def add_category(self):
        category_name = self.new_category_entry.get().strip()
        if not category_name:
            self.show_messagebox("त्रुटी", "कृपया कॅटेगिरी नाव प्रविष्ट करा")
            return
        try:
            self.db.cursor.execute("INSERT INTO products (category, name) VALUES (?, 'डमी')", (category_name,))
            self.db.conn.commit()
            self.new_category_entry.delete(0, tk.END)
            self.load_category_details()
        except Exception as e:
            self.show_messagebox("त्रुटी", f"कॅटेगिरी जोड त्रुटी: {str(e)}")
    def edit_category(self, old_category, new_category):
        if new_category and new_category != old_category:
            try:
                self.db.cursor.execute("UPDATE products SET category = ? WHERE category = ?", (new_category, old_category))
                self.db.conn.commit()
                self.load_category_details()
            except Exception as e:
                self.show_messagebox("त्रुटी", f"कॅटेगिरी बदल त्रुटी: {str(e)}")
    def delete_category(self, category):
        if not category:
            return
        try:
            self.db.cursor.execute("SELECT COUNT(*) FROM products WHERE category = ? AND name != 'डमी'", (category,))
            count = self.db.cursor.fetchone()[0]
            if count > 0:
                self.show_messagebox("त्रुटी", f"या कॅटेगिरीमध्ये {count} उत्पादन आहेत. फक्त रिकामी कॅटेगिरी डिलीट करता येईल.")
                return
            self.db.cursor.execute("DELETE FROM products WHERE category = ? AND name = 'डमी'", (category,))
            self.db.conn.commit()
            self.load_category_details()
        except Exception as e:
            self.show_messagebox("त्रुटी", f"कॅटेगिरी डिलीट त्रुटी: {str(e)}")
    def load_category_details(self):
        for item in self.category_tree.get_children():
            self.category_tree.delete(item)
        try:
            self.db.cursor.execute('''
                SELECT category, COUNT(*) as product_count, SUM(sale_price * stock) as total_value
                FROM products 
                WHERE category IS NOT NULL AND category != '' AND name != 'डमी'
                GROUP BY category
                ORDER BY category
            ''')
            categories = self.db.cursor.fetchall()
            for category in categories:
                cat_name, count, total = category
                self.category_tree.insert('', tk.END, values=(cat_name, count, f"₹{total or 0:.2f}", "✏️", "🗑️"))
        except:
            pass
    def load_barcode_products(self):
        for item in self.barcode_tree.get_children():
            self.barcode_tree.delete(item)
        filter_type = self.barcode_filter_combo.get()
        try:
            if filter_type == 'बारकोड असलेले':
                query = '''
                    SELECT name, barcode, category
                    FROM products 
                    WHERE barcode IS NOT NULL AND barcode != ''
                    ORDER BY category, name
                    LIMIT 50
                '''
            elif filter_type == 'बारकोड नसलेले':
                query = '''
                    SELECT name, barcode, category
                    FROM products 
                    WHERE barcode IS NULL OR barcode = ''
                    ORDER BY category, name
                    LIMIT 50
                '''
            else:
                query = '''
                    SELECT name, barcode, category
                    FROM products 
                    ORDER BY category, name
                    LIMIT 50
                '''
            self.db.cursor.execute(query)
            products = self.db.cursor.fetchall()
            for product in products:
                name, barcode, category = product
                self.barcode_tree.insert('', tk.END, values=(name, barcode if barcode else "", category if category else ""))
        except:
            pass
    def setup_accounts_content(self, parent):
        main_container = tk.Frame(parent, bg='white')
        main_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        header_frame = tk.Frame(main_container, bg='white')
        header_frame.pack(fill=tk.X, pady=(0, 15), padx=10)
        tk.Label(header_frame, text="💳 खाते व्यवस्थापन", 
                font=('Arial', 20, 'bold'), bg='white').pack(side=tk.LEFT)
        self.accounts_notebook = ttk.Notebook(main_container)
        self.accounts_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        transactions_tab = tk.Frame(self.accounts_notebook, bg='white')
        self.accounts_notebook.add(transactions_tab, text="व्यवहार")
        self.setup_transactions_tab(transactions_tab)
        credit_transactions_tab = tk.Frame(self.accounts_notebook, bg='white')
        self.accounts_notebook.add(credit_transactions_tab, text="उधारी व्यवहार")
        self.setup_credit_transactions_tab(credit_transactions_tab)
        manual_credit_tab = tk.Frame(self.accounts_notebook, bg='white')
        self.accounts_notebook.add(manual_credit_tab, text="मॅन्युअल उदारी")
        self.setup_manual_credit_tab(manual_credit_tab)
    def refresh_accounts_tab(self):
        """Refresh accounts tab data"""
        self.update_contact_filter()
        self.search_transactions()
        self.load_customer_credit_data()
        self.load_supplier_credit_data()
        self.load_manual_credit_list()
    def setup_transactions_tab(self, parent):
        main_frame = tk.Frame(parent, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        filter_frame = tk.LabelFrame(main_frame, text="शोध फिल्टर", bg='white', font=('Arial', 10, 'bold'))
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        tk.Label(filter_frame, text="व्यवहार प्रकार:", bg='white', font=('Arial', 9)).grid(row=0, column=0, padx=5, pady=5)
        self.transaction_type_filter = ttk.Combobox(filter_frame, 
                                                   values=['सर्व', 'विक्री', 'खरेदी', 'उधारी जमा', 'मॅन्युअल उधारी'], 
                                                   width=20, font=('Arial', 9), state='readonly')
        self.transaction_type_filter.grid(row=0, column=1, padx=5, pady=5)
        self.transaction_type_filter.current(0)
        self.transaction_type_filter.bind('<<ComboboxSelected>>', lambda e: self.update_contact_filter())
        tk.Label(filter_frame, text="संपर्क:", bg='white', font=('Arial', 9)).grid(row=0, column=2, padx=5, pady=5)
        self.contact_filter = ttk.Combobox(filter_frame, width=20, font=('Arial', 9))
        self.contact_filter.grid(row=0, column=3, padx=5, pady=5)
        self.contact_filter.bind('<Return>', lambda e: self.from_date_filter.focus())
        tk.Label(filter_frame, text="तारीख पासून:", bg='white', font=('Arial', 9)).grid(row=1, column=0, padx=5, pady=5)
        self.from_date_filter = DateEntry(filter_frame, width=15, font=('Arial', 9), date_pattern='dd/mm/yyyy')
        self.from_date_filter.grid(row=1, column=1, padx=5, pady=5)
        self.from_date_filter.bind('<Return>', lambda e: self.to_date_filter.focus())
        tk.Label(filter_frame, text="तारीख पर्यंत:", bg='white', font=('Arial', 9)).grid(row=1, column=2, padx=5, pady=5)
        self.to_date_filter = DateEntry(filter_frame, width=15, font=('Arial', 9), date_pattern='dd/mm/yyyy')
        self.to_date_filter.grid(row=1, column=3, padx=5, pady=5)
        self.to_date_filter.bind('<Return>', lambda e: self.search_transactions())
        search_btn = tk.Button(filter_frame, text="🔍 शोधा", bg='#3a86ff', fg='white',
                              font=('Arial', 9), command=self.search_transactions)
        search_btn.grid(row=1, column=4, padx=5, pady=5)
        table_frame = tk.Frame(main_frame, bg='white')
        table_frame.pack(fill=tk.BOTH, expand=True)
        columns = ('बिल क्र.', 'तारीख', 'प्रकार', 'संपर्क', 'एकूण', 'सवलत', 'जमा', 'उर्वरित', 'पेमेंट मोड', 'स्थिती')
        self.transactions_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        column_widths = [100, 120, 80, 150, 80, 70, 80, 80, 100, 80]
        for i, (col, width) in enumerate(zip(columns, column_widths)):
            self.transactions_tree.heading(col, text=col)
            self.transactions_tree.column(col, width=width, anchor='center')
        scrollbar_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.transactions_tree.yview)
        scrollbar_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.transactions_tree.xview)
        self.transactions_tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        self.transactions_tree.grid(row=0, column=0, sticky='nsew')
        scrollbar_y.grid(row=0, column=1, sticky='ns')
        scrollbar_x.grid(row=1, column=0, sticky='ew')
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        status_frame = tk.Frame(main_frame, bg='white')
        status_frame.pack(fill=tk.X, pady=10)
        tk.Label(status_frame, text="एकूण व्यवहार:", bg='white', font=('Arial', 10)).pack(side=tk.LEFT, padx=20)
        self.total_transactions_label = tk.Label(status_frame, text="₹0.00", bg='white', font=('Arial', 10, 'bold'), fg='#0fcea7')
        self.total_transactions_label.pack(side=tk.LEFT, padx=5)
        tk.Label(status_frame, text="एकूण उदारी:", bg='white', font=('Arial', 10)).pack(side=tk.LEFT, padx=20)
        self.total_transactions_credit_label = tk.Label(status_frame, text="₹0.00", bg='white', font=('Arial', 10, 'bold'), fg='#e94560')
        self.total_transactions_credit_label.pack(side=tk.LEFT, padx=5)
        self.update_contact_filter()
        self.search_transactions()
    def update_contact_filter(self):
        transaction_type = self.transaction_type_filter.get()
        self.contact_filter.set('')
        try:
            contacts = []
            if transaction_type in ['सर्व', 'विक्री', 'उधारी जमा', 'मॅन्युअल उधारी']:
                self.db.cursor.execute("""
                    SELECT DISTINCT customer_name 
                    FROM sales 
                    WHERE customer_name IS NOT NULL 
                    AND customer_name != ''
                    AND customer_name NOT LIKE 'CUST-%'
                """)
                sales_contacts = [row[0] for row in self.db.cursor.fetchall()]
                contacts.extend(sales_contacts)
            if transaction_type in ['सर्व', 'खरेदी', 'उधारी जमा', 'मॅन्युअल उधारी']:
                self.db.cursor.execute("""
                    SELECT DISTINCT supplier_name 
                    FROM purchases 
                    WHERE supplier_name IS NOT NULL 
                    AND supplier_name != ''
                """)
                purchase_contacts = [row[0] for row in self.db.cursor.fetchall()]
                contacts.extend(purchase_contacts)
            if contacts:
                unique_contacts = sorted(set([c for c in contacts if c]))  # None/empty values remove करा
                self.contact_filter['values'] = unique_contacts
            else:
                self.contact_filter['values'] = []
        except Exception as e:
            print(f"Error updating contact filter: {str(e)}")
            self.contact_filter['values'] = []
    def search_transactions(self):
        for item in self.transactions_tree.get_children():
            self.transactions_tree.delete(item)
        transaction_type = self.transaction_type_filter.get()
        contact = self.contact_filter.get()
        from_date = self.from_date_filter.get_date().strftime("%Y-%m-%d")
        to_date = self.to_date_filter.get_date().strftime("%Y-%m-%d")
        try:
            total_amount = 0
            total_credit = 0
            if transaction_type in ['सर्व', 'विक्री', 'उधारी जमा', 'मॅन्युअल उधारी']:
                sales_query = """
                    SELECT invoice_no, date, customer_name, total_amount, 
                           discount_amount, paid_amount, balance_amount, 
                           payment_mode, status, transaction_type
                    FROM sales 
                    WHERE 1=1
                """
                sales_params = []
                if transaction_type == 'विक्री':
                    sales_query += " AND transaction_type = 'विक्री'"
                elif transaction_type == 'उधारी जमा':
                    sales_query += " AND transaction_type = 'पेमेंट'"
                elif transaction_type == 'मॅन्युअल उधारी':
                    sales_query += " AND transaction_type = 'मॅन्युअल उधारी'"
                elif transaction_type == 'सर्व':
                    sales_query += " AND transaction_type IN ('विक्री', 'पेमेंट', 'मॅन्युअल उधारी')"
                if from_date:
                    sales_query += " AND DATE(date) >= ?"
                    sales_params.append(from_date)
                if to_date:
                    sales_query += " AND DATE(date) <= ?"
                    sales_params.append(to_date)
                if contact:
                    sales_query += " AND customer_name = ?"
                    sales_params.append(contact)
                sales_query += " ORDER BY date DESC"
                self.db.cursor.execute(sales_query, sales_params)
                sales_transactions = self.db.cursor.fetchall()
                for trans in sales_transactions:
                    invoice_no, date_str, contact_name, total, discount, paid, balance, payment_mode, status, original_type = trans
                    display_type = 'विक्री'
                    if original_type == 'पेमेंट':
                        display_type = 'उधारी जमा'
                    elif original_type == 'मॅन्युअल उधारी':
                        display_type = 'मॅन्युअल उधारी'
                    try:
                        date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                        formatted_date = date_obj.strftime("%d/%m/%Y %H:%M")
                    except:
                        formatted_date = date_str
                    balance_value = float(balance) if balance else 0
                    discount_value = float(discount) if discount else 0
                    values = (
                        invoice_no,
                        formatted_date,
                        display_type,
                        contact_name if contact_name else "-",
                        f"₹{float(total):.2f}" if total else "₹0.00",
                        f"₹{discount_value:.2f}",
                        f"₹{float(paid):.2f}" if paid else "₹0.00",
                        f"₹{balance_value:.2f}",
                        payment_mode if payment_mode else "-",
                        status if status else "-"
                    )
                    self.transactions_tree.insert('', tk.END, values=values)
                    total_amount += float(total) if total else 0
                    if balance_value > 0:
                        total_credit += balance_value
            if transaction_type in ['सर्व', 'खरेदी', 'उधारी जमा', 'मॅन्युअल उधारी']:
                purchases_query = """
                    SELECT invoice_no, date, supplier_name, total_amount, 
                           paid_amount, balance_amount, payment_mode, status, transaction_type
                    FROM purchases 
                    WHERE 1=1
                """
                purchases_params = []
                if transaction_type == 'खरेदी':
                    purchases_query += " AND transaction_type = 'खरेदी'"
                elif transaction_type == 'उधारी जमा':
                    purchases_query += " AND transaction_type = 'पेमेंट'"
                elif transaction_type == 'मॅन्युअल उधारी':
                    purchases_query += " AND transaction_type = 'मॅन्युअल उधारी'"
                elif transaction_type == 'सर्व':
                    purchases_query += " AND transaction_type IN ('खरेदी', 'पेमेंट', 'मॅन्युअल उधारी')"
                if from_date:
                    purchases_query += " AND DATE(date) >= ?"
                    purchases_params.append(from_date)
                if to_date:
                    purchases_query += " AND DATE(date) <= ?"
                    purchases_params.append(to_date)
                if contact:
                    purchases_query += " AND supplier_name = ?"
                    purchases_params.append(contact)
                purchases_query += " ORDER BY date DESC"
                self.db.cursor.execute(purchases_query, purchases_params)
                purchases_transactions = self.db.cursor.fetchall()
                for trans in purchases_transactions:
                    invoice_no, date_str, contact_name, total, paid, balance, payment_mode, status, original_type = trans
                    display_type = 'खरेदी'
                    if original_type == 'पेमेंट':
                        display_type = 'उधारी जमा'
                    elif original_type == 'मॅन्युअल उधारी':
                        display_type = 'मॅन्युअल उधारी'
                    try:
                        date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                        formatted_date = date_obj.strftime("%d/%m/%Y %H:%M")
                    except:
                        formatted_date = date_str
                    balance_value = float(balance) if balance else 0
                    discount_value = 0  # Purchases don't have discount
                    values = (
                        invoice_no,
                        formatted_date,
                        display_type,
                        contact_name if contact_name else "-",
                        f"₹{float(total):.2f}" if total else "₹0.00",
                        f"₹{discount_value:.2f}",
                        f"₹{float(paid):.2f}" if paid else "₹0.00",
                        f"₹{balance_value:.2f}",
                        payment_mode if payment_mode else "-",
                        status if status else "-"
                    )
                    self.transactions_tree.insert('', tk.END, values=values)
                    total_amount += float(total) if total else 0
                    if balance_value > 0:
                        total_credit += balance_value
            self.total_transactions_label.config(text=f"₹{total_amount:.2f}")
            self.total_transactions_credit_label.config(text=f"₹{total_credit:.2f}")
        except Exception as e:
            print(f"Error searching transactions: {str(e)}")
            import traceback
            traceback.print_exc() 
    def setup_credit_transactions_tab(self, parent):
        main_frame = tk.Frame(parent, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        container = tk.Frame(main_frame, bg='white')
        container.pack(fill=tk.BOTH, expand=True)
        left_frame = tk.Frame(container, bg='white')
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        customer_frame = tk.LabelFrame(left_frame, text="ग्राहक उधारी", bg='white', font=('Arial', 12, 'bold'))
        customer_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        customer_search_frame = tk.Frame(customer_frame, bg='white')
        customer_search_frame.pack(fill=tk.X, padx=10, pady=10)
        tk.Label(customer_search_frame, text="शोध:", bg='white', font=('Arial', 10)).pack(side=tk.LEFT)
        self.customer_credit_search = tk.Entry(customer_search_frame, width=15, font=('Arial', 10))
        self.customer_credit_search.pack(side=tk.LEFT, padx=5)
        self.customer_credit_search.bind('<KeyRelease>', lambda e: self.search_customer_credit())
        tk.Label(customer_search_frame, text="पासून:", bg='white', font=('Arial', 10)).pack(side=tk.LEFT, padx=(10, 5))
        self.cust_from_date = DateEntry(customer_search_frame, width=12, font=('Arial', 9), date_pattern='dd/mm/yyyy')
        self.cust_from_date.pack(side=tk.LEFT, padx=5)
        tk.Label(customer_search_frame, text="पर्यंत:", bg='white', font=('Arial', 10)).pack(side=tk.LEFT, padx=(10, 5))
        self.cust_to_date = DateEntry(customer_search_frame, width=12, font=('Arial', 9), date_pattern='dd/mm/yyyy')
        self.cust_to_date.pack(side=tk.LEFT, padx=5)
        search_btn = tk.Button(customer_search_frame, text="🔍 शोधा", bg='#3a86ff', fg='white',
                              font=('Arial', 10), command=self.search_customer_credit)
        search_btn.pack(side=tk.LEFT, padx=5)
        customer_credit_tree_frame = tk.Frame(customer_frame, bg='white')
        customer_credit_tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        columns = ('नाव', 'एकूण उधारी', 'जमा', 'बाकी')
        self.customer_credit_tree = ttk.Treeview(customer_credit_tree_frame, columns=columns, show='headings', height=15)
        for col in columns:
            self.customer_credit_tree.heading(col, text=col)
            self.customer_credit_tree.column(col, width=150, anchor='center')
        self.customer_credit_tree.bind('<Double-1>', self.open_customer_credit_payment_form)
        scrollbar = ttk.Scrollbar(customer_credit_tree_frame, orient=tk.VERTICAL, command=self.customer_credit_tree.yview)
        self.customer_credit_tree.configure(yscrollcommand=scrollbar.set)
        self.customer_credit_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        right_frame = tk.Frame(container, bg='white')
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        supplier_frame = tk.LabelFrame(right_frame, text="पुरवठादार उधारी", bg='white', font=('Arial', 12, 'bold'))
        supplier_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        supplier_search_frame = tk.Frame(supplier_frame, bg='white')
        supplier_search_frame.pack(fill=tk.X, padx=10, pady=10)
        tk.Label(supplier_search_frame, text="शोध:", bg='white', font=('Arial', 10)).pack(side=tk.LEFT)
        self.supplier_credit_search = tk.Entry(supplier_search_frame, width=15, font=('Arial', 10))
        self.supplier_credit_search.pack(side=tk.LEFT, padx=5)
        self.supplier_credit_search.bind('<KeyRelease>', lambda e: self.search_supplier_credit())
        tk.Label(supplier_search_frame, text="पासून:", bg='white', font=('Arial', 10)).pack(side=tk.LEFT, padx=(10, 5))
        self.supp_from_date = DateEntry(supplier_search_frame, width=12, font=('Arial', 9), date_pattern='dd/mm/yyyy')
        self.supp_from_date.pack(side=tk.LEFT, padx=5)
        tk.Label(supplier_search_frame, text="पर्यंत:", bg='white', font=('Arial', 10)).pack(side=tk.LEFT, padx=(10, 5))
        self.supp_to_date = DateEntry(supplier_search_frame, width=12, font=('Arial', 9), date_pattern='dd/mm/yyyy')
        self.supp_to_date.pack(side=tk.LEFT, padx=5)
        search_btn2 = tk.Button(supplier_search_frame, text="🔍 शोधा", bg='#3a86ff', fg='white',
                               font=('Arial', 10), command=self.search_supplier_credit)
        search_btn2.pack(side=tk.LEFT, padx=5)
        supplier_credit_tree_frame = tk.Frame(supplier_frame, bg='white')
        supplier_credit_tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        columns = ('नाव', 'एकूण उधारी', 'जमा', 'बाकी')
        self.supplier_credit_tree = ttk.Treeview(supplier_credit_tree_frame, columns=columns, show='headings', height=15)
        for col in columns:
            self.supplier_credit_tree.heading(col, text=col)
            self.supplier_credit_tree.column(col, width=150, anchor='center')
        self.supplier_credit_tree.bind('<Double-1>', self.open_supplier_credit_payment_form)
        scrollbar2 = ttk.Scrollbar(supplier_credit_tree_frame, orient=tk.VERTICAL, command=self.supplier_credit_tree.yview)
        self.supplier_credit_tree.configure(yscrollcommand=scrollbar2.set)
        self.supplier_credit_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar2.pack(side=tk.RIGHT, fill=tk.Y)
        self.load_customer_credit_data()
        self.load_supplier_credit_data()
    def load_customer_credit_data(self):
        try:
            for item in self.customer_credit_tree.get_children():
                self.customer_credit_tree.delete(item)
            self.db.cursor.execute('''
                SELECT customer_name, 
                       SUM(balance_amount) as total_credit,
                       SUM(paid_amount) as total_paid,
                       SUM(total_amount) as total_bill
                FROM sales 
                WHERE customer_name NOT LIKE 'CUST-%' 
                AND balance_amount > 0
                GROUP BY customer_name
                ORDER BY customer_name
            ''')
            customers = self.db.cursor.fetchall()
            self.db.cursor.execute('''
                SELECT name, credit_balance 
                FROM customers 
                WHERE credit_balance > 0 
                AND name NOT LIKE 'CUST-%'
            ''')
            db_customers = self.db.cursor.fetchall()
            customer_dict = {}
            for customer in customers:
                name, total_credit, total_paid, total_bill = customer
                if total_credit > 0:
                    customer_dict[name] = {
                        'total_credit': total_credit,
                        'total_paid': total_paid or 0,
                        'balance': total_credit,
                        'total_bill': total_bill or 0
                    }
            for customer in db_customers:
                name, credit_balance = customer
                if credit_balance > 0:
                    if name in customer_dict:
                        customer_dict[name]['total_credit'] = credit_balance
                        customer_dict[name]['balance'] = credit_balance
                    else:
                        customer_dict[name] = {
                            'total_credit': credit_balance,
                            'total_paid': 0,
                            'balance': credit_balance,
                            'total_bill': 0
                        }
            for name, data in customer_dict.items():
                if data['balance'] > 0:
                    values = (
                        name,
                        f"₹{data['total_credit']:.2f}",
                        f"₹{data['total_paid']:.2f}",
                        f"₹{data['balance']:.2f}"
                    )
                    self.customer_credit_tree.insert('', tk.END, values=values)
        except Exception as e:
            print(f"Error loading customer credit data: {str(e)}")  
    def search_customer_credit(self):
        search_text = self.customer_credit_search.get().strip()
        from_date = self.cust_from_date.get_date().strftime("%Y-%m-%d")
        to_date = self.cust_to_date.get_date().strftime("%Y-%m-%d")
        for item in self.customer_credit_tree.get_children():
            self.customer_credit_tree.delete(item)
        try:
            query = '''
                SELECT customer_name, 
                       SUM(balance_amount) as total_credit,
                       SUM(paid_amount) as total_paid,
                       SUM(total_amount) as total_bill
                FROM sales 
                WHERE customer_name NOT LIKE 'CUST-%' 
                AND balance_amount > 0
            '''
            params = []
            if search_text:
                query += " AND customer_name LIKE ?"
                params.append(f'%{search_text}%')
            if from_date:
                query += " AND DATE(date) >= ?"
                params.append(from_date)
            if to_date:
                query += " AND DATE(date) <= ?"
                params.append(to_date)
            query += " GROUP BY customer_name ORDER BY customer_name"
            self.db.cursor.execute(query, params)
            customers = self.db.cursor.fetchall()
            customer_query = '''
                SELECT name, credit_balance 
                FROM customers 
                WHERE credit_balance > 0 
                AND name NOT LIKE 'CUST-%'
            '''
            customer_params = []
            if search_text:
                customer_query += " AND name LIKE ?"
                customer_params.append(f'%{search_text}%')
            self.db.cursor.execute(customer_query, customer_params)
            db_customers = self.db.cursor.fetchall()
            customer_dict = {}
            for customer in customers:
                name, total_credit, total_paid, total_bill = customer
                if total_credit > 0:
                    customer_dict[name] = {
                        'total_credit': total_credit,
                        'total_paid': total_paid or 0,
                        'balance': total_credit,
                        'total_bill': total_bill or 0
                    }
            for customer in db_customers:
                name, credit_balance = customer
                if credit_balance > 0:
                    if name in customer_dict:
                        customer_dict[name]['total_credit'] = credit_balance
                        customer_dict[name]['balance'] = credit_balance
                    else:
                        customer_dict[name] = {
                            'total_credit': credit_balance,
                            'total_paid': 0,
                            'balance': credit_balance,
                            'total_bill': 0
                        }
            for name, data in customer_dict.items():
                if data['balance'] > 0:
                    values = (
                        name,
                        f"₹{data['total_credit']:.2f}",
                        f"₹{data['total_paid']:.2f}",
                        f"₹{data['balance']:.2f}"
                    )
                    self.customer_credit_tree.insert('', tk.END, values=values)
        except Exception as e:
            print(f"Error searching customer credit: {str(e)}")
    def open_customer_credit_payment_form(self, event):
        item = self.customer_credit_tree.selection()
        if not item:
            return
        values = self.customer_credit_tree.item(item, 'values')
        if not values:
            return
        customer_name = values[0]
        total_credit = float(values[1].replace('₹', '').replace(',', ''))
        paid = float(values[2].replace('₹', '').replace(',', ''))
        balance = float(values[3].replace('₹', '').replace(',', ''))
        dialog = tk.Toplevel(self.root)
        dialog.title("ग्राहक उधारी जमा")
        dialog.geometry("450x350")
        dialog.configure(bg='white')
        dialog.transient(self.root)
        dialog.grab_set()
        self.center_dialog(dialog)
        tk.Label(dialog, text="ग्राहक उधारी जमा", font=('Arial', 14, 'bold'), bg='white').pack(pady=10)
        form_frame = tk.Frame(dialog, bg='white')
        form_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        tk.Label(form_frame, text="ग्राहक:", bg='white', font=('Arial', 10)).grid(row=0, column=0, padx=5, pady=5, sticky='w')
        tk.Label(form_frame, text=customer_name, bg='white', font=('Arial', 10, 'bold')).grid(row=0, column=1, padx=5, pady=5, sticky='w')
        tk.Label(form_frame, text="एकूण उधारी:", bg='white', font=('Arial', 10)).grid(row=1, column=0, padx=5, pady=5, sticky='w')
        tk.Label(form_frame, text=f"₹{total_credit:.2f}", bg='white', font=('Arial', 10, 'bold')).grid(row=1, column=1, padx=5, pady=5, sticky='w')
        tk.Label(form_frame, text="आधी जमा:", bg='white', font=('Arial', 10)).grid(row=2, column=0, padx=5, pady=5, sticky='w')
        tk.Label(form_frame, text=f"₹{paid:.2f}", bg='white', font=('Arial', 10)).grid(row=2, column=1, padx=5, pady=5, sticky='w')
        tk.Label(form_frame, text="बाकी:", bg='white', font=('Arial', 10)).grid(row=3, column=0, padx=5, pady=5, sticky='w')
        tk.Label(form_frame, text=f"₹{balance:.2f}", bg='white', font=('Arial', 10, 'bold'), fg='#e94560').grid(row=3, column=1, padx=5, pady=5, sticky='w')
        tk.Label(form_frame, text="जमा रक्कम:", bg='white', font=('Arial', 10)).grid(row=4, column=0, padx=5, pady=5, sticky='w')
        amount_entry = tk.Entry(form_frame, width=15, font=('Arial', 10))
        amount_entry.grid(row=4, column=1, padx=5, pady=5, sticky='w')
        amount_entry.insert(0, str(balance))
        tk.Label(form_frame, text="मोड:", bg='white', font=('Arial', 10)).grid(row=5, column=0, padx=5, pady=5, sticky='w')
        payment_mode = ttk.Combobox(form_frame, values=['रोख', 'बँक'], width=15, font=('Arial', 10))
        payment_mode.grid(row=5, column=1, padx=5, pady=5, sticky='w')
        payment_mode.current(0)
        def save_payment():
            try:
                amount = float(amount_entry.get())
                if amount <= 0:
                    self.show_messagebox("त्रुटी", "रक्कम ० पेक्षा जास्त असावी")
                    return
                if amount > balance:
                    self.show_messagebox("त्रुटी", f"रक्कम बाकीपेक्षा ({balance:.2f}) जास्त असू शकत नाही")
                    return
                self.db.cursor.execute('''
                    UPDATE customers SET credit_balance = credit_balance - ? 
                    WHERE name = ?
                ''', (amount, customer_name))
                self.db.cursor.execute('''
                    INSERT INTO sales (invoice_no, customer_name, date, total_amount, 
                                     discount_amount, discount_type, paid_amount, 
                                     balance_amount, payment_mode, status, transaction_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    f"PAY-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    customer_name,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    0,
                    0,
                    '₹',
                    amount,
                    -amount,
                    payment_mode.get(),
                    'पूर्ण',
                    'पेमेंट'
                ))
                self.db.conn.commit()
                dialog.destroy()
                self.load_customer_credit_data()
            except ValueError:
                self.show_messagebox("त्रुटी", "कृपया वैध रक्कम प्रविष्ट करा")
            except Exception as e:
                self.show_messagebox("त्रुटी", f"उधारी जमा त्रुटी: {str(e)}")
        button_frame = tk.Frame(dialog, bg='white')
        button_frame.pack(pady=20)
        save_btn = tk.Button(button_frame, text="💰 उधारी जमा करा", bg='#0fcea7', fg='white',
                           font=('Arial', 12, 'bold'), command=save_payment)
        save_btn.pack(side=tk.LEFT, padx=10)
        cancel_btn = tk.Button(button_frame, text="रद्द करा", bg='#e94560', fg='white',
                             font=('Arial', 12), command=dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=10)
    def load_supplier_credit_data(self):
        try:
            for item in self.supplier_credit_tree.get_children():
                self.supplier_credit_tree.delete(item)
            self.db.cursor.execute('''
                SELECT supplier_name, 
                       SUM(balance_amount) as total_credit,
                       SUM(paid_amount) as total_paid,
                       SUM(total_amount) as total_bill
                FROM purchases 
                WHERE balance_amount > 0
                GROUP BY supplier_name
                ORDER BY supplier_name
            ''')
            suppliers = self.db.cursor.fetchall()
            self.db.cursor.execute('''
                SELECT name, credit_balance 
                FROM suppliers 
                WHERE credit_balance > 0
            ''')
            db_suppliers = self.db.cursor.fetchall()
            supplier_dict = {}
            for supplier in suppliers:
                name, total_credit, total_paid, total_bill = supplier
                if total_credit > 0:
                    supplier_dict[name] = {
                        'total_credit': total_credit,
                        'total_paid': total_paid or 0,
                        'balance': total_credit,
                        'total_bill': total_bill or 0
                    }
            for supplier in db_suppliers:
                name, credit_balance = supplier
                if credit_balance > 0:
                    if name in supplier_dict:
                        supplier_dict[name]['total_credit'] = credit_balance
                        supplier_dict[name]['balance'] = credit_balance
                    else:
                        supplier_dict[name] = {
                            'total_credit': credit_balance,
                            'total_paid': 0,
                            'balance': credit_balance,
                            'total_bill': 0
                        }
            for name, data in supplier_dict.items():
                if data['balance'] > 0:
                    values = (
                        name,
                        f"₹{data['total_credit']:.2f}",
                        f"₹{data['total_paid']:.2f}",
                        f"₹{data['balance']:.2f}"
                    )
                    self.supplier_credit_tree.insert('', tk.END, values=values)
        except Exception as e:
            print(f"Error loading supplier credit data: {str(e)}")
    def search_supplier_credit(self):
        search_text = self.supplier_credit_search.get().strip()
        from_date = self.supp_from_date.get_date().strftime("%Y-%m-%d")
        to_date = self.supp_to_date.get_date().strftime("%Y-%m-%d")
        for item in self.supplier_credit_tree.get_children():
            self.supplier_credit_tree.delete(item)
        try:
            query = '''
                SELECT supplier_name, 
                       SUM(balance_amount) as total_credit,
                       SUM(paid_amount) as total_paid,
                       SUM(total_amount) as total_bill
                FROM purchases 
                WHERE balance_amount > 0
            '''
            params = []
            if search_text:
                query += " AND supplier_name LIKE ?"
                params.append(f'%{search_text}%')
            if from_date:
                query += " AND DATE(date) >= ?"
                params.append(from_date)
            if to_date:
                query += " AND DATE(date) <= ?"
                params.append(to_date)
            query += " GROUP BY supplier_name ORDER BY supplier_name"
            self.db.cursor.execute(query, params)
            suppliers = self.db.cursor.fetchall()
            supplier_query = '''
                SELECT name, credit_balance 
                FROM suppliers 
                WHERE credit_balance > 0
            '''
            supplier_params = []
            if search_text:
                supplier_query += " AND name LIKE ?"
                supplier_params.append(f'%{search_text}%')
            self.db.cursor.execute(supplier_query, supplier_params)
            db_suppliers = self.db.cursor.fetchall()
            supplier_dict = {}
            for supplier in suppliers:
                name, total_credit, total_paid, total_bill = supplier
                if total_credit > 0:
                    supplier_dict[name] = {
                        'total_credit': total_credit,
                        'total_paid': total_paid or 0,
                        'balance': total_credit,
                        'total_bill': total_bill or 0
                    }
            for supplier in db_suppliers:
                name, credit_balance = supplier
                if credit_balance > 0:
                    if name in supplier_dict:
                        supplier_dict[name]['total_credit'] = credit_balance
                        supplier_dict[name]['balance'] = credit_balance
                    else:
                        supplier_dict[name] = {
                            'total_credit': credit_balance,
                            'total_paid': 0,
                            'balance': credit_balance,
                            'total_bill': 0
                        }
            for name, data in supplier_dict.items():
                if data['balance'] > 0:
                    values = (
                        name,
                        f"₹{data['total_credit']:.2f}",
                        f"₹{data['total_paid']:.2f}",
                        f"₹{data['balance']:.2f}"
                    )
                    self.supplier_credit_tree.insert('', tk.END, values=values)
        except Exception as e:
            print(f"Error searching supplier credit: {str(e)}")    
    def open_supplier_credit_payment_form(self, event):
        item = self.supplier_credit_tree.selection()
        if not item:
            return
        values = self.supplier_credit_tree.item(item, 'values')
        if not values:
            return
        supplier_name = values[0]
        total_credit = float(values[1].replace('₹', '').replace(',', ''))
        paid = float(values[2].replace('₹', '').replace(',', ''))
        balance = float(values[3].replace('₹', '').replace(',', ''))
        dialog = tk.Toplevel(self.root)
        dialog.title("पुरवठादार उधारी जमा")
        dialog.geometry("450x350")
        dialog.configure(bg='white')
        dialog.transient(self.root)
        dialog.grab_set()
        self.center_dialog(dialog)
        tk.Label(dialog, text="पुरवठादार उधारी जमा", font=('Arial', 14, 'bold'), bg='white').pack(pady=10)
        form_frame = tk.Frame(dialog, bg='white')
        form_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        tk.Label(form_frame, text="पुरवठादार:", bg='white', font=('Arial', 10)).grid(row=0, column=0, padx=5, pady=5, sticky='w')
        tk.Label(form_frame, text=supplier_name, bg='white', font=('Arial', 10, 'bold')).grid(row=0, column=1, padx=5, pady=5, sticky='w')
        tk.Label(form_frame, text="एकूण उधारी:", bg='white', font=('Arial', 10)).grid(row=1, column=0, padx=5, pady=5, sticky='w')
        tk.Label(form_frame, text=f"₹{total_credit:.2f}", bg='white', font=('Arial', 10, 'bold')).grid(row=1, column=1, padx=5, pady=5, sticky='w')
        tk.Label(form_frame, text="आधी जमा:", bg='white', font=('Arial', 10)).grid(row=2, column=0, padx=5, pady=5, sticky='w')
        tk.Label(form_frame, text=f"₹{paid:.2f}", bg='white', font=('Arial', 10)).grid(row=2, column=1, padx=5, pady=5, sticky='w')
        tk.Label(form_frame, text="बाकी:", bg='white', font=('Arial', 10)).grid(row=3, column=0, padx=5, pady=5, sticky='w')
        tk.Label(form_frame, text=f"₹{balance:.2f}", bg='white', font=('Arial', 10, 'bold'), fg='#e94560').grid(row=3, column=1, padx=5, pady=5, sticky='w')
        tk.Label(form_frame, text="जमा रक्कम:", bg='white', font=('Arial', 10)).grid(row=4, column=0, padx=5, pady=5, sticky='w')
        amount_entry = tk.Entry(form_frame, width=15, font=('Arial', 10))
        amount_entry.grid(row=4, column=1, padx=5, pady=5, sticky='w')
        amount_entry.insert(0, str(balance))
        tk.Label(form_frame, text="मोड:", bg='white', font=('Arial', 10)).grid(row=5, column=0, padx=5, pady=5, sticky='w')
        payment_mode = ttk.Combobox(form_frame, values=['रोख', 'बँक'], width=15, font=('Arial', 10))
        payment_mode.grid(row=5, column=1, padx=5, pady=5, sticky='w')
        payment_mode.current(0)
        def save_payment():
            try:
                amount = float(amount_entry.get())
                if amount <= 0:
                    self.show_messagebox("त्रुटी", "रक्कम ० पेक्षा जास्त असावी")
                    return
                if amount > balance:
                    self.show_messagebox("त्रुटी", f"रक्कम बाकीपेक्षा ({balance:.2f}) जास्त असू शकत नाही")
                    return
                self.db.cursor.execute('''
                    UPDATE suppliers SET credit_balance = credit_balance - ? 
                    WHERE name = ?
                ''', (amount, supplier_name))
                self.db.cursor.execute('''
                    INSERT INTO purchases (invoice_no, supplier_name, date, total_amount, 
                                         paid_amount, balance_amount, payment_mode, status, transaction_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    f"PAY-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    supplier_name,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    0,
                    amount,
                    -amount,
                    payment_mode.get(),
                    'पूर्ण',
                    'पेमेंट'
                ))
                self.db.conn.commit()
                dialog.destroy()
                self.load_supplier_credit_data()
            except ValueError:
                self.show_messagebox("त्रुटी", "कृपया वैध रक्कम प्रविष्ट करा")
            except Exception as e:
                self.show_messagebox("त्रुटी", f"उधारी जमा त्रुटी: {str(e)}")
        button_frame = tk.Frame(dialog, bg='white')
        button_frame.pack(pady=20)
        save_btn = tk.Button(button_frame, text="💰 उधारी जमा करा", bg='#0fcea7', fg='white',
                           font=('Arial', 12, 'bold'), command=save_payment)
        save_btn.pack(side=tk.LEFT, padx=10)
        cancel_btn = tk.Button(button_frame, text="रद्द करा", bg='#e94560', fg='white',
                             font=('Arial', 12), command=dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=10)
    def center_dialog(self, dialog):
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
    def show_messagebox(self, title, message):
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("400x200")
        dialog.configure(bg='white')
        dialog.transient(self.root)
        dialog.grab_set()
        self.center_dialog(dialog)
        tk.Label(dialog, text=message, bg='white', font=('Arial', 12), wraplength=350).pack(pady=30, padx=20)
        ok_button = tk.Button(dialog, text="OK", bg='#0fcea7', fg='white',
                            font=('Arial', 12), width=15, command=dialog.destroy)
        ok_button.pack(pady=20)
        dialog.bind('<Return>', lambda e: dialog.destroy())
        dialog.bind('<Escape>', lambda e: dialog.destroy())
    def setup_manual_credit_tab(self, parent):
        main_frame = tk.Frame(parent, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        filter_frame = tk.LabelFrame(main_frame, text="शोध आणि फिल्टर", bg='white', font=('Arial', 10, 'bold'))
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        tk.Label(filter_frame, text="प्रकार:", bg='white', font=('Arial', 10)).grid(row=0, column=0, padx=5, pady=5)
        self.credit_type_combo = ttk.Combobox(filter_frame, values=['ग्राहक', 'पुरवठादार'], width=15, font=('Arial', 10), state='readonly')
        self.credit_type_combo.grid(row=0, column=1, padx=5, pady=5)
        self.credit_type_combo.current(0)
        self.credit_type_combo.bind('<<ComboboxSelected>>', lambda e: self.load_manual_credit_list())
        tk.Label(filter_frame, text="शोध:", bg='white', font=('Arial', 10)).grid(row=0, column=2, padx=5, pady=5)
        self.manual_search_combo = ttk.Combobox(filter_frame, width=25, font=('Arial', 10))
        self.manual_search_combo.grid(row=0, column=3, padx=5, pady=5)
        self.manual_search_combo.bind('<KeyRelease>', self.search_manual_credit)
        search_btn = tk.Button(filter_frame, text="🔍 शोधा", bg='#3a86ff', fg='white',
                              font=('Arial', 10), command=self.search_manual_credit_list)
        search_btn.grid(row=0, column=4, padx=5, pady=5)
        list_frame = tk.Frame(main_frame, bg='white')
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        columns = ('नाव', 'सध्याची उधारी', 'फोन')
        self.manual_credit_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        for col in columns:
            self.manual_credit_tree.heading(col, text=col)
            self.manual_credit_tree.column(col, width=150, anchor='center')
        self.manual_credit_tree.bind('<Double-1>', self.open_manual_credit_form)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.manual_credit_tree.yview)
        self.manual_credit_tree.configure(yscrollcommand=scrollbar.set)
        self.manual_credit_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.load_manual_credit_list()
    def load_manual_credit_list(self):
        credit_type = self.credit_type_combo.get()
        for item in self.manual_credit_tree.get_children():
            self.manual_credit_tree.delete(item)
        try:
            if credit_type == 'ग्राहक':
                self.db.cursor.execute("""
                    SELECT name, credit_balance, phone 
                    FROM customers 
                    WHERE name NOT LIKE 'CUST-%' 
                    ORDER BY name
                """)
                customers_from_db = self.db.cursor.fetchall()
                self.db.cursor.execute("""
                    SELECT DISTINCT customer_name 
                    FROM sales 
                    WHERE customer_name NOT LIKE 'CUST-%'
                    AND customer_name NOT IN (
                        SELECT name FROM customers WHERE name NOT LIKE 'CUST-%'
                    )
                """)
                customers_from_sales = self.db.cursor.fetchall()
                all_customers = []
                for name, credit, phone in customers_from_db:
                    all_customers.append((name, credit, phone))
                for (customer_name,) in customers_from_sales:
                    self.db.cursor.execute("""
                        SELECT SUM(balance_amount) 
                        FROM sales 
                        WHERE customer_name = ? 
                        AND balance_amount > 0
                    """, (customer_name,))
                    credit_result = self.db.cursor.fetchone()
                    credit_balance = credit_result[0] if credit_result and credit_result[0] else 0
                    all_customers.append((customer_name, credit_balance, ""))
                names = [row[0] for row in all_customers]
                self.manual_search_combo['values'] = names
                for name, credit, phone in all_customers:
                    self.manual_credit_tree.insert('', tk.END, values=(
                        name, 
                        f"₹{credit:.2f}", 
                        phone if phone else "-"
                    ))
            else: 
                self.db.cursor.execute("""
                    SELECT name, credit_balance, phone 
                    FROM suppliers 
                    ORDER BY name
                """)
                suppliers_from_db = self.db.cursor.fetchall()
                self.db.cursor.execute("""
                    SELECT DISTINCT supplier_name 
                    FROM purchases 
                    WHERE supplier_name NOT IN (
                        SELECT name FROM suppliers
                    )
                """)
                suppliers_from_purchases = self.db.cursor.fetchall()
                all_suppliers = []
                for name, credit, phone in suppliers_from_db:
                    all_suppliers.append((name, credit, phone))
                for (supplier_name,) in suppliers_from_purchases:
                    self.db.cursor.execute("""
                        SELECT SUM(balance_amount) 
                        FROM purchases 
                        WHERE supplier_name = ? 
                        AND balance_amount > 0
                    """, (supplier_name,))
                    credit_result = self.db.cursor.fetchone()
                    credit_balance = credit_result[0] if credit_result and credit_result[0] else 0
                    all_suppliers.append((supplier_name, credit_balance, ""))
                names = [row[0] for row in all_suppliers]
                self.manual_search_combo['values'] = names
                for name, credit, phone in all_suppliers:
                    self.manual_credit_tree.insert('', tk.END, values=(
                        name, 
                        f"₹{credit:.2f}", 
                        phone if phone else "-"
                    ))
        except Exception as e:
            print(f"Error loading manual credit list: {str(e)}")
    def search_manual_credit(self, event):
        search_text = self.manual_search_combo.get().strip()
        if len(search_text) < 2:
            return
        credit_type = self.credit_type_combo.get()
        try:
            if credit_type == 'ग्राहक':
                self.db.cursor.execute("""
                    SELECT name 
                    FROM customers 
                    WHERE name NOT LIKE 'CUST-%' 
                    AND name LIKE ? 
                    ORDER BY name LIMIT 10
                """, (f'%{search_text}%',))
            else:
                self.db.cursor.execute("""
                    SELECT name 
                    FROM suppliers 
                    WHERE name LIKE ? 
                    ORDER BY name LIMIT 10
                """, (f'%{search_text}%',))
            names = [row[0] for row in self.db.cursor.fetchall()]
            self.manual_search_combo['values'] = names
        except Exception as e:
            print(f"Error searching manual credit: {str(e)}")
    def search_manual_credit_list(self):
        search_text = self.manual_search_combo.get().strip()
        credit_type = self.credit_type_combo.get()
        for item in self.manual_credit_tree.get_children():
            self.manual_credit_tree.delete(item)
        try:
            if credit_type == 'ग्राहक':
                customer_query = """
                    SELECT name, credit_balance, phone 
                    FROM customers 
                    WHERE name NOT LIKE 'CUST-%'
                """
                params = []
                if search_text:
                    customer_query += " AND name LIKE ?"
                    params.append(f'%{search_text}%')
                customer_query += " ORDER BY name"
                self.db.cursor.execute(customer_query, params)
                customers_from_db = self.db.cursor.fetchall()
                sales_query = """
                    SELECT DISTINCT customer_name 
                    FROM sales 
                    WHERE customer_name NOT LIKE 'CUST-%'
                    AND customer_name NOT IN (
                        SELECT name FROM customers WHERE name NOT LIKE 'CUST-%'
                    )
                """
                sales_params = []
                if search_text:
                    sales_query += " AND customer_name LIKE ?"
                    sales_params.append(f'%{search_text}%')
                self.db.cursor.execute(sales_query, sales_params)
                customers_from_sales = self.db.cursor.fetchall()
                all_customers = []
                for name, credit, phone in customers_from_db:
                    all_customers.append((name, credit, phone))
                for (customer_name,) in customers_from_sales:
                    self.db.cursor.execute("""
                        SELECT SUM(balance_amount) 
                        FROM sales 
                        WHERE customer_name = ? 
                        AND balance_amount > 0
                    """, (customer_name,))
                    credit_result = self.db.cursor.fetchone()
                    credit_balance = credit_result[0] if credit_result and credit_result[0] else 0
                    all_customers.append((customer_name, credit_balance, ""))
                for name, credit, phone in all_customers:
                    self.manual_credit_tree.insert('', tk.END, values=(
                        name, 
                        f"₹{credit:.2f}", 
                        phone if phone else "-"
                    ))
            else:
                supplier_query = """
                    SELECT name, credit_balance, phone 
                    FROM suppliers 
                    WHERE 1=1
                """
                params = []
                if search_text:
                    supplier_query += " AND name LIKE ?"
                    params.append(f'%{search_text}%')
                supplier_query += " ORDER BY name"
                self.db.cursor.execute(supplier_query, params)
                suppliers_from_db = self.db.cursor.fetchall()
                purchase_query = """
                    SELECT DISTINCT supplier_name 
                    FROM purchases 
                    WHERE supplier_name NOT IN (
                        SELECT name FROM suppliers
                    )
                """
                purchase_params = []
                if search_text:
                    purchase_query += " AND supplier_name LIKE ?"
                    purchase_params.append(f'%{search_text}%')
                self.db.cursor.execute(purchase_query, purchase_params)
                suppliers_from_purchases = self.db.cursor.fetchall()
                all_suppliers = []
                for name, credit, phone in suppliers_from_db:
                    all_suppliers.append((name, credit, phone))
                for (supplier_name,) in suppliers_from_purchases:
                    self.db.cursor.execute("""
                        SELECT SUM(balance_amount) 
                        FROM purchases 
                        WHERE supplier_name = ? 
                        AND balance_amount > 0
                    """, (supplier_name,))
                    credit_result = self.db.cursor.fetchone()
                    credit_balance = credit_result[0] if credit_result and credit_result[0] else 0
                    all_suppliers.append((supplier_name, credit_balance, ""))
                for name, credit, phone in all_suppliers:
                    self.manual_credit_tree.insert('', tk.END, values=(
                        name, 
                        f"₹{credit:.2f}", 
                        phone if phone else "-"
                    ))
        except Exception as e:
            print(f"Error searching manual credit list: {str(e)}")
    def open_manual_credit_form(self, event):
        item = self.manual_credit_tree.selection()
        if not item:
            return
        values = self.manual_credit_tree.item(item, 'values')
        if not values:
            return
        name = values[0]
        current_credit = float(values[1].replace('₹', '').replace(',', ''))
        credit_type = self.credit_type_combo.get()
        dialog = tk.Toplevel(self.root)
        dialog.title("मॅन्युअल उधारी जोडा")
        dialog.geometry("450x350")
        dialog.configure(bg='white')
        dialog.transient(self.root)
        dialog.grab_set()
        self.center_dialog(dialog)
        tk.Label(dialog, text=f"{credit_type} उधारी जोडा", font=('Arial', 14, 'bold'), bg='white').pack(pady=10)
        form_frame = tk.Frame(dialog, bg='white')
        form_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        tk.Label(form_frame, text=f"{credit_type}:", bg='white', font=('Arial', 10)).grid(row=0, column=0, padx=5, pady=5, sticky='w')
        tk.Label(form_frame, text=name, bg='white', font=('Arial', 10, 'bold')).grid(row=0, column=1, padx=5, pady=5, sticky='w')
        tk.Label(form_frame, text="सध्याची उधारी:", bg='white', font=('Arial', 10)).grid(row=1, column=0, padx=5, pady=5, sticky='w')
        tk.Label(form_frame, text=f"₹{current_credit:.2f}", bg='white', font=('Arial', 10, 'bold')).grid(row=1, column=1, padx=5, pady=5, sticky='w')
        tk.Label(form_frame, text="नवीन उधारी:", bg='white', font=('Arial', 10)).grid(row=2, column=0, padx=5, pady=5, sticky='w')
        new_credit_entry = tk.Entry(form_frame, width=15, font=('Arial', 10))
        new_credit_entry.grid(row=2, column=1, padx=5, pady=5, sticky='w')
        new_credit_entry.insert(0, "0")
        tk.Label(form_frame, text="नवीन एकूण उधारी:", bg='white', font=('Arial', 10)).grid(row=3, column=0, padx=5, pady=5, sticky='w')
        new_total_label = tk.Label(form_frame, text=f"₹{current_credit:.2f}", bg='white', font=('Arial', 10, 'bold'), fg='#e94560')
        new_total_label.grid(row=3, column=1, padx=5, pady=5, sticky='w')
        def calculate_new_total(event=None):
            try:
                new_credit = float(new_credit_entry.get())
                new_total = current_credit + new_credit
                new_total_label.config(text=f"₹{new_total:.2f}")
            except:
                new_total_label.config(text=f"₹{current_credit:.2f}")
        new_credit_entry.bind('<KeyRelease>', calculate_new_total)
        tk.Label(form_frame, text="नोंद:", bg='white', font=('Arial', 10)).grid(row=4, column=0, padx=5, pady=5, sticky='w')
        note_entry = tk.Entry(form_frame, width=25, font=('Arial', 10))
        note_entry.grid(row=4, column=1, padx=5, pady=5, sticky='w')
        note_entry.insert(0, "मॅन्युअल उधारी जोडली")
        def add_credit():
            try:
                new_credit = float(new_credit_entry.get())
                if new_credit <= 0:
                    self.show_messagebox("त्रुटी", "उधारी रक्कम ० पेक्षा जास्त असावी")
                    return
                new_total = current_credit + new_credit
                note = note_entry.get()
                if credit_type == 'ग्राहक':
                    self.db.cursor.execute('''
                        UPDATE customers SET credit_balance = ? 
                        WHERE name = ?
                    ''', (new_total, name))
                    self.db.cursor.execute('''
                        INSERT INTO sales (invoice_no, customer_name, date, total_amount, 
                                         discount_amount, discount_type, paid_amount, 
                                         balance_amount, payment_mode, status, transaction_type)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        f"MAN-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        name,
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        new_credit,
                        0,
                        '₹',
                        0,
                        new_credit,
                        'उदारी',
                        'उदारी',
                        'मॅन्युअल उधारी'
                    ))
                else:
                    self.db.cursor.execute('''
                        UPDATE suppliers SET credit_balance = ? 
                        WHERE name = ?
                    ''', (new_total, name))
                    self.db.cursor.execute('''
                        INSERT INTO purchases (invoice_no, supplier_name, date, total_amount, 
                                             paid_amount, balance_amount, payment_mode, status, transaction_type)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        f"MAN-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        name,
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        new_credit,
                        0,
                        new_credit,
                        'उदारी',
                        'उदारी',
                        'मॅन्युअल उधारी'
                    ))
                self.db.conn.commit()
                dialog.destroy()
                self.load_manual_credit_list()
                self.load_customer_credit_data()
                self.load_supplier_credit_data()
            except ValueError:
                self.show_messagebox("त्रुटी", "कृपया वैध रक्कम प्रविष्ट करा")
            except Exception as e:
                self.show_messagebox("त्रुटी", f"उधारी जोड त्रुटी: {str(e)}")
        button_frame = tk.Frame(dialog, bg='white')
        button_frame.pack(pady=20)
        add_btn = tk.Button(button_frame, text="➕ उधारी जोडा", bg='#0fcea7', fg='white',
                           font=('Arial', 12, 'bold'), command=add_credit)
        add_btn.pack(side=tk.LEFT, padx=10)
        cancel_btn = tk.Button(button_frame, text="रद्द करा", bg='#e94560', fg='white',
                             font=('Arial', 12), command=dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=10)
    def setup_reports_content(self, parent):
        main_container = tk.Frame(parent, bg='white')
        main_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        header_frame = tk.Frame(main_container, bg='white')
        header_frame.pack(fill=tk.X, pady=(0, 15), padx=10)
        tk.Label(header_frame, text="📊 अहवाल", 
                font=('Arial', 20, 'bold'), bg='white').pack(side=tk.LEFT)
        self.reports_notebook = ttk.Notebook(main_container)
        self.reports_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        daily_report_tab = tk.Frame(self.reports_notebook, bg='white')
        self.reports_notebook.add(daily_report_tab, text="दैनिक अहवाल")
        self.setup_daily_report_tab(daily_report_tab)
        monthly_report_tab = tk.Frame(self.reports_notebook, bg='white')
        self.reports_notebook.add(monthly_report_tab, text="मासिक अहवाल")
        self.setup_monthly_report_tab(monthly_report_tab)
        credit_report_tab = tk.Frame(self.reports_notebook, bg='white')
        self.reports_notebook.add(credit_report_tab, text="उधारी अहवाल")
        self.setup_credit_report_tab(credit_report_tab)
    def refresh_settings_tab(self):
        """Refresh settings tab data"""
        try:
            self.db.cursor.execute("SELECT shop_name, owner_name, address, phone, email, gst_no FROM shop_info LIMIT 1")
            result = self.db.cursor.fetchone()
            if result and hasattr(self, 'shop_name_entry'):
                shop_name, owner_name, address, phone, email, gst_no = result
                self.shop_name_entry.delete(0, tk.END)
                self.shop_name_entry.insert(0, shop_name if shop_name else "")
                if hasattr(self, 'owner_name_entry'):
                    self.owner_name_entry.delete(0, tk.END)
                    self.owner_name_entry.insert(0, owner_name if owner_name else "")
                if hasattr(self, 'address_entry'):
                    self.address_entry.delete(0, tk.END)
                    self.address_entry.insert(0, address if address else "")
                if hasattr(self, 'phone_entry'):
                    self.phone_entry.delete(0, tk.END)
                    self.phone_entry.insert(0, phone if phone else "")
                if hasattr(self, 'email_entry'):
                    self.email_entry.delete(0, tk.END)
                    self.email_entry.insert(0, email if email else "")
                if hasattr(self, 'gst_entry'):
                    self.gst_entry.delete(0, tk.END)
                    self.gst_entry.insert(0, gst_no if gst_no else "")
            if hasattr(self, 'print_settings_tree'):
                for item in self.print_settings_tree.get_children():
                    self.print_settings_tree.delete(item)
                self.db.cursor.execute("SELECT header_text, footer_text, font_size FROM print_settings")
                settings = self.db.cursor.fetchall()
                for i, setting in enumerate(settings, 1):
                    header, footer, font_size = setting
                    self.print_settings_tree.insert('', tk.END, values=(
                        i,
                        header if header else "",
                        footer if footer else "",
                        font_size if font_size else "10"
                    ))
            if hasattr(self, 'backup_settings_tree'):
                for item in self.backup_settings_tree.get_children():
                    self.backup_settings_tree.delete(item)
                self.db.cursor.execute("SELECT auto_backup, backup_path, backup_interval_hours, keep_days FROM backup_settings")
                settings = self.db.cursor.fetchall()
                for i, setting in enumerate(settings, 1):
                    auto_backup, backup_path, interval, keep_days = setting
                    self.backup_settings_tree.insert('', tk.END, values=(
                        i,
                        "होय" if auto_backup == 1 else "नाही",
                        backup_path if backup_path else "-",
                        f"{interval} तास" if interval else "-",
                        f"{keep_days} दिवस" if keep_days else "-"
                    ))
            if hasattr(self, 'users_tree'):
                for item in self.users_tree.get_children():
                    self.users_tree.delete(item)
                self.db.cursor.execute("SELECT username, full_name, user_type FROM users")
                users = self.db.cursor.fetchall()
                for i, user in enumerate(users, 1):
                    username, full_name, user_type = user
                    self.users_tree.insert('', tk.END, values=(
                        i,
                        username,
                        full_name if full_name else "",
                        "व्यवस्थापक" if user_type == "admin" else "वापरकर्ता"
                    ))
        except Exception as e:
            print(f"Settings tab refresh error: {e}")
    def setup_daily_report_tab(self, parent):
        main_frame = tk.Frame(parent, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        tk.Label(main_frame, text="📅 दैनिक अहवाल", 
                font=('Arial', 16, 'bold'), bg='white').pack(pady=(0, 20))
        filter_frame = tk.LabelFrame(main_frame, text="तारीख निवडा", bg='white', font=('Arial', 10, 'bold'))
        filter_frame.pack(fill=tk.X, pady=(0, 20))
        tk.Label(filter_frame, text="तारीख:", bg='white', font=('Arial', 10)).grid(row=0, column=0, padx=10, pady=10)
        self.daily_date_entry = DateEntry(filter_frame, width=15, font=('Arial', 10), date_pattern='dd/mm/yyyy')
        self.daily_date_entry.grid(row=0, column=1, padx=10, pady=10)
        self.daily_date_entry.bind('<Return>', lambda e: self.generate_daily_report())
        generate_btn = tk.Button(filter_frame, text="📊 जनरेट करा", bg='#3a86ff', fg='white',
                               font=('Arial', 10), command=self.generate_daily_report)
        generate_btn.grid(row=0, column=2, padx=10, pady=10)
        button_frame = tk.Frame(main_frame, bg='white')
        button_frame.pack(fill=tk.X, pady=20)
        print_btn = tk.Button(button_frame, text="🖨️ प्रिंट करा", bg='#f0a500', fg='white',
                            font=('Arial', 10), width=15, command=self.print_daily_report)
        print_btn.pack(side=tk.LEFT, padx=10)
        export_btn = tk.Button(button_frame, text="📁 PDF एक्सपोर्ट करा", bg='#0fcea7', fg='white',
                             font=('Arial', 10), width=15, command=self.export_daily_report_pdf)
        export_btn.pack(side=tk.LEFT, padx=10)
    def generate_daily_report(self):
        date_obj = self.daily_date_entry.get_date()
        date_str = date_obj.strftime("%Y-%m-%d")
        try:
            report_window = tk.Toplevel(self.root)
            report_window.title(f"दैनिक अहवाल - {date_obj.strftime('%d/%m/%Y')}")
            report_window.geometry("1000x700")
            report_window.configure(bg='white')
            self.center_dialog(report_window)
            text_widget = tk.Text(report_window, bg='white', font=('Arial', 11), wrap=tk.WORD)
            scrollbar = tk.Scrollbar(report_window, command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            report_data = self.get_daily_report_data(date_str)
            text_widget.insert(tk.END, report_data)
            text_widget.config(state=tk.DISABLED)
            export_btn = tk.Button(report_window, text="📁 PDF एक्सपोर्ट करा", bg='#0fcea7', fg='white',
                                 font=('Arial', 12, 'bold'), command=lambda: self.export_daily_report_pdf(date_str))
            export_btn.pack(pady=10)
        except:
            pass
    def get_daily_report_data(self, date_str):
        try:
            report = ""
            report += "="*70 + "\n"
            report += f"{'दैनिक अहवाल':^70}\n"
            report += f"{self.shop_name:^70}\n"
            report += f"{'तारीख: ' + datetime.strptime(date_str, '%Y-%m-%d').strftime('%d/%m/%Y'):^70}\n"
            report += "="*70 + "\n\n"
            report += "📊 विक्री सारांश:\n"
            report += "-"*70 + "\n"
            self.db.cursor.execute('''
                SELECT SUM(total_amount) as total, SUM(paid_amount) as paid, SUM(balance_amount) as balance
                FROM sales 
                WHERE DATE(date) = ? AND transaction_type = 'विक्री'
            ''', (date_str,))
            sales_result = self.db.cursor.fetchone()
            total_sales = sales_result[0] or 0
            paid_sales = sales_result[1] or 0
            balance_sales = sales_result[2] or 0
            report += f"एकूण विक्री: ₹{total_sales:,.2f}\n"
            report += f"जमा रक्कम: ₹{paid_sales:,.2f}\n"
            report += f"बाकी रक्कम: ₹{balance_sales:,.2f}\n\n"
            report += "🛒 खरेदी सारांश:\n"
            report += "-"*70 + "\n"
            self.db.cursor.execute('''
                SELECT SUM(total_amount) as total, SUM(paid_amount) as paid, SUM(balance_amount) as balance
                FROM purchases 
                WHERE DATE(date) = ? AND transaction_type = 'खरेदी'
            ''', (date_str,))
            purchase_result = self.db.cursor.fetchone()
            total_purchase = purchase_result[0] or 0
            paid_purchase = purchase_result[1] or 0
            balance_purchase = purchase_result[2] or 0
            report += f"एकूण खरेदी: ₹{total_purchase:,.2f}\n"
            report += f"जमा रक्कम: ₹{paid_purchase:,.2f}\n"
            report += f"बाकी रक्कम: ₹{balance_purchase:,.2f}\n\n"
            report += "💳 उधारी सारांश:\n"
            report += "-"*70 + "\n"
            report += f"एकूण उधारी येणे (ग्राहक): ₹{balance_sales:,.2f}\n"
            report += f"एकूण उधारी देणे (पुरवठादार): ₹{balance_purchase:,.2f}\n\n"
            self.db.cursor.execute('''
                SELECT SUM(paid_amount) as total_paid
                FROM sales 
                WHERE DATE(date) = ? AND transaction_type = 'पेमेंट' AND balance_amount < 0
            ''', (date_str,))
            customer_payment_result = self.db.cursor.fetchone()
            total_customer_payment = customer_payment_result[0] or 0
            self.db.cursor.execute('''
                SELECT SUM(paid_amount) as total_paid
                FROM purchases 
                WHERE DATE(date) = ? AND transaction_type = 'पेमेंट' AND balance_amount < 0
            ''', (date_str,))
            supplier_payment_result = self.db.cursor.fetchone()
            total_supplier_payment = supplier_payment_result[0] or 0
            report += f"एकूण उधारी आली (ग्राहक): ₹{total_customer_payment:,.2f}\n"
            report += f"एकूण उधारी दिली (पुरवठादार): ₹{total_supplier_payment:,.2f}\n\n"
            report += "💰 एकूण शिल्लक:\n"
            report += "-"*70 + "\n"
            net_balance = (total_sales - total_purchase) + (total_customer_payment - total_supplier_payment)
            report += f"एकूण नफा/तोटा: ₹{net_balance:,.2f}\n\n"
            report += "="*70 + "\n"
            report += f"{'तयार केल्याची वेळ: ' + datetime.now().strftime('%d/%m/%Y %H:%M:%S'):^70}\n"
            report += "="*70 + "\n"
            return report
        except Exception as e:
            return f"त्रुटी: {str(e)}"
    def print_daily_report(self):
        try:
            temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
            pdf_path = temp_file.name
            doc = SimpleDocTemplate(pdf_path, pagesize=A4)
            elements = []
            styles = getSampleStyleSheet()
            title_style = styles['Heading1']
            title_style.alignment = 1
            title_style.textColor = colors.HexColor('#1a1a2e')
            subtitle_style = styles['Heading2']
            subtitle_style.alignment = 1
            subtitle_style.textColor = colors.HexColor('#e94560')
            normal_style = styles['Normal']
            elements.append(Paragraph("दैनिक अहवाल", title_style))
            elements.append(Paragraph(self.shop_name, subtitle_style))
            elements.append(Paragraph(f"तारीख: {self.daily_date_entry.get_date().strftime('%d/%m/%Y')}", normal_style))
            elements.append(Paragraph("="*50, normal_style))
            elements.append(Paragraph("<br/>", normal_style))
            date_str = self.daily_date_entry.get_date().strftime("%Y-%m-%d")
            report_data = self.get_daily_report_data(date_str)
            lines = report_data.split('\n')
            for line in lines:
                if line.strip():
                    if line.startswith('=') or line.startswith('-'):
                        elements.append(Paragraph(line, normal_style))
                    elif ':' in line:
                        parts = line.split(':')
                        if len(parts) >= 2:
                            bold_text = f"<b>{parts[0]}:</b> {':'.join(parts[1:])}"
                            elements.append(Paragraph(bold_text, normal_style))
                    else:
                        elements.append(Paragraph(line, normal_style))
                    elements.append(Paragraph("<br/>", normal_style))
            elements.append(Paragraph(f"तयार केल्याची वेळ: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", normal_style))
            doc.build(elements)
            if sys.platform == "win32":
                os.startfile(pdf_path, "print")
            elif sys.platform == "darwin":
                subprocess.Popen(['open', pdf_path])
            else:
                subprocess.Popen(['xdg-open', pdf_path])
        except:
            pass
    def export_daily_report_pdf(self, date_str=None):
        if not date_str:
            date_obj = self.daily_date_entry.get_date()
            date_str = date_obj.strftime("%Y-%m-%d")
        try:
            temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
            pdf_path = temp_file.name
            doc = SimpleDocTemplate(pdf_path, pagesize=A4)
            elements = []
            styles = getSampleStyleSheet()
            title_style = styles['Heading1']
            title_style.alignment = 1
            title_style.textColor = colors.HexColor('#1a1a2e')
            subtitle_style = styles['Heading2']
            subtitle_style.alignment = 1
            subtitle_style.textColor = colors.HexColor('#e94560')
            normal_style = styles['Normal']
            elements.append(Paragraph("दैनिक अहवाल", title_style))
            elements.append(Paragraph(self.shop_name, subtitle_style))
            elements.append(Paragraph(f"तारीख: {datetime.strptime(date_str, '%Y-%m-%d').strftime('%d/%m/%Y')}", normal_style))
            elements.append(Paragraph("="*50, normal_style))
            elements.append(Paragraph("<br/>", normal_style))
            report_data = self.get_daily_report_data(date_str)
            lines = report_data.split('\n')
            for line in lines:
                if line.strip():
                    if line.startswith('=') or line.startswith('-'):
                        elements.append(Paragraph(line, normal_style))
                    elif ':' in line:
                        parts = line.split(':')
                        if len(parts) >= 2:
                            bold_text = f"<b>{parts[0]}:</b> {':'.join(parts[1:])}"
                            elements.append(Paragraph(bold_text, normal_style))
                    else:
                        elements.append(Paragraph(line, normal_style))
                    elements.append(Paragraph("<br/>", normal_style))
            elements.append(Paragraph(f"तयार केल्याची वेळ: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", normal_style))
            doc.build(elements)
            webbrowser.open(pdf_path)
        except:
            pass
    def setup_monthly_report_tab(self, parent):
        main_frame = tk.Frame(parent, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        tk.Label(main_frame, text="📆 मासिक अहवाल", 
                font=('Arial', 16, 'bold'), bg='white').pack(pady=(0, 20))
        filter_frame = tk.LabelFrame(main_frame, text="महिना निवडा", bg='white', font=('Arial', 10, 'bold'))
        filter_frame.pack(fill=tk.X, pady=(0, 20))
        current_year = datetime.now().year
        months = ["जानेवारी", "फेब्रुवारी", "मार्च", "एप्रिल", "मे", "जून", 
                 "जुलै", "ऑगस्ट", "सप्टेंबर", "ऑक्टोबर", "नोव्हेंबर", "डिसेंबर"]
        tk.Label(filter_frame, text="महिना:", bg='white', font=('Arial', 10)).grid(row=0, column=0, padx=10, pady=10)
        self.month_combo = ttk.Combobox(filter_frame, values=months, width=15, font=('Arial', 10))
        self.month_combo.grid(row=0, column=1, padx=10, pady=10)
        self.month_combo.current(datetime.now().month - 1)
        self.month_combo.bind('<Return>', lambda e: self.year_entry.focus())
        tk.Label(filter_frame, text="वर्ष:", bg='white', font=('Arial', 10)).grid(row=0, column=2, padx=10, pady=10)
        self.year_entry = tk.Entry(filter_frame, width=10, font=('Arial', 10))
        self.year_entry.grid(row=0, column=3, padx=10, pady=10)
        self.year_entry.insert(0, str(current_year))
        self.year_entry.bind('<Return>', lambda e: self.generate_monthly_report())
        generate_btn = tk.Button(filter_frame, text="📊 जनरेट करा", bg='#3a86ff', fg='white',
                               font=('Arial', 10), command=self.generate_monthly_report)
        generate_btn.grid(row=0, column=4, padx=10, pady=10)
        button_frame = tk.Frame(main_frame, bg='white')
        button_frame.pack(fill=tk.X, pady=20)
        print_btn = tk.Button(button_frame, text="🖨️ प्रिंट करा", bg='#f0a500', fg='white',
                            font=('Arial', 10), width=15, command=self.print_monthly_report)
        print_btn.pack(side=tk.LEFT, padx=10)
        export_btn = tk.Button(button_frame, text="📁 PDF एक्सपोर्ट करा", bg='#0fcea7', fg='white',
                             font=('Arial', 10), width=15, command=self.export_monthly_report_pdf)
        export_btn.pack(side=tk.LEFT, padx=10)
    def generate_monthly_report(self):
        month_index = self.month_combo.current() + 1
        year = self.year_entry.get()
        try:
            month = month_index
            year = int(year)
            from_date = f"{year}-{month:02d}-01"
            if month == 12:
                next_month = 1
                next_year = year + 1
            else:
                next_month = month + 1
                next_year = year
            to_date = f"{next_year}-{next_month:02d}-01"
            report_window = tk.Toplevel(self.root)
            report_window.title(f"मासिक अहवाल - {self.month_combo.get()} {year}")
            report_window.geometry("1000x700")
            report_window.configure(bg='white')
            self.center_dialog(report_window)
            text_widget = tk.Text(report_window, bg='white', font=('Arial', 11), wrap=tk.WORD)
            scrollbar = tk.Scrollbar(report_window, command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            report_data = self.get_monthly_report_data(from_date, to_date, month_index, year)
            text_widget.insert(tk.END, report_data)
            text_widget.config(state=tk.DISABLED)
            export_btn = tk.Button(report_window, text="📁 PDF एक्सपोर्ट करा", bg='#0fcea7', fg='white',
                                 font=('Arial', 12, 'bold'), command=lambda: self.export_monthly_report_pdf(from_date, to_date, month_index, year))
            export_btn.pack(pady=10)
        except:
            pass
    def get_monthly_report_data(self, from_date, to_date, month, year):
        try:
            report = ""
            report += "="*70 + "\n"
            report += f"{'मासिक अहवाल':^70}\n"
            report += f"{self.shop_name:^70}\n"
            report += f"{'महिना: ' + self.month_combo.get() + ' ' + str(year):^70}\n"
            report += "="*70 + "\n\n"
            report += "📊 विक्री सारांश:\n"
            report += "-"*70 + "\n"
            self.db.cursor.execute('''
                SELECT SUM(total_amount) as total, SUM(paid_amount) as paid, SUM(balance_amount) as balance
                FROM sales 
                WHERE date >= ? AND date < ? AND transaction_type = 'विक्री'
            ''', (from_date, to_date))
            sales_result = self.db.cursor.fetchone()
            total_sales = sales_result[0] or 0
            paid_sales = sales_result[1] or 0
            balance_sales = sales_result[2] or 0
            report += f"एकूण विक्री: ₹{total_sales:,.2f}\n"
            report += f"जमा रक्कम: ₹{paid_sales:,.2f}\n"
            report += f"बाकी रक्कम: ₹{balance_sales:,.2f}\n\n"
            report += "🛒 खरेदी सारांश:\n"
            report += "-"*70 + "\n"
            self.db.cursor.execute('''
                SELECT SUM(total_amount) as total, SUM(paid_amount) as paid, SUM(balance_amount) as balance
                FROM purchases 
                WHERE date >= ? AND date < ? AND transaction_type = 'खरेदी'
            ''', (from_date, to_date))
            purchase_result = self.db.cursor.fetchone()
            total_purchase = purchase_result[0] or 0
            paid_purchase = purchase_result[1] or 0
            balance_purchase = purchase_result[2] or 0
            report += f"एकूण खरेदी: ₹{total_purchase:,.2f}\n"
            report += f"जमा रक्कम: ₹{paid_purchase:,.2f}\n"
            report += f"बाकी रक्कम: ₹{balance_purchase:,.2f}\n\n"
            report += "💳 उधारी सारांश:\n"
            report += "-"*70 + "\n"
            report += f"एकूण उधारी येणे (ग्राहक): ₹{balance_sales:,.2f}\n"
            report += f"एकूण उधारी देणे (पुरवठादार): ₹{balance_purchase:,.2f}\n\n"
            report += "📈 दैनंदिन विक्री:\n"
            report += "-"*70 + "\n"
            self.db.cursor.execute('''
                SELECT DATE(date) as sale_date, COUNT(*) as count, SUM(total_amount) as total
                FROM sales 
                WHERE date >= ? AND date < ? AND transaction_type = 'विक्री'
                GROUP BY DATE(date)
                ORDER BY sale_date
            ''', (from_date, to_date))
            daily_sales = self.db.cursor.fetchall()
            if daily_sales:
                for sale in daily_sales:
                    sale_date, count, total = sale
                    formatted_date = datetime.strptime(sale_date, '%Y-%m-%d').strftime('%d/%m/%Y')
                    report += f"{formatted_date}: {count} विक्री, ₹{total or 0:,.2f}\n"
            else:
                report += "कोणतीही विक्री नाही\n"
            report += "\n"
            self.db.cursor.execute('''
                SELECT SUM(paid_amount) as total_paid
                FROM sales 
                WHERE date >= ? AND date < ? AND transaction_type = 'पेमेंट' AND balance_amount < 0
            ''', (from_date, to_date))
            customer_payment_result = self.db.cursor.fetchone()
            total_customer_payment = customer_payment_result[0] or 0
            self.db.cursor.execute('''
                SELECT SUM(paid_amount) as total_paid
                FROM purchases 
                WHERE date >= ? AND date < ? AND transaction_type = 'पेमेंट' AND balance_amount < 0
            ''', (from_date, to_date))
            supplier_payment_result = self.db.cursor.fetchone()
            total_supplier_payment = supplier_payment_result[0] or 0
            report += "💰 एकूण शिल्लक:\n"
            report += "-"*70 + "\n"
            net_balance = (total_sales - total_purchase) + (total_customer_payment - total_supplier_payment)
            report += f"एकूण नफा/तोटा: ₹{net_balance:,.2f}\n\n"
            report += "="*70 + "\n"
            report += f"{'तयार केल्याची वेळ: ' + datetime.now().strftime('%d/%m/%Y %H:%M:%S'):^70}\n"
            report += "="*70 + "\n"
            return report
        except Exception as e:
            return f"त्रुटी: {str(e)}"
    def print_monthly_report(self):
        try:
            month_index = self.month_combo.current() + 1
            year = int(self.year_entry.get())
            month = month_index
            from_date = f"{year}-{month:02d}-01"
            if month == 12:
                next_month = 1
                next_year = year + 1
            else:
                next_month = month + 1
                next_year = year
            to_date = f"{next_year}-{next_month:02d}-01"
            temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
            pdf_path = temp_file.name
            doc = SimpleDocTemplate(pdf_path, pagesize=A4)
            elements = []
            styles = getSampleStyleSheet()
            title_style = styles['Heading1']
            title_style.alignment = 1
            title_style.textColor = colors.HexColor('#1a1a2e')
            subtitle_style = styles['Heading2']
            subtitle_style.alignment = 1
            subtitle_style.textColor = colors.HexColor('#e94560')
            normal_style = styles['Normal']
            elements.append(Paragraph("मासिक अहवाल", title_style))
            elements.append(Paragraph(self.shop_name, subtitle_style))
            elements.append(Paragraph(f"महिना: {self.month_combo.get()} {year}", normal_style))
            elements.append(Paragraph("="*50, normal_style))
            elements.append(Paragraph("<br/>", normal_style))
            report_data = self.get_monthly_report_data(from_date, to_date, month, year)
            lines = report_data.split('\n')
            for line in lines:
                if line.strip():
                    if line.startswith('=') or line.startswith('-'):
                        elements.append(Paragraph(line, normal_style))
                    elif ':' in line:
                        parts = line.split(':')
                        if len(parts) >= 2:
                            bold_text = f"<b>{parts[0]}:</b> {':'.join(parts[1:])}"
                            elements.append(Paragraph(bold_text, normal_style))
                    else:
                        elements.append(Paragraph(line, normal_style))
                    elements.append(Paragraph("<br/>", normal_style))
            elements.append(Paragraph(f"तयार केल्याची वेळ: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", normal_style))
            doc.build(elements)
            if sys.platform == "win32":
                os.startfile(pdf_path, "print")
            elif sys.platform == "darwin":
                subprocess.Popen(['open', pdf_path])
            else:
                subprocess.Popen(['xdg-open', pdf_path])
        except:
            pass
    def export_monthly_report_pdf(self, from_date=None, to_date=None, month=None, year=None):
        if not from_date:
            month_index = self.month_combo.current() + 1
            year = int(self.year_entry.get())
            month = month_index
            from_date = f"{year}-{month:02d}-01"
            if month == 12:
                next_month = 1
                next_year = year + 1
            else:
                next_month = month + 1
                next_year = year
            to_date = f"{next_year}-{next_month:02d}-01"
        try:
            temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
            pdf_path = temp_file.name
            doc = SimpleDocTemplate(pdf_path, pagesize=A4)
            elements = []
            styles = getSampleStyleSheet()
            title_style = styles['Heading1']
            title_style.alignment = 1
            title_style.textColor = colors.HexColor('#1a1a2e')
            subtitle_style = styles['Heading2']
            subtitle_style.alignment = 1
            subtitle_style.textColor = colors.HexColor('#e94560')
            normal_style = styles['Normal']
            elements.append(Paragraph("मासिक अहवाल", title_style))
            elements.append(Paragraph(self.shop_name, subtitle_style))
            elements.append(Paragraph(f"महिना: {self.month_combo.get()} {year}", normal_style))
            elements.append(Paragraph("="*50, normal_style))
            elements.append(Paragraph("<br/>", normal_style))
            report_data = self.get_monthly_report_data(from_date, to_date, month, year)
            lines = report_data.split('\n')
            for line in lines:
                if line.strip():
                    if line.startswith('=') or line.startswith('-'):
                        elements.append(Paragraph(line, normal_style))
                    elif ':' in line:
                        parts = line.split(':')
                        if len(parts) >= 2:
                            bold_text = f"<b>{parts[0]}:</b> {':'.join(parts[1:])}"
                            elements.append(Paragraph(bold_text, normal_style))
                    else:
                        elements.append(Paragraph(line, normal_style))
                    elements.append(Paragraph("<br/>", normal_style))
            elements.append(Paragraph(f"तयार केल्याची वेळ: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", normal_style))
            doc.build(elements)
            webbrowser.open(pdf_path)
        except:
            pass
    def setup_credit_report_tab(self, parent):
        main_frame = tk.Frame(parent, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        tk.Label(main_frame, text="💳 उधारी अहवाल", 
                font=('Arial', 16, 'bold'), bg='white').pack(pady=(0, 20))
        button_frame = tk.Frame(main_frame, bg='white')
        button_frame.pack(pady=20)
        customer_credit_btn = tk.Button(button_frame, text="👥 ग्राहक उधारी (येणे बाकी)", bg='#3a86ff', fg='white',
                                       font=('Arial', 12, 'bold'), width=25, command=self.show_customer_credit_report)
        customer_credit_btn.pack(pady=10)
        supplier_credit_btn = tk.Button(button_frame, text="🏭 पुरवठादार उधारी (देणे बाकी)", bg='#e94560', fg='white',
                                       font=('Arial', 12, 'bold'), width=25, command=self.show_supplier_credit_report)
        supplier_credit_btn.pack(pady=10)
    def show_customer_credit_report(self):
        try:
            self.db.cursor.execute('''
                SELECT name, credit_balance, phone 
                FROM customers 
                WHERE credit_balance > 0 AND name NOT LIKE 'CUST-%'
                ORDER BY credit_balance DESC
            ''')
            customers = self.db.cursor.fetchall()
            report_window = tk.Toplevel(self.root)
            report_window.title("ग्राहक उधारी अहवाल")
            report_window.geometry("1000x700")
            report_window.configure(bg='white')
            self.center_dialog(report_window)
            text_widget = tk.Text(report_window, bg='white', font=('Arial', 11), wrap=tk.WORD)
            scrollbar = tk.Scrollbar(report_window, command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            report = "="*70 + "\n"
            report += f"{'ग्राहक उधारी अहवाल (येणे बाकी)':^70}\n"
            report += f"{self.shop_name:^70}\n"
            report += f"{'तारीख: ' + datetime.now().strftime('%d/%m/%Y'):^70}\n"
            report += "="*70 + "\n\n"
            total_credit = 0
            if customers:
                report += f"{'क्रमांक':<5} {'ग्राहक नाव':<30} {'फोन':<15} {'उधारी रक्कम':>15}\n"
                report += "-"*70 + "\n"
                for i, customer in enumerate(customers, 1):
                    name, credit, phone = customer
                    total_credit += credit
                    report += f"{i:<5} {name:<30} {(phone if phone else '-'):<15} ₹{credit:>12,.2f}\n"
                report += "-"*70 + "\n"
                report += f"{'एकूण':<50} ₹{total_credit:>12,.2f}\n\n"
            else:
                report += "कोणतेही ग्राहक उधारी नाही\n\n"
            report += "="*70 + "\n"
            report += f"{'तयार केल्याची वेळ: ' + datetime.now().strftime('%d/%m/%Y %H:%M:%S'):^70}\n"
            report += "="*70 + "\n"
            text_widget.insert(tk.END, report)
            text_widget.config(state=tk.DISABLED)
        except:
            pass
    def show_supplier_credit_report(self):
        try:
            self.db.cursor.execute('''
                SELECT name, credit_balance, phone 
                FROM suppliers 
                WHERE credit_balance > 0
                ORDER BY credit_balance DESC
            ''')
            suppliers = self.db.cursor.fetchall()
            report_window = tk.Toplevel(self.root)
            report_window.title("पुरवठादार उधारी अहवाल")
            report_window.geometry("1000x700")
            report_window.configure(bg='white')
            self.center_dialog(report_window)
            text_widget = tk.Text(report_window, bg='white', font=('Arial', 11), wrap=tk.WORD)
            scrollbar = tk.Scrollbar(report_window, command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            report = "="*70 + "\n"
            report += f"{'पुरवठादार उधारी अहवाल (देणे बाकी)':^70}\n"
            report += f"{self.shop_name:^70}\n"
            report += f"{'तारीख: ' + datetime.now().strftime('%d/%m/%Y'):^70}\n"
            report += "="*70 + "\n\n"
            total_credit = 0
            if suppliers:
                report += f"{'क्रमांक':<5} {'पुरवठादार नाव':<30} {'फोन':<15} {'उधारी रक्कम':>15}\n"
                report += "-"*70 + "\n"
                for i, supplier in enumerate(suppliers, 1):
                    name, credit, phone = supplier
                    total_credit += credit
                    report += f"{i:<5} {name:<30} {(phone if phone else '-'):<15} ₹{credit:>12,.2f}\n"
                report += "-"*70 + "\n"
                report += f"{'एकूण':<50} ₹{total_credit:>12,.2f}\n\n"
            else:
                report += "कोणतीही पुरवठादार उधारी नाही\n\n"
            report += "="*70 + "\n"
            report += f"{'तयार केल्याची वेळ: ' + datetime.now().strftime('%d/%m/%Y %H:%M:%S'):^70}\n"
            report += "="*70 + "\n"
            text_widget.insert(tk.END, report)
            text_widget.config(state=tk.DISABLED)
        except:
            pass
    def export_customer_credit_report_pdf(self, customers, total_credit):
        try:
            temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
            pdf_path = temp_file.name
            doc = SimpleDocTemplate(pdf_path, pagesize=A4)
            elements = []
            styles = getSampleStyleSheet()
            title_style = styles['Heading1']
            title_style.alignment = 1
            title_style.textColor = colors.HexColor('#3a86ff')
            subtitle_style = styles['Heading2']
            subtitle_style.alignment = 1
            subtitle_style.textColor = colors.HexColor('#1a1a2e')
            normal_style = styles['Normal']
            elements.append(Paragraph("ग्राहक उधारी अहवाल (येणे बाकी)", title_style))
            elements.append(Paragraph(self.shop_name, subtitle_style))
            elements.append(Paragraph(f"तारीख: {datetime.now().strftime('%d/%m/%Y')}", normal_style))
            elements.append(Paragraph("="*50, normal_style))
            elements.append(Paragraph("<br/>", normal_style))
            if customers:
                table_data = [['क्रमांक', 'ग्राहक नाव', 'फोन', 'उधारी रक्कम']]
                for i, customer in enumerate(customers, 1):
                    name, credit, phone = customer
                    table_data.append([str(i), name, phone if phone else '-', f"₹{credit:,.2f}"])
                table_data.append(['', '', 'एकूण:', f"₹{total_credit:,.2f}"])
                table = Table(table_data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3a86ff')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -2), colors.white),
                    ('TEXTCOLOR', (0, 1), (-1, -2), colors.black),
                    ('ALIGN', (3, 1), (3, -1), 'RIGHT'),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -2), 1, colors.grey),
                    ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f0a500')),
                    ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
                    ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ]))
                elements.append(table)
                elements.append(Paragraph("<br/>", normal_style))
            else:
                elements.append(Paragraph("कोणतेही ग्राहक उधारी नाही", normal_style))
                elements.append(Paragraph("<br/>", normal_style))
            elements.append(Paragraph(f"तयार केल्याची वेळ: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", normal_style))
            doc.build(elements)
            webbrowser.open(pdf_path)
        except:
            pass
    def export_supplier_credit_report_pdf(self, suppliers, total_credit):
        try:
            temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
            pdf_path = temp_file.name
            doc = SimpleDocTemplate(pdf_path, pagesize=A4)
            elements = []
            styles = getSampleStyleSheet()
            title_style = styles['Heading1']
            title_style.alignment = 1
            title_style.textColor = colors.HexColor('#e94560')
            subtitle_style = styles['Heading2']
            subtitle_style.alignment = 1
            subtitle_style.textColor = colors.HexColor('#1a1a2e')
            normal_style = styles['Normal']
            elements.append(Paragraph("पुरवठादार उधारी अहवाल (देणे बाकी)", title_style))
            elements.append(Paragraph(self.shop_name, subtitle_style))
            elements.append(Paragraph(f"तारीख: {datetime.now().strftime('%d/%m/%Y')}", normal_style))
            elements.append(Paragraph("="*50, normal_style))
            elements.append(Paragraph("<br/>", normal_style))
            if suppliers:
                table_data = [['क्रमांक', 'पुरवठादार नाव', 'फोन', 'उधारी रक्कम']]
                for i, supplier in enumerate(suppliers, 1):
                    name, credit, phone = supplier
                    table_data.append([str(i), name, phone if phone else '-', f"₹{credit:,.2f}"])
                table_data.append(['', '', 'एकूण:', f"₹{total_credit:,.2f}"])
                table = Table(table_data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e94560')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -2), colors.white),
                    ('TEXTCOLOR', (0, 1), (-1, -2), colors.black),
                    ('ALIGN', (3, 1), (3, -1), 'RIGHT'),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -2), 1, colors.grey),
                    ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f0a500')),
                    ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
                    ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ]))
                elements.append(table)
                elements.append(Paragraph("<br/>", normal_style))
            else:
                elements.append(Paragraph("कोणतीही पुरवठादार उधारी नाही", normal_style))
                elements.append(Paragraph("<br/>", normal_style))
            elements.append(Paragraph(f"तयार केल्याची वेळ: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", normal_style))
            doc.build(elements)
            webbrowser.open(pdf_path)
        except:
            pass
    def setup_settings_content(self, parent):
        main_container = tk.Frame(parent, bg='white')
        main_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        header_frame = tk.Frame(main_container, bg='white')
        header_frame.pack(fill=tk.X, pady=(0, 15), padx=10)
        tk.Label(header_frame, text="⚙️ सेटिंग", 
                font=('Arial', 20, 'bold'), bg='white').pack(side=tk.LEFT)
        self.settings_notebook = ttk.Notebook(main_container)
        self.settings_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        business_info_tab = tk.Frame(self.settings_notebook, bg='white')
        self.settings_notebook.add(business_info_tab, text="व्यवसाय माहिती")
        self.setup_business_info_tab(business_info_tab)
        print_settings_tab = tk.Frame(self.settings_notebook, bg='white')
        self.settings_notebook.add(print_settings_tab, text="बिल प्रिंटिंग सेटिंग")
        self.setup_print_settings_tab(print_settings_tab)
        backup_tab = tk.Frame(self.settings_notebook, bg='white')
        self.settings_notebook.add(backup_tab, text="बॅकअप")
        self.setup_backup_tab(backup_tab)
        user_settings_tab = tk.Frame(self.settings_notebook, bg='white')
        self.settings_notebook.add(user_settings_tab, text="वापरकर्ते सेटिंग")
        self.setup_user_settings_tab(user_settings_tab)
    def refresh_settings_tab(self):
        self.load_backup_settings()
        self.load_print_settings()
    def setup_business_info_tab(self, parent):
        main_frame = tk.Frame(parent, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        tk.Label(main_frame, text="🏢 व्यवसाय माहिती", 
                font=('Arial', 16, 'bold'), bg='white').pack(pady=(0, 20))
        form_frame = tk.LabelFrame(main_frame, text="माहिती भरा", bg='white', font=('Arial', 10, 'bold'))
        form_frame.pack(fill=tk.X, pady=(0, 20))
        tk.Label(form_frame, text="दुकानाचे नाव:", bg='white', font=('Arial', 10)).grid(row=0, column=0, padx=10, pady=10, sticky='w')
        self.shop_name_entry = tk.Entry(form_frame, width=40, font=('Arial', 10))
        self.shop_name_entry.grid(row=0, column=1, padx=10, pady=10, sticky='w')
        self.shop_name_entry.insert(0, self.shop_name)
        self.shop_name_entry.bind('<Return>', lambda e: self.owner_name_entry.focus())
        tk.Label(form_frame, text="मालकाचे नाव:", bg='white', font=('Arial', 10)).grid(row=1, column=0, padx=10, pady=10, sticky='w')
        self.owner_name_entry = tk.Entry(form_frame, width=40, font=('Arial', 10))
        self.owner_name_entry.grid(row=1, column=1, padx=10, pady=10, sticky='w')
        self.owner_name_entry.bind('<Return>', lambda e: self.address_entry.focus())
        tk.Label(form_frame, text="पत्ता:", bg='white', font=('Arial', 10)).grid(row=2, column=0, padx=10, pady=10, sticky='w')
        self.address_entry = tk.Entry(form_frame, width=40, font=('Arial', 10))
        self.address_entry.grid(row=2, column=1, padx=10, pady=10, sticky='w')
        self.address_entry.bind('<Return>', lambda e: self.save_business_info())
        def save_business_info():
            shop_name = self.shop_name_entry.get().strip()
            owner_name = self.owner_name_entry.get().strip()
            address = self.address_entry.get().strip()
            if not shop_name:
                self.show_messagebox("त्रुटी", "कृपया दुकानाचे नाव प्रविष्ट करा")
                return
            try:
                self.db.cursor.execute("SELECT COUNT(*) FROM shop_info")
                count = self.db.cursor.fetchone()[0]
                if count == 0:
                    self.db.cursor.execute('''
                        INSERT INTO shop_info (shop_name, owner_name, address)
                        VALUES (?, ?, ?)
                    ''', (shop_name, owner_name, address))
                else:
                    self.db.cursor.execute('''
                        UPDATE shop_info SET shop_name = ?, owner_name = ?, address = ?
                    ''', (shop_name, owner_name, address))
                self.db.conn.commit()
                self.shop_name = shop_name
                self.root.title(f"{self.shop_name} आवृत्ती १.१.०")
                self.show_messagebox("यशस्वी", "व्यवसाय माहिती अपडेट झाली")
            except Exception as e:
                self.show_messagebox("त्रुटी", f"माहिती सेव्ह त्रुटी: {str(e)}")
        save_btn = tk.Button(form_frame, text="💾 सेव्ह करा", bg='#0fcea7', fg='white',
                           font=('Arial', 12), command=save_business_info)
        save_btn.grid(row=3, column=0, columnspan=2, pady=20)
    def setup_print_settings_tab(self, parent):
        main_frame = tk.Frame(parent, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        tk.Label(main_frame, text="🖨️ बिल प्रिंटिंग सेटिंग", 
                font=('Arial', 16, 'bold'), bg='white').pack(pady=(0, 20))
        form_frame = tk.LabelFrame(main_frame, text="सेटिंग", bg='white', font=('Arial', 10, 'bold'))
        form_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        tk.Label(form_frame, text="हेडर टेक्स्ट:", bg='white', font=('Arial', 10)).grid(row=0, column=0, padx=10, pady=10, sticky='w')
        self.header_entry = tk.Entry(form_frame, width=40, font=('Arial', 10))
        self.header_entry.grid(row=0, column=1, padx=10, pady=10, sticky='w')
        self.header_entry.bind('<Return>', lambda e: self.footer_entry.focus())
        tk.Label(form_frame, text="फूटर टेक्स्ट:", bg='white', font=('Arial', 10)).grid(row=1, column=0, padx=10, pady=10, sticky='w')
        self.footer_entry = tk.Entry(form_frame, width=40, font=('Arial', 10))
        self.footer_entry.grid(row=1, column=1, padx=10, pady=10, sticky='w')
        self.footer_entry.bind('<Return>', lambda e: self.font_size_entry.focus())
        tk.Label(form_frame, text="फॉन्ट साइझ:", bg='white', font=('Arial', 10)).grid(row=2, column=0, padx=10, pady=10, sticky='w')
        self.font_size_entry = tk.Entry(form_frame, width=10, font=('Arial', 10))
        self.font_size_entry.grid(row=2, column=1, padx=10, pady=10, sticky='w')
        self.font_size_entry.insert(0, "10")
        self.font_size_entry.bind('<Return>', lambda e: self.save_print_settings())
        self.load_print_settings()
        def save_print_settings():
            try:
                header_text = self.header_entry.get().strip()
                footer_text = self.footer_entry.get().strip()
                font_size = int(self.font_size_entry.get())
                if font_size < 6 or font_size > 20:
                    self.show_messagebox("त्रुटी", "फॉन्ट साइझ ६ ते २० दरम्यान असावा")
                    return
                self.db.cursor.execute("SELECT COUNT(*) FROM print_settings")
                count = self.db.cursor.fetchone()[0]
                if count == 0:
                    self.db.cursor.execute('''
                        INSERT INTO print_settings (header_text, footer_text, font_size)
                        VALUES (?, ?, ?)
                    ''', (header_text, footer_text, font_size))
                else:
                    self.db.cursor.execute('''
                        UPDATE print_settings SET header_text = ?, footer_text = ?, font_size = ?
                    ''', (header_text, footer_text, font_size))
                self.db.conn.commit()
                self.show_messagebox("यशस्वी", "प्रिंट सेटिंग्स सेव्ह झाल्या")
            except ValueError:
                self.show_messagebox("त्रुटी", "कृपया वैध फॉन्ट साइझ प्रविष्ट करा")
            except Exception as e:
                self.show_messagebox("त्रुटी", f"सेटिंग्स सेव्ह त्रुटी: {str(e)}")
        save_btn = tk.Button(form_frame, text="💾 सेव्ह करा", bg='#0fcea7', fg='white',
                           font=('Arial', 12), command=save_print_settings)
        save_btn.grid(row=3, column=0, columnspan=2, pady=20)
    def load_print_settings(self):
        try:
            self.db.cursor.execute("SELECT header_text, footer_text, font_size FROM print_settings LIMIT 1")
            result = self.db.cursor.fetchone()
            if result:
                header_text, footer_text, font_size = result
                self.header_entry.delete(0, tk.END)
                self.header_entry.insert(0, header_text if header_text else "")
                self.footer_entry.delete(0, tk.END)
                self.footer_entry.insert(0, footer_text if footer_text else "")
                self.font_size_entry.delete(0, tk.END)
                self.font_size_entry.insert(0, str(font_size))
        except:
            pass
    def setup_backup_tab(self, parent):
        main_frame = tk.Frame(parent, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        tk.Label(main_frame, text="💾 बॅकअप सेटिंग", 
                font=('Arial', 16, 'bold'), bg='white').pack(pady=(0, 20))
        form_frame = tk.LabelFrame(main_frame, text="ऑटो बॅकअप सेटिंग", bg='white', font=('Arial', 10, 'bold'))
        form_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        self.auto_backup_var = tk.IntVar(value=0)
        auto_backup_check = tk.Checkbutton(form_frame, text="ऑटो बॅकअप सक्षम करा", 
                                          variable=self.auto_backup_var, bg='white', font=('Arial', 10))
        auto_backup_check.grid(row=0, column=0, padx=10, pady=10, sticky='w', columnspan=2)
        tk.Label(form_frame, text="बॅकअप पाथ:", bg='white', font=('Arial', 10)).grid(row=1, column=0, padx=10, pady=10, sticky='w')
        self.backup_path_entry = tk.Entry(form_frame, width=30, font=('Arial', 10))
        self.backup_path_entry.grid(row=1, column=1, padx=10, pady=10, sticky='w')
        browse_btn = tk.Button(form_frame, text="🔍 ब्राउझ करा", bg='#3a86ff', fg='white',
                              font=('Arial', 9), command=self.browse_backup_path)
        browse_btn.grid(row=1, column=2, padx=10, pady=10)
        tk.Label(form_frame, text="बॅकअप अंतर (तास):", bg='white', font=('Arial', 10)).grid(row=2, column=0, padx=10, pady=10, sticky='w')
        self.backup_interval_entry = tk.Entry(form_frame, width=10, font=('Arial', 10))
        self.backup_interval_entry.grid(row=2, column=1, padx=10, pady=10, sticky='w')
        self.backup_interval_entry.insert(0, "24")
        tk.Label(form_frame, text="फाइल्स ठेवा (दिवस):", bg='white', font=('Arial', 10)).grid(row=3, column=0, padx=10, pady=10, sticky='w')
        self.keep_days_entry = tk.Entry(form_frame, width=10, font=('Arial', 10))
        self.keep_days_entry.grid(row=3, column=1, padx=10, pady=10, sticky='w')
        self.keep_days_entry.insert(0, "30")
        self.load_backup_settings()
        def save_backup_settings():
            try:
                auto_backup = self.auto_backup_var.get()
                backup_path = self.backup_path_entry.get().strip()
                backup_interval = int(self.backup_interval_entry.get())
                keep_days = int(self.keep_days_entry.get())
                if backup_path and not os.path.exists(backup_path):
                    os.makedirs(backup_path)
                if backup_interval < 1:
                    self.show_messagebox("त्रुटी", "बॅकअप अंतर १ तासापेक्षा कमी असू शकत नाही")
                    return
                if keep_days < 1:
                    self.show_messagebox("त्रुटी", "फाइल्स ठेवण्याचा कालावधी १ दिवसापेक्षा कमी असू शकत नाही")
                    return
                self.db.cursor.execute("SELECT COUNT(*) FROM backup_settings")
                count = self.db.cursor.fetchone()[0]
                if count == 0:
                    self.db.cursor.execute('''
                        INSERT INTO backup_settings (auto_backup, backup_path, backup_interval_hours, keep_days)
                        VALUES (?, ?, ?, ?)
                    ''', (auto_backup, backup_path, backup_interval, keep_days))
                else:
                    self.db.cursor.execute('''
                        UPDATE backup_settings SET auto_backup = ?, backup_path = ?, 
                        backup_interval_hours = ?, keep_days = ?
                    ''', (auto_backup, backup_path, backup_interval, keep_days))
                self.db.conn.commit()
                self.show_messagebox("यशस्वी", "बॅकअप सेटिंग्स सेव्ह झाल्या")
            except ValueError:
                self.show_messagebox("त्रुटी", "कृपया वैध संख्या प्रविष्ट करा")
            except Exception as e:
                self.show_messagebox("त्रुटी", f"सेटिंग्स सेव्ह त्रुटी: {str(e)}")
        save_btn = tk.Button(form_frame, text="💾 सेव्ह करा", bg='#0fcea7', fg='white',
                           font=('Arial', 12), command=save_backup_settings)
        save_btn.grid(row=4, column=0, columnspan=3, pady=20)
        manual_frame = tk.LabelFrame(main_frame, text="मॅन्युअल बॅकअप", bg='white', font=('Arial', 10, 'bold'))
        manual_frame.pack(fill=tk.X, pady=(0, 20))
        backup_btn = tk.Button(manual_frame, text="💾 आजचा बॅकअप करा", bg='#3a86ff', fg='white',
                              font=('Arial', 12), width=20, command=self.create_backup)
        backup_btn.pack(side=tk.LEFT, padx=10, pady=10)
        restore_btn = tk.Button(manual_frame, text="🔄 बॅकअप रिस्टोर करा", bg='#f0a500', fg='white',
                               font=('Arial', 12), width=20, command=self.restore_backup_with_password)
        restore_btn.pack(side=tk.LEFT, padx=10, pady=10)
    def load_backup_settings(self):
        try:
            self.db.cursor.execute("SELECT auto_backup, backup_path, backup_interval_hours, keep_days FROM backup_settings LIMIT 1")
            result = self.db.cursor.fetchone()
            if result:
                auto_backup, backup_path, backup_interval, keep_days = result
                self.auto_backup_var.set(auto_backup)
                self.backup_path_entry.delete(0, tk.END)
                self.backup_path_entry.insert(0, backup_path if backup_path else "")
                self.backup_interval_entry.delete(0, tk.END)
                self.backup_interval_entry.insert(0, str(backup_interval))
                self.keep_days_entry.delete(0, tk.END)
                self.keep_days_entry.insert(0, str(keep_days))
        except:
            pass
    def browse_backup_path(self):
        path = filedialog.askdirectory(title="बॅकअप पाथ निवडा")
        if path:
            self.backup_path_entry.delete(0, tk.END)
            self.backup_path_entry.insert(0, path)
    def create_backup(self):
        backup_path = self.backup_path_entry.get().strip()
        if not backup_path:
            self.show_messagebox("त्रुटी", "कृपया बॅकअप पाथ निवडा")
            return
        try:
            if not os.path.exists(backup_path):
                os.makedirs(backup_path)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(backup_path, f"shop_backup_{timestamp}.db")
            shutil.copy2('shop_management.db', backup_file)
            self.db.cursor.execute('''
                UPDATE backup_settings SET last_backup = ?
            ''', (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),))
            self.db.conn.commit()
            self.show_messagebox("यशस्वी", f"बॅकअप यशस्वी!\nफाइल: {backup_file}")
        except Exception as e:
            self.show_messagebox("त्रुटी", f"बॅकअप त्रुटी: {str(e)}")
    def restore_backup_with_password(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("बॅकअप रिस्टोर - पासवर्ड")
        dialog.geometry("400x200")
        dialog.configure(bg='white')
        dialog.transient(self.root)
        dialog.grab_set()
        self.center_dialog(dialog)
        tk.Label(dialog, text="पासवर्ड प्रविष्ट करा", font=('Arial', 14, 'bold'), bg='white').pack(pady=10)
        password_entry = tk.Entry(dialog, show="*", font=('Arial', 12), width=20)
        password_entry.pack(pady=10)
        password_entry.focus()
        def verify_password():
            password = password_entry.get().strip()
            if password == "admin":
                dialog.destroy()
                self.restore_backup()
            else:
                self.show_messagebox("त्रुटी", "चुकीचा पासवर्ड")
                dialog.destroy()
        verify_btn = tk.Button(dialog, text="पुष्टी करा", bg='#0fcea7', fg='white',
                              font=('Arial', 12), command=verify_password)
        verify_btn.pack(pady=10)
        dialog.bind('<Return>', lambda e: verify_password())
    def restore_backup(self):
        backup_file = filedialog.askopenfilename(
            title="बॅकअप फाइल निवडा",
            filetypes=[("Database files", "*.db"), ("All files", "*.*")]
        )
        if not backup_file:
            return
        try:
            if os.path.exists('shop_management.db'):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                old_backup = f"shop_management_old_{timestamp}.db"
                shutil.copy2('shop_management.db', old_backup)
            shutil.copy2(backup_file, 'shop_management.db')
            self.show_messagebox("यशस्वी", "बॅकअप रिस्टोर यशस्वी!\nकृपया प्रोग्राम रीस्टार्ट करा.")
            self.root.quit()
        except Exception as e:
            self.show_messagebox("त्रुटी", f"रिस्टोर त्रुटी: {str(e)}")
    def setup_user_settings_tab(self, parent):
        main_frame = tk.Frame(parent, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        tk.Label(main_frame, text="👤 वापरकर्ते सेटिंग", 
                font=('Arial', 16, 'bold'), bg='white').pack(pady=(0, 20))
        if self.user_type != 'admin':
            tk.Label(main_frame, text="तुमच्याकडे या सेटिंगसाठी परवानगी नाही", 
                    font=('Arial', 12), bg='white', fg='#e94560').pack(pady=50)
            return
        form_frame = tk.LabelFrame(main_frame, text="नवीन वापरकर्ता जोडा", bg='white', font=('Arial', 10, 'bold'))
        form_frame.pack(fill=tk.X, pady=(0, 20))
        tk.Label(form_frame, text="वापरकर्ता नाव:", bg='white', font=('Arial', 10)).grid(row=0, column=0, padx=10, pady=10, sticky='w')
        new_username_entry = tk.Entry(form_frame, width=20, font=('Arial', 10))
        new_username_entry.grid(row=0, column=1, padx=10, pady=10, sticky='w')
        new_username_entry.bind('<Return>', lambda e: new_password_entry.focus())
        tk.Label(form_frame, text="पासवर्ड:", bg='white', font=('Arial', 10)).grid(row=1, column=0, padx=10, pady=10, sticky='w')
        new_password_entry = tk.Entry(form_frame, width=20, font=('Arial', 10), show="*")
        new_password_entry.grid(row=1, column=1, padx=10, pady=10, sticky='w')
        new_password_entry.bind('<Return>', lambda e: new_fullname_entry.focus())
        tk.Label(form_frame, text="पूर्ण नाव:", bg='white', font=('Arial', 10)).grid(row=2, column=0, padx=10, pady=10, sticky='w')
        new_fullname_entry = tk.Entry(form_frame, width=20, font=('Arial', 10))
        new_fullname_entry.grid(row=2, column=1, padx=10, pady=10, sticky='w')
        new_fullname_entry.bind('<Return>', lambda e: user_type_combo.focus())
        tk.Label(form_frame, text="वापरकर्ता प्रकार:", bg='white', font=('Arial', 10)).grid(row=3, column=0, padx=10, pady=10, sticky='w')
        user_type_combo = ttk.Combobox(form_frame, values=['user', 'admin'], width=10, font=('Arial', 10), state='readonly')
        user_type_combo.grid(row=3, column=1, padx=10, pady=10, sticky='w')
        user_type_combo.current(0)
        user_type_combo.bind('<Return>', lambda e: add_user())
        def add_user():
            username = new_username_entry.get().strip()
            password = new_password_entry.get().strip()
            fullname = new_fullname_entry.get().strip()
            usertype = user_type_combo.get()
            if not username or not password:
                self.show_messagebox("त्रुटी", "कृपया वापरकर्ता नाव आणि पासवर्ड प्रविष्ट करा")
                return
            try:
                self.db.cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (username,))
                if self.db.cursor.fetchone()[0] > 0:
                    self.show_messagebox("त्रुटी", "हा वापरकर्ता नाव आधीच अस्तित्वात आहे")
                    return
                self.db.cursor.execute('''
                    INSERT INTO users (username, password, full_name, user_type)
                    VALUES (?, ?, ?, ?)
                ''', (username, password, fullname, usertype))
                self.db.conn.commit()
                new_username_entry.delete(0, tk.END)
                new_password_entry.delete(0, tk.END)
                new_fullname_entry.delete(0, tk.END)
                user_type_combo.current(0)
                self.show_messagebox("यशस्वी", f"वापरकर्ता '{username}' यशस्वीरित्या जोडला")
            except Exception as e:
                self.show_messagebox("त्रुटी", f"वापरकर्ता जोड त्रुटी: {str(e)}")
        add_btn = tk.Button(form_frame, text="➕ वापरकर्ता जोडा", bg='#0fcea7', fg='white',
                           font=('Arial', 12), command=add_user)
        add_btn.grid(row=4, column=0, columnspan=2, pady=20)
    def setup_status_bar(self):
        status_bar = tk.Frame(self.root, bg='#f8f9fa', height=30)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        tk.Label(status_bar, text="© 2023 माझे दुकान - सर्व हक्क राखीव", 
                bg='#f8f9fa', fg='#666', font=('Arial', 9)).pack(side=tk.RIGHT, padx=10)
        self.status_label = tk.Label(status_bar, text="तयार", bg='#f8f9fa', fg='#0fcea7', font=('Arial', 9))
        self.status_label.pack(side=tk.LEFT, padx=10)
    def update_time_display(self):
        now = datetime.now()
        date_str = now.strftime("%d/%m/%Y")
        time_str = now.strftime("%H:%M:%S")
        self.datetime_label.config(text=f"📅 {date_str} ⏰ {time_str}")
        self.root.after(1000, self.update_time_display)
    def on_closing(self):
        if messagebox.askokcancel("बाहेर पडा", "तुम्हाला प्रोग्राम बंद करायचे आहे का?"):
            self.db.conn.close()
            self.root.destroy()
    def run(self):
        self.root.mainloop()
if __name__ == "__main__":
    license_manager = LicenseManager()
    if license_manager.check_license():
        db = DatabaseManager()
        login_window = LoginWindow(db)
        login_window.run()