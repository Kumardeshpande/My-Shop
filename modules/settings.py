# modules/settings.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import shutil
from datetime import datetime

class SettingsModule:
    def __init__(self, db, parent_app):
        self.db = db
        self.parent_app = parent_app
    
    def create_settings_tab(self):
        """Create the settings tab content"""
        settings_frame = tk.Frame(self.parent_app.notebook, bg='white')
        
        main_container = tk.Frame(settings_frame, bg='white')
        main_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        header_frame = tk.Frame(main_container, bg='white')
        header_frame.pack(fill=tk.X, pady=(0, 15), padx=10)
        tk.Label(header_frame, text="⚙️ सेटिंग", 
                font=('Arial', 20, 'bold'), bg='white').pack(side=tk.LEFT)
        
        self.settings_notebook = ttk.Notebook(main_container)
        self.settings_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Shop info tab
        shop_info_tab = tk.Frame(self.settings_notebook, bg='white')
        self.settings_notebook.add(shop_info_tab, text="दुकान माहिती")
        self.setup_shop_info_tab(shop_info_tab)
        
        # Print settings tab
        print_settings_tab = tk.Frame(self.settings_notebook, bg='white')
        self.settings_notebook.add(print_settings_tab, text="प्रिंट सेटिंग")
        self.setup_print_settings_tab(print_settings_tab)
        
        # Backup settings tab
        backup_settings_tab = tk.Frame(self.settings_notebook, bg='white')
        self.settings_notebook.add(backup_settings_tab, text="बॅकअप सेटिंग")
        self.setup_backup_settings_tab(backup_settings_tab)
        
        # User management tab
        user_management_tab = tk.Frame(self.settings_notebook, bg='white')
        self.settings_notebook.add(user_management_tab, text="वापरकर्ता व्यवस्थापन")
        self.setup_user_management_tab(user_management_tab)
        
        return settings_frame
    
    def setup_shop_info_tab(self, parent):
        """Setup shop information tab"""
        main_frame = tk.Frame(parent, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        form_frame = tk.LabelFrame(main_frame, text="दुकान माहिती", 
                                  bg='white', font=('Arial', 10, 'bold'))
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Shop name
        tk.Label(form_frame, text="दुकानाचे नाव:", bg='white', 
                font=('Arial', 10)).grid(row=0, column=0, padx=10, pady=10, sticky='w')
        
        self.shop_name_entry = tk.Entry(form_frame, width=40, font=('Arial', 10))
        self.shop_name_entry.grid(row=0, column=1, padx=10, pady=10, sticky='w')
        
        # Owner name
        tk.Label(form_frame, text="मालकाचे नाव:", bg='white', 
                font=('Arial', 10)).grid(row=1, column=0, padx=10, pady=10, sticky='w')
        
        self.owner_name_entry = tk.Entry(form_frame, width=40, font=('Arial', 10))
        self.owner_name_entry.grid(row=1, column=1, padx=10, pady=10, sticky='w')
        
        # Address
        tk.Label(form_frame, text="पत्ता:", bg='white', 
                font=('Arial', 10)).grid(row=2, column=0, padx=10, pady=10, sticky='w')
        
        self.address_entry = tk.Entry(form_frame, width=40, font=('Arial', 10))
        self.address_entry.grid(row=2, column=1, padx=10, pady=10, sticky='w')
        
        # Phone
        tk.Label(form_frame, text="फोन नंबर:", bg='white', 
                font=('Arial', 10)).grid(row=3, column=0, padx=10, pady=10, sticky='w')
        
        self.phone_entry = tk.Entry(form_frame, width=40, font=('Arial', 10))
        self.phone_entry.grid(row=3, column=1, padx=10, pady=10, sticky='w')
        
        # Email
        tk.Label(form_frame, text="ईमेल:", bg='white', 
                font=('Arial', 10)).grid(row=4, column=0, padx=10, pady=10, sticky='w')
        
        self.email_entry = tk.Entry(form_frame, width=40, font=('Arial', 10))
        self.email_entry.grid(row=4, column=1, padx=10, pady=10, sticky='w')
        
        # GST Number
        tk.Label(form_frame, text="GST नंबर:", bg='white', 
                font=('Arial', 10)).grid(row=5, column=0, padx=10, pady=10, sticky='w')
        
        self.gst_entry = tk.Entry(form_frame, width=40, font=('Arial', 10))
        self.gst_entry.grid(row=5, column=1, padx=10, pady=10, sticky='w')
        
        # Save button
        save_btn = tk.Button(form_frame, text="💾 माहिती सेव्ह करा", bg='#0fcea7', fg='white',
                           font=('Arial', 12, 'bold'), command=self.save_shop_info)
        save_btn.grid(row=6, column=0, columnspan=2, pady=20)
        
        # Load existing shop info
        self.load_shop_info()
    
    def setup_print_settings_tab(self, parent):
        """Setup print settings tab"""
        main_frame = tk.Frame(parent, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        form_frame = tk.LabelFrame(main_frame, text="प्रिंट सेटिंग", 
                                  bg='white', font=('Arial', 10, 'bold'))
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header text
        tk.Label(form_frame, text="बिल हेडर मजकूर:", bg='white', 
                font=('Arial', 10)).grid(row=0, column=0, padx=10, pady=10, sticky='w')
        
        self.header_text_entry = tk.Entry(form_frame, width=40, font=('Arial', 10))
        self.header_text_entry.grid(row=0, column=1, padx=10, pady=10, sticky='w')
        
        # Footer text
        tk.Label(form_frame, text="बिल फुटर मजकूर:", bg='white', 
                font=('Arial', 10)).grid(row=1, column=0, padx=10, pady=10, sticky='w')
        
        self.footer_text_entry = tk.Entry(form_frame, width=40, font=('Arial', 10))
        self.footer_text_entry.grid(row=1, column=1, padx=10, pady=10, sticky='w')
        
        # Font size
        tk.Label(form_frame, text="फॉन्ट साईझ:", bg='white', 
                font=('Arial', 10)).grid(row=2, column=0, padx=10, pady=10, sticky='w')
        
        self.font_size_combo = ttk.Combobox(form_frame, values=['8', '9', '10', '11', '12'], 
                                           width=10, font=('Arial', 10), state='readonly')
        self.font_size_combo.grid(row=2, column=1, padx=10, pady=10, sticky='w')
        self.font_size_combo.set('10')
        
        # Save button
        save_btn = tk.Button(form_frame, text="💾 सेटिंग सेव्ह करा", bg='#0fcea7', fg='white',
                           font=('Arial', 12, 'bold'), command=self.save_print_settings)
        save_btn.grid(row=3, column=0, columnspan=2, pady=20)
        
        # Load existing print settings
        self.load_print_settings()
    
    def setup_backup_settings_tab(self, parent):
        """Setup backup settings tab"""
        main_frame = tk.Frame(parent, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        form_frame = tk.LabelFrame(main_frame, text="बॅकअप सेटिंग", 
                                  bg='white', font=('Arial', 10, 'bold'))
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Auto backup
        self.auto_backup_var = tk.BooleanVar()
        auto_backup_check = tk.Checkbutton(form_frame, text="ऑटो बॅकअप सुरू करा", 
                                          variable=self.auto_backup_var,
                                          bg='white', font=('Arial', 10))
        auto_backup_check.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky='w')
        
        # Backup path
        tk.Label(form_frame, text="बॅकअप पाथ:", bg='white', 
                font=('Arial', 10)).grid(row=1, column=0, padx=10, pady=10, sticky='w')
        
        self.backup_path_entry = tk.Entry(form_frame, width=30, font=('Arial', 10))
        self.backup_path_entry.grid(row=1, column=1, padx=10, pady=10, sticky='w')
        
        browse_btn = tk.Button(form_frame, text="🔍 ब्राउझ करा", bg='#3a86ff', fg='white',
                              font=('Arial', 10), command=self.browse_backup_path)
        browse_btn.grid(row=1, column=2, padx=10, pady=10)
        
        # Backup interval
        tk.Label(form_frame, text="बॅकअप अंतर (तास):", bg='white', 
                font=('Arial', 10)).grid(row=2, column=0, padx=10, pady=10, sticky='w')
        
        self.backup_interval_combo = ttk.Combobox(form_frame, 
                                                 values=['1', '2', '4', '6', '12', '24'], 
                                                 width=10, font=('Arial', 10), state='readonly')
        self.backup_interval_combo.grid(row=2, column=1, padx=10, pady=10, sticky='w')
        self.backup_interval_combo.set('24')
        
        # Keep days
        tk.Label(form_frame, text="बॅकअप ठेवा (दिवस):", bg='white', 
                font=('Arial', 10)).grid(row=3, column=0, padx=10, pady=10, sticky='w')
        
        self.keep_days_combo = ttk.Combobox(form_frame, 
                                           values=['7', '15', '30', '60', '90', '180', '365'], 
                                           width=10, font=('Arial', 10), state='readonly')
        self.keep_days_combo.grid(row=3, column=1, padx=10, pady=10, sticky='w')
        self.keep_days_combo.set('30')
        
        # Buttons frame
        button_frame = tk.Frame(form_frame, bg='white')
        button_frame.grid(row=4, column=0, columnspan=3, pady=20)
        
        save_btn = tk.Button(button_frame, text="💾 सेटिंग सेव्ह करा", bg='#0fcea7', fg='white',
                           font=('Arial', 12), command=self.save_backup_settings)
        save_btn.pack(side=tk.LEFT, padx=10)
        
        backup_now_btn = tk.Button(button_frame, text="📁 आत्ता बॅकअप घ्या", bg='#3a86ff', fg='white',
                                  font=('Arial', 12), command=self.create_backup_now)
        backup_now_btn.pack(side=tk.LEFT, padx=10)
        
        # Load existing backup settings
        self.load_backup_settings()
    
    def setup_user_management_tab(self, parent):
        """Setup user management tab"""
        main_frame = tk.Frame(parent, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left frame - User list
        left_frame = tk.Frame(main_frame, bg='white')
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        list_frame = tk.LabelFrame(left_frame, text="वापरकर्ता यादी", 
                                  bg='white', font=('Arial', 10, 'bold'))
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ('वापरकर्ता नाव', 'पूर्ण नाव', 'प्रकार')
        self.users_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.users_tree.heading(col, text=col)
            self.users_tree.column(col, width=150, anchor='center')
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=scrollbar.set)
        
        self.users_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Right frame - Add/Edit user
        right_frame = tk.Frame(main_frame, bg='white')
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        form_frame = tk.LabelFrame(right_frame, text="वापरकर्ता जोडा/संपादित करा", 
                                  bg='white', font=('Arial', 10, 'bold'))
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(form_frame, text="वापरकर्ता नाव:", bg='white', 
                font=('Arial', 10)).grid(row=0, column=0, padx=10, pady=10, sticky='w')
        
        self.username_entry = tk.Entry(form_frame, width=30, font=('Arial', 10))
        self.username_entry.grid(row=0, column=1, padx=10, pady=10, sticky='w')
        
        tk.Label(form_frame, text="पासवर्ड:", bg='white', 
                font=('Arial', 10)).grid(row=1, column=0, padx=10, pady=10, sticky='w')
        
        self.password_entry = tk.Entry(form_frame, width=30, font=('Arial', 10), show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=10, sticky='w')
        
        tk.Label(form_frame, text="पूर्ण नाव:", bg='white', 
                font=('Arial', 10)).grid(row=2, column=0, padx=10, pady=10, sticky='w')
        
        self.fullname_entry = tk.Entry(form_frame, width=30, font=('Arial', 10))
        self.fullname_entry.grid(row=2, column=1, padx=10, pady=10, sticky='w')
        
        tk.Label(form_frame, text="वापरकर्ता प्रकार:", bg='white', 
                font=('Arial', 10)).grid(row=3, column=0, padx=10, pady=10, sticky='w')
        
        self.user_type_combo = ttk.Combobox(form_frame, values=['admin', 'user'], 
                                           width=15, font=('Arial', 10), state='readonly')
        self.user_type_combo.grid(row=3, column=1, padx=10, pady=10, sticky='w')
        self.user_type_combo.set('user')
        
        # Buttons frame
        button_frame = tk.Frame(form_frame, bg='white')
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        add_btn = tk.Button(button_frame, text="➕ नवीन वापरकर्ता", bg='#0fcea7', fg='white',
                          font=('Arial', 12), command=self.add_user)
        add_btn.pack(side=tk.LEFT, padx=5)
        
        update_btn = tk.Button(button_frame, text="✏️ अपडेट करा", bg='#3a86ff', fg='white',
                             font=('Arial', 12), command=self.update_user)
        update_btn.pack(side=tk.LEFT, padx=5)
        
        delete_btn = tk.Button(button_frame, text="🗑️ डिलीट करा", bg='#e94560', fg='white',
                             font=('Arial', 12), command=self.delete_user)
        delete_btn.pack(side=tk.LEFT, padx=5)
        
        # Load users
        self.load_users()
    
    def load_shop_info(self):
        """Load shop information"""
        try:
            self.db.cursor.execute("SELECT shop_name, owner_name, address, phone, email, gst_no FROM shop_info LIMIT 1")
            result = self.db.cursor.fetchone()
            
            if result:
                shop_name, owner_name, address, phone, email, gst_no = result
                self.shop_name_entry.delete(0, tk.END)
                self.shop_name_entry.insert(0, shop_name if shop_name else "")
                
                self.owner_name_entry.delete(0, tk.END)
                self.owner_name_entry.insert(0, owner_name if owner_name else "")
                
                self.address_entry.delete(0, tk.END)
                self.address_entry.insert(0, address if address else "")
                
                self.phone_entry.delete(0, tk.END)
                self.phone_entry.insert(0, phone if phone else "")
                
                self.email_entry.delete(0, tk.END)
                self.email_entry.insert(0, email if email else "")
                
                self.gst_entry.delete(0, tk.END)
                self.gst_entry.insert(0, gst_no if gst_no else "")
        except:
            pass
    
    def save_shop_info(self):
        """Save shop information"""
        try:
            # Check if record exists
            self.db.cursor.execute("SELECT COUNT(*) FROM shop_info")
            count = self.db.cursor.fetchone()[0]
            
            if count > 0:
                # Update existing record
                self.db.cursor.execute('''
                    UPDATE shop_info SET 
                    shop_name = ?, owner_name = ?, address = ?, phone = ?, email = ?, gst_no = ?
                ''', (
                    self.shop_name_entry.get(),
                    self.owner_name_entry.get(),
                    self.address_entry.get(),
                    self.phone_entry.get(),
                    self.email_entry.get(),
                    self.gst_entry.get()
                ))
            else:
                # Insert new record
                self.db.cursor.execute('''
                    INSERT INTO shop_info (shop_name, owner_name, address, phone, email, gst_no)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    self.shop_name_entry.get(),
                    self.owner_name_entry.get(),
                    self.address_entry.get(),
                    self.phone_entry.get(),
                    self.email_entry.get(),
                    self.gst_entry.get()
                ))
            
            self.db.conn.commit()
            messagebox.showinfo("यशस्वी", "दुकान माहिती यशस्वीरित्या सेव्ह केली!")
            
            # Update app title
            self.parent_app.shop_name = self.shop_name_entry.get()
            self.parent_app.root.title(f"{self.parent_app.shop_name} आवृत्ती १.१.०")
            
        except Exception as e:
            messagebox.showerror("त्रुटी", f"माहिती सेव्ह करताना त्रुटी: {str(e)}")
    
    def load_print_settings(self):
        """Load print settings"""
        try:
            self.db.cursor.execute("SELECT header_text, footer_text, font_size FROM print_settings LIMIT 1")
            result = self.db.cursor.fetchone()
            
            if result:
                header_text, footer_text, font_size = result
                self.header_text_entry.delete(0, tk.END)
                self.header_text_entry.insert(0, header_text if header_text else "")
                
                self.footer_text_entry.delete(0, tk.END)
                self.footer_text_entry.insert(0, footer_text if footer_text else "")
                
                self.font_size_combo.set(str(font_size) if font_size else "10")
        except:
            pass
    
    def save_print_settings(self):
        """Save print settings"""
        try:
            # Check if record exists
            self.db.cursor.execute("SELECT COUNT(*) FROM print_settings")
            count = self.db.cursor.fetchone()[0]
            
            if count > 0:
                # Update existing record
                self.db.cursor.execute('''
                    UPDATE print_settings SET 
                    header_text = ?, footer_text = ?, font_size = ?
                ''', (
                    self.header_text_entry.get(),
                    self.footer_text_entry.get(),
                    int(self.font_size_combo.get())
                ))
            else:
                # Insert new record
                self.db.cursor.execute('''
                    INSERT INTO print_settings (header_text, footer_text, font_size)
                    VALUES (?, ?, ?)
                ''', (
                    self.header_text_entry.get(),
                    self.footer_text_entry.get(),
                    int(self.font_size_combo.get())
                ))
            
            self.db.conn.commit()
            messagebox.showinfo("यशस्वी", "प्रिंट सेटिंग यशस्वीरित्या सेव्ह केली!")
            
        except Exception as e:
            messagebox.showerror("त्रुटी", f"सेटिंग सेव्ह करताना त्रुटी: {str(e)}")
    
    def load_backup_settings(self):
        """Load backup settings"""
        try:
            self.db.cursor.execute("SELECT auto_backup, backup_path, backup_interval_hours, keep_days FROM backup_settings LIMIT 1")
            result = self.db.cursor.fetchone()
            
            if result:
                auto_backup, backup_path, backup_interval, keep_days = result
                self.auto_backup_var.set(bool(auto_backup))
                
                self.backup_path_entry.delete(0, tk.END)
                self.backup_path_entry.insert(0, backup_path if backup_path else "")
                
                self.backup_interval_combo.set(str(backup_interval) if backup_interval else "24")
                self.keep_days_combo.set(str(keep_days) if keep_days else "30")
        except:
            pass
    
    def save_backup_settings(self):
        """Save backup settings"""
        try:
            # Check if record exists
            self.db.cursor.execute("SELECT COUNT(*) FROM backup_settings")
            count = self.db.cursor.fetchone()[0]
            
            if count > 0:
                # Update existing record
                self.db.cursor.execute('''
                    UPDATE backup_settings SET 
                    auto_backup = ?, backup_path = ?, backup_interval_hours = ?, keep_days = ?
                ''', (
                    1 if self.auto_backup_var.get() else 0,
                    self.backup_path_entry.get(),
                    int(self.backup_interval_combo.get()),
                    int(self.keep_days_combo.get())
                ))
            else:
                # Insert new record
                self.db.cursor.execute('''
                    INSERT INTO backup_settings (auto_backup, backup_path, backup_interval_hours, keep_days)
                    VALUES (?, ?, ?, ?)
                ''', (
                    1 if self.auto_backup_var.get() else 0,
                    self.backup_path_entry.get(),
                    int(self.backup_interval_combo.get()),
                    int(self.keep_days_combo.get())
                ))
            
            self.db.conn.commit()
            messagebox.showinfo("यशस्वी", "बॅकअप सेटिंग यशस्वीरित्या सेव्ह केली!")
            
        except Exception as e:
            messagebox.showerror("त्रुटी", f"सेटिंग सेव्ह करताना त्रुटी: {str(e)}")
    
    def browse_backup_path(self):
        """Browse for backup path"""
        path = filedialog.askdirectory(title="बॅकअप पाथ निवडा")
        if path:
            self.backup_path_entry.delete(0, tk.END)
            self.backup_path_entry.insert(0, path)
    
    def create_backup_now(self):
        """Create backup immediately"""
        backup_path = self.backup_path_entry.get()
        
        if not backup_path:
            messagebox.showerror("त्रुटी", "कृपया बॅकअप पाथ निवडा")
            return
        
        try:
            # Create backup directory if it doesn't exist
            if not os.path.exists(backup_path):
                os.makedirs(backup_path)
            
            # Create backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(backup_path, f"shop_backup_{timestamp}.db")
            
            # Copy database file
            shutil.copy2('shop_management.db', backup_file)
            
            # Update last backup time
            self.db.cursor.execute('''
                UPDATE backup_settings SET last_backup = datetime('now')
            ''')
            self.db.conn.commit()
            
            messagebox.showinfo("यशस्वी", f"बॅकअप यशस्वीरित्या तयार केला!\nफाइल: {backup_file}")
            
        except Exception as e:
            messagebox.showerror("त्रुटी", f"बॅकअप तयार करताना त्रुटी: {str(e)}")
    
    def load_users(self):
        """Load users list"""
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
        
        try:
            self.db.cursor.execute("SELECT username, full_name, user_type FROM users ORDER BY username")
            users = self.db.cursor.fetchall()
            
            for user in users:
                username, full_name, user_type = user
                self.users_tree.insert('', tk.END, values=(username, full_name, user_type))
        except:
            pass
    
    def add_user(self):
        """Add new user"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        full_name = self.fullname_entry.get().strip()
        user_type = self.user_type_combo.get()
        
        if not username or not password:
            messagebox.showerror("त्रुटी", "कृपया वापरकर्ता नाव आणि पासवर्ड प्रविष्ट करा")
            return
        
        try:
            self.db.cursor.execute('''
                INSERT INTO users (username, password, full_name, user_type, created_at)
                VALUES (?, ?, ?, ?, datetime('now'))
            ''', (username, password, full_name, user_type))
            
            self.db.conn.commit()
            messagebox.showinfo("यशस्वी", "वापरकर्ता यशस्वीरित्या जोडला!")
            
            # Clear form and reload list
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
            self.fullname_entry.delete(0, tk.END)
            self.user_type_combo.set('user')
            
            self.load_users()
            
        except Exception as e:
            messagebox.showerror("त्रुटी", f"वापरकर्ता जोडताना त्रुटी: {str(e)}")
    
    def update_user(self):
        """Update selected user"""
        selected_item = self.users_tree.selection()
        if not selected_item:
            messagebox.showerror("त्रुटी", "कृपया वापरकर्ता निवडा")
            return
        
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        full_name = self.fullname_entry.get().strip()
        user_type = self.user_type_combo.get()
        
        if not username:
            messagebox.showerror("त्रुटी", "कृपया वापरकर्ता नाव प्रविष्ट करा")
            return
        
        try:
            if password:
                # Update with password
                self.db.cursor.execute('''
                    UPDATE users SET password = ?, full_name = ?, user_type = ?
                    WHERE username = ?
                ''', (password, full_name, user_type, username))
            else:
                # Update without password
                self.db.cursor.execute('''
                    UPDATE users SET full_name = ?, user_type = ?
                    WHERE username = ?
                ''', (full_name, user_type, username))
            
            self.db.conn.commit()
            messagebox.showinfo("यशस्वी", "वापरकर्ता यशस्वीरित्या अपडेट केला!")
            
            # Clear form and reload list
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
            self.fullname_entry.delete(0, tk.END)
            self.user_type_combo.set('user')
            
            self.load_users()
            
        except Exception as e:
            messagebox.showerror("त्रुटी", f"वापरकर्ता अपडेट करताना त्रुटी: {str(e)}")
    
    def delete_user(self):
        """Delete selected user"""
        selected_item = self.users_tree.selection()
        if not selected_item:
            messagebox.showerror("त्रुटी", "कृपया वापरकर्ता निवडा")
            return
        
        values = self.users_tree.item(selected_item, 'values')
        username = values[0]
        
        if username == 'admin':
            messagebox.showerror("त्रुटी", "admin वापरकर्ता डिलीट करता येणार नाही")
            return
        
        confirm = messagebox.askyesno("नक्की करा", f"तुम्हाला '{username}' वापरकर्ता डिलीट करायचा आहे का?")
        if not confirm:
            return
        
        try:
            self.db.cursor.execute("DELETE FROM users WHERE username = ?", (username,))
            self.db.conn.commit()
            messagebox.showinfo("यशस्वी", "वापरकर्ता यशस्वीरित्या डिलीट केला!")
            
            # Clear form and reload list
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
            self.fullname_entry.delete(0, tk.END)
            self.user_type_combo.set('user')
            
            self.load_users()
            
        except Exception as e:
            messagebox.showerror("त्रुटी", f"वापरकर्ता डिलीट करताना त्रुटी: {str(e)}")