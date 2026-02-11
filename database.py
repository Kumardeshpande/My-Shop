# database.py
import sqlite3
from datetime import datetime
import os
import json

class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect('shop_management.db')
        self.cursor = self.conn.cursor()
        self.create_tables()
    
    def create_tables(self):
        # Products table
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
        
        # Customers table
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
        
        # Suppliers table
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
        
        # Sales table
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
        
        # Sale items table
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
        
        # Purchases table
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
        
        # Purchase items table
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
        
        # Shop info table
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
        
        # Backup settings table
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
        
        # Users table
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
        
        # Print settings table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS print_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                header_text TEXT DEFAULT '',
                footer_text TEXT DEFAULT '',
                font_size INTEGER DEFAULT 10
            )
        ''')
        
        self.conn.commit()
        
        # Create default admin user
        self.cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
        if self.cursor.fetchone()[0] == 0:
            self.cursor.execute("INSERT INTO users (username, password, full_name, user_type) VALUES ('admin', 'admin', 'Administrator', 'admin')")
            self.conn.commit()