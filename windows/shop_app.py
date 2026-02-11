# windows/shop_app.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import sys
from database import DatabaseManager

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
    
    def update_time_display(self):
        current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        if hasattr(self, 'datetime_label'):
            self.datetime_label.config(text=current_time)
        self.root.after(1000, self.update_time_display)
    
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
        # Tab change logic will be implemented in modules
    
    def create_tabs(self):
        from modules.sales import SalesModule
        from modules.purchases import PurchasesModule
        from modules.stock import StockModule
        from modules.accounts import AccountsModule
        from modules.reports import ReportsModule
        from modules.settings import SettingsModule
        
        # Dashboard tab
        dashboard_frame = tk.Frame(self.notebook, bg='#f8f9fa')
        self.notebook.add(dashboard_frame, text="  डॅशबोर्ड  ")
        self.setup_dashboard_content(dashboard_frame)
        
        # Sales tab
        sales_module = SalesModule(self.db, self)
        sales_frame = sales_module.create_sales_tab()
        self.notebook.add(sales_frame, text="  नवीन विक्री  ")
        
        # Purchases tab
        purchases_module = PurchasesModule(self.db, self)
        purchase_frame = purchases_module.create_purchases_tab()
        self.notebook.add(purchase_frame, text="  नवीन खरेदी  ")
        
        # Stock tab
        stock_module = StockModule(self.db, self)
        stock_frame = stock_module.create_stock_tab()
        self.notebook.add(stock_frame, text="  स्टॉक व्यवस्थापन  ")
        
        # Accounts tab
        accounts_module = AccountsModule(self.db, self)
        accounts_frame = accounts_module.create_accounts_tab()
        self.notebook.add(accounts_frame, text="  खाते व्यवस्थापन  ")
        
        # Reports tab
        reports_module = ReportsModule(self.db, self)
        reports_frame = reports_module.create_reports_tab()
        self.notebook.add(reports_frame, text="  अहवाल  ")
        
        # Settings tab
        settings_module = SettingsModule(self.db, self)
        settings_frame = settings_module.create_settings_tab()
        self.notebook.add(settings_frame, text="  सेटिंग  ")
    
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
        
        # Dashboard statistics will be implemented
        
        bottom_container = tk.Frame(main_container, bg='#f8f9fa')
        bottom_container.grid(row=2, column=0, sticky='nsew')
        
        # Dashboard panels will be implemented
    
    def setup_status_bar(self):
        status_bar = tk.Frame(self.root, bg='#1a1a2e', height=25)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = tk.Label(status_bar, text="तयार", 
                                    bg='#1a1a2e', fg='white',
                                    font=('Arial', 10))
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        version_label = tk.Label(status_bar, text="आवृत्ती 1.1.0", 
                                bg='#1a1a2e', fg='#f0a500',
                                font=('Arial', 10))
        version_label.pack(side=tk.RIGHT, padx=10)
    
    def run(self):
        self.root.mainloop()
    
    def on_closing(self):
        if messagebox.askokcancel("बाहेर पडा", "तुम्हाला खरोखर बाहेर पडायचे आहे?"):
            self.db.conn.close()
            self.root.destroy()
    
    def refresh_all_tabs(self):
        """Refresh all tabs when transaction completes"""
        if self.current_tab == 0:  # Dashboard tab
            self.update_dashboard_stats()
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
    
    def update_dashboard_stats(self):
        """Update dashboard statistics"""
        pass
    
    def refresh_sales_tab(self):
        """Refresh sales tab data"""
        pass
    
    def refresh_purchases_tab(self):
        """Refresh purchases tab data"""
        pass
    
    def refresh_stock_tab(self):
        """Refresh stock tab data"""
        pass
    
    def refresh_accounts_tab(self):
        """Refresh accounts tab data"""
        pass
    
    def refresh_reports_tab(self):
        """Refresh reports tab data"""
        pass
    
    def refresh_settings_tab(self):
        """Refresh settings tab data"""
        pass
    
    def show_messagebox(self, title, message):
        """Show message box"""
        messagebox.showinfo(title, message)