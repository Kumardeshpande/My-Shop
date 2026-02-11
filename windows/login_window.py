# windows/login_window.py
import tkinter as tk
from tkinter import ttk
from database import DatabaseManager

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
                from windows.shop_app import ShopManagementApp
                app = ShopManagementApp(username, result[1])
                app.run()
            else:
                self.status_label.config(text="अवैध वापरकर्ता नाव किंवा पासवर्ड")
        except Exception as e:
            self.status_label.config(text=f"लॉगिन त्रुटी: {str(e)}")
    
    def run(self):
        self.login_window.mainloop()