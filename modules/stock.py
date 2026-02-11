# modules/stock.py
import tkinter as tk
from tkinter import ttk, messagebox

class StockModule:
    def __init__(self, db, parent_app):
        self.db = db
        self.parent_app = parent_app
    
    def create_stock_tab(self):
        """Create the stock management tab content"""
        stock_frame = tk.Frame(self.parent_app.notebook, bg='white')
        
        main_container = tk.Frame(stock_frame, bg='white')
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
        
        # Stock tab
        stock_tab = tk.Frame(self.stock_notebook, bg='white')
        self.stock_notebook.add(stock_tab, text="स्टॉक")
        self.setup_stock_tab(stock_tab)
        
        # Category-Barcode tab
        category_tab = tk.Frame(self.stock_notebook, bg='white')
        self.stock_notebook.add(category_tab, text="कॅटेगरी - बारकोड")
        self.setup_category_tab(category_tab)
        
        return stock_frame
    
    def setup_stock_tab(self, parent):
        """Setup stock management tab"""
        main_frame = tk.Frame(parent, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Search frame
        search_frame = tk.Frame(main_frame, bg='white')
        search_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(search_frame, text="उत्पादन शोधा:", bg='white', 
                font=('Arial', 10)).pack(side=tk.LEFT)
        
        self.stock_search_entry = tk.Entry(search_frame, width=30, font=('Arial', 10))
        self.stock_search_entry.pack(side=tk.LEFT, padx=5)
        
        search_btn = tk.Button(search_frame, text="🔍 शोधा", bg='#3a86ff', fg='white',
                              font=('Arial', 10), command=self.search_stock)
        search_btn.pack(side=tk.LEFT, padx=5)
        
        new_product_btn = tk.Button(search_frame, text="+ नवीन उत्पादन", bg='#0fcea7', fg='white',
                                   font=('Arial', 10), command=self.add_new_product)
        new_product_btn.pack(side=tk.LEFT, padx=5)
        
        refresh_btn = tk.Button(search_frame, text="🔄 रिफ्रेश", bg='#f0a500', fg='white',
                               font=('Arial', 10), command=self.load_stock)
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        tk.Label(search_frame, text="कॅटेगिरी:", bg='white', font=('Arial', 10)).pack(
            side=tk.LEFT, padx=(20, 5))
        
        self.stock_category_combo = ttk.Combobox(search_frame, width=20, font=('Arial', 10))
        self.stock_category_combo.pack(side=tk.LEFT, padx=5)
        
        # Table frame
        table_frame = tk.Frame(main_frame, bg='white')
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ('क्रमांक', 'उत्पादन', 'बारकोड', 'कॅटेगिरी', 'खरेदी किं.', 
                  'विक्री किं.', 'स्टॉक', 'किमान', 'एकूण किंमत')
        
        self.stock_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        column_widths = [50, 150, 100, 100, 80, 80, 60, 60, 100]
        for i, (col, width) in enumerate(zip(columns, column_widths)):
            self.stock_tree.heading(col, text=col)
            if i in [0, 4, 5, 6, 7, 8]:
                self.stock_tree.column(col, width=width, anchor='e')
            else:
                self.stock_tree.column(col, width=width, anchor='w')
        
        scrollbar_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.stock_tree.yview)
        scrollbar_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.stock_tree.xview)
        self.stock_tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        self.stock_tree.grid(row=0, column=0, sticky='nsew')
        scrollbar_y.grid(row=0, column=1, sticky='ns')
        scrollbar_x.grid(row=1, column=0, sticky='ew')
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Load initial data
        self.load_c