# modules/accounts.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from tkcalendar import DateEntry

class AccountsModule:
    def __init__(self, db, parent_app):
        self.db = db
        self.parent_app = parent_app
    
    def create_accounts_tab(self):
        """Create the accounts management tab content"""
        accounts_frame = tk.Frame(self.parent_app.notebook, bg='white')
        
        main_container = tk.Frame(accounts_frame, bg='white')
        main_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        header_frame = tk.Frame(main_container, bg='white')
        header_frame.pack(fill=tk.X, pady=(0, 15), padx=10)
        tk.Label(header_frame, text="💳 खाते व्यवस्थापन", 
                font=('Arial', 20, 'bold'), bg='white').pack(side=tk.LEFT)
        
        self.accounts_notebook = ttk.Notebook(main_container)
        self.accounts_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Transactions tab
        transactions_tab = tk.Frame(self.accounts_notebook, bg='white')
        self.accounts_notebook.add(transactions_tab, text="व्यवहार")
        self.setup_transactions_tab(transactions_tab)
        
        # Credit transactions tab
        credit_transactions_tab = tk.Frame(self.accounts_notebook, bg='white')
        self.accounts_notebook.add(credit_transactions_tab, text="उधारी व्यवहार")
        self.setup_credit_transactions_tab(credit_transactions_tab)
        
        # Manual credit tab
        manual_credit_tab = tk.Frame(self.accounts_notebook, bg='white')
        self.accounts_notebook.add(manual_credit_tab, text="मॅन्युअल उदारी")
        self.setup_manual_credit_tab(manual_credit_tab)
        
        return accounts_frame
    
    def setup_transactions_tab(self, parent):
        """Setup transactions tab"""
        main_frame = tk.Frame(parent, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Filter frame
        filter_frame = tk.LabelFrame(main_frame, text="शोध फिल्टर", 
                                    bg='white', font=('Arial', 10, 'bold'))
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(filter_frame, text="व्यवहार प्रकार:", bg='white', 
                font=('Arial', 9)).grid(row=0, column=0, padx=5, pady=5)
        
        self.transaction_type_filter = ttk.Combobox(filter_frame, 
                                                   values=['सर्व', 'विक्री', 'खरेदी'], 
                                                   width=20, font=('Arial', 9), state='readonly')
        self.transaction_type_filter.grid(row=0, column=1, padx=5, pady=5)
        self.transaction_type_filter.current(0)
        
        tk.Label(filter_frame, text="तारीख पासून:", bg='white', 
                font=('Arial', 9)).grid(row=0, column=2, padx=5, pady=5)
        
        self.from_date_filter = DateEntry(filter_frame, width=15, 
                                         font=('Arial', 9), date_pattern='dd/mm/yyyy')
        self.from_date_filter.grid(row=0, column=3, padx=5, pady=5)
        
        tk.Label(filter_frame, text="तारीख पर्यंत:", bg='white', 
                font=('Arial', 9)).grid(row=0, column=4, padx=5, pady=5)
        
        self.to_date_filter = DateEntry(filter_frame, width=15, 
                                       font=('Arial', 9), date_pattern='dd/mm/yyyy')
        self.to_date_filter.grid(row=0, column=5, padx=5, pady=5)
        
        search_btn = tk.Button(filter_frame, text="🔍 शोधा", bg='#3a86ff', fg='white',
                              font=('Arial', 9), command=self.search_transactions)
        search_btn.grid(row=0, column=6, padx=5, pady=5)
        
        # Table frame
        table_frame = tk.Frame(main_frame, bg='white')
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ('बिल क्र.', 'तारीख', 'प्रकार', 'संपर्क', 'एकूण', 
                  'सवलत', 'जमा', 'उर्वरित', 'पेमेंट मोड', 'स्थिती')
        
        self.transactions_tree = ttk.Treeview(table_frame, columns=columns, 
                                             show='headings', height=15)
        
        column_widths = [100, 120, 80, 150, 80, 70, 80, 80, 100, 80]
        for i, (col, width) in enumerate(zip(columns, column_widths)):
            self.transactions_tree.heading(col, text=col)
            self.transactions_tree.column(col, width=width, anchor='center')
        
        scrollbar_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, 
                                   command=self.transactions_tree.yview)
        scrollbar_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, 
                                   command=self.transactions_tree.xview)
        
        self.transactions_tree.configure(yscrollcommand=scrollbar_y.set, 
                                        xscrollcommand=scrollbar_x.set)
        
        self.transactions_tree.grid(row=0, column=0, sticky='nsew')
        scrollbar_y.grid(row=0, column=1, sticky='ns')
        scrollbar_x.grid(row=1, column=0, sticky='ew')
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Status frame
        status_frame = tk.Frame(main_frame, bg='white')
        status_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(status_frame, text="एकूण व्यवहार:", bg='white', 
                font=('Arial', 10)).pack(side=tk.LEFT, padx=20)
        
        self.total_transactions_label = tk.Label(status_frame, text="₹0.00", bg='white', 
                                                font=('Arial', 10, 'bold'), fg='#0fcea7')
        self.total_transactions_label.pack(side=tk.LEFT, padx=5)
        
        tk.Label(status_frame, text="एकूण उदारी:", bg='white', 
                font=('Arial', 10)).pack(side=tk.LEFT, padx=20)
        
        self.total_transactions_credit_label = tk.Label(status_frame, text="₹0.00", bg='white', 
                                                       font=('Arial', 10, 'bold'), fg='#e94560')
        self.total_transactions_credit_label.pack(side=tk.LEFT, padx=5)
        
        # Load initial data
        self.search_transactions()
    
    def setup_credit_transactions_tab(self, parent):
        """Setup credit transactions tab"""
        main_frame = tk.Frame(parent, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        container = tk.Frame(main_frame, bg='white')
        container.pack(fill=tk.BOTH, expand=True)
        
        # Left frame - Customer credits
        left_frame = tk.Frame(container, bg='white')
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        customer_frame = tk.LabelFrame(left_frame, text="ग्राहक उधारी", 
                                      bg='white', font=('Arial', 12, 'bold'))
        customer_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        customer_search_frame = tk.Frame(customer_frame, bg='white')
        customer_search_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(customer_search_frame, text="शोध:", bg='white', 
                font=('Arial', 10)).pack(side=tk.LEFT)
        
        self.customer_credit_search = tk.Entry(customer_search_frame, width=15, 
                                              font=('Arial', 10))
        self.customer_credit_search.pack(side=tk.LEFT, padx=5)
        
        search_btn = tk.Button(customer_search_frame, text="🔍 शोधा", bg='#3a86ff', fg='white',
                              font=('Arial', 10), command=self.search_customer_credit)
        search_btn.pack(side=tk.LEFT, padx=5)
        
        customer_credit_tree_frame = tk.Frame(customer_frame, bg='white')
        customer_credit_tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        columns = ('नाव', 'एकूण उधारी', 'जमा', 'बाकी')
        self.customer_credit_tree = ttk.Treeview(customer_credit_tree_frame, 
                                                columns=columns, show='headings', height=15)
        
        for col in columns:
            self.customer_credit_tree.heading(col, text=col)
            self.customer_credit_tree.column(col, width=150, anchor='center')
        
        scrollbar = ttk.Scrollbar(customer_credit_tree_frame, orient=tk.VERTICAL, 
                                 command=self.customer_credit_tree.yview)
        self.customer_credit_tree.configure(yscrollcommand=scrollbar.set)
        
        self.customer_credit_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Right frame - Supplier credits
        right_frame = tk.Frame(container, bg='white')
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        supplier_frame = tk.LabelFrame(right_frame, text="पुरवठादार उधारी", 
                                      bg='white', font=('Arial', 12, 'bold'))
        supplier_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        supplier_search_frame = tk.Frame(supplier_frame, bg='white')
        supplier_search_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(supplier_search_frame, text="शोध:", bg='white', 
                font=('Arial', 10)).pack(side=tk.LEFT)
        
        self.supplier_credit_search = tk.Entry(supplier_search_frame, width=15, 
                                              font=('Arial', 10))
        self.supplier_credit_search.pack(side=tk.LEFT, padx=5)
        
        search_btn2 = tk.Button(supplier_search_frame, text="🔍 शोधा", bg='#3a86ff', fg='white',
                               font=('Arial', 10), command=self.search_supplier_credit)
        search_btn2.pack(side=tk.LEFT, padx=5)
        
        supplier_credit_tree_frame = tk.Frame(supplier_frame, bg='white')
        supplier_credit_tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        columns = ('नाव', 'एकूण उधारी', 'जमा', 'बाकी')
        self.supplier_credit_tree = ttk.Treeview(supplier_credit_tree_frame, 
                                                columns=columns, show='headings', height=15)
        
        for col in columns:
            self.supplier_credit_tree.heading(col, text=col)
            self.supplier_credit_tree.column(col, width=150, anchor='center')
        
        scrollbar2 = ttk.Scrollbar(supplier_credit_tree_frame, orient=tk.VERTICAL, 
                                  command=self.supplier_credit_tree.yview)
        self.supplier_credit_tree.configure(yscrollcommand=scrollbar2.set)
        
        self.supplier_credit_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar2.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load initial data
        self.load_customer_credit_data()
        self.load_supplier_credit_data()
    
    def setup_manual_credit_tab(self, parent):
        """Setup manual credit tab"""
        main_frame = tk.Frame(parent, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        filter_frame = tk.LabelFrame(main_frame, text="शोध आणि फिल्टर", 
                                    bg='white', font=('Arial', 10, 'bold'))
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(filter_frame, text="प्रकार:", bg='white', 
                font=('Arial', 10)).grid(row=0, column=0, padx=5, pady=5)
        
        self.credit_type_combo = ttk.Combobox(filter_frame, 
                                             values=['ग्राहक', 'पुरवठादार'], 
                                             width=15, font=('Arial', 10), state='readonly')
        self.credit_type_combo.grid(row=0, column=1, padx=5, pady=5)
        self.credit_type_combo.current(0)
        
        tk.Label(filter_frame, text="शोध:", bg='white', 
                font=('Arial', 10)).grid(row=0, column=2, padx=5, pady=5)
        
        self.manual_search_combo = ttk.Combobox(filter_frame, width=25, font=('Arial', 10))
        self.manual_search_combo.grid(row=0, column=3, padx=5, pady=5)
        
        search_btn = tk.Button(filter_frame, text="🔍 शोधा", bg='#3a86ff', fg='white',
                              font=('Arial', 10), command=self.search_manual_credit_list)
        search_btn.grid(row=0, column=4, padx=5, pady=5)
        
        list_frame = tk.Frame(main_frame, bg='white')
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        columns = ('नाव', 'सध्याची उधारी', 'फोन')
        self.manual_credit_tree = ttk.Treeview(list_frame, columns=columns, 
                                              show='headings', height=15)
        
        for col in columns:
            self.manual_credit_tree.heading(col, text=col)
            self.manual_credit_tree.column(col, width=150, anchor='center')
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, 
                                 command=self.manual_credit_tree.yview)
        self.manual_credit_tree.configure(yscrollcommand=scrollbar.set)
        
        self.manual_credit_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load initial data
        self.load_manual_credit_list()
    
    def search_transactions(self):
        """Search transactions based on filters"""
        for item in self.transactions_tree.get_children():
            self.transactions_tree.delete(item)
        
        transaction_type = self.transaction_type_filter.get()
        from_date = self.from_date_filter.get_date().strftime("%Y-%m-%d")
        to_date = self.to_date_filter.get_date().strftime("%Y-%m-%d")
        
        try:
            total_amount = 0
            total_credit = 0
            
            if transaction_type in ['सर्व', 'विक्री']:
                sales_query = """
                    SELECT invoice_no, date, customer_name, total_amount, 
                           discount_amount, paid_amount, balance_amount, 
                           payment_mode, status
                    FROM sales 
                    WHERE 1=1
                """
                sales_params = []
                
                if from_date:
                    sales_query += " AND DATE(date) >= ?"
                    sales_params.append(from_date)
                if to_date:
                    sales_query += " AND DATE(date) <= ?"
                    sales_params.append(to_date)
                
                sales_query += " ORDER BY date DESC"
                self.db.cursor.execute(sales_query, sales_params)
                sales_transactions = self.db.cursor.fetchall()
                
                for trans in sales_transactions:
                    invoice_no, date_str, contact_name, total, discount, paid, balance, payment_mode, status = trans
                    
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
                        'विक्री',
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
            
            if transaction_type in ['सर्व', 'खरेदी']:
                purchases_query = """
                    SELECT invoice_no, date, supplier_name, total_amount, 
                           paid_amount, balance_amount, payment_mode, status
                    FROM purchases 
                    WHERE 1=1
                """
                purchases_params = []
                
                if from_date:
                    purchases_query += " AND DATE(date) >= ?"
                    purchases_params.append(from_date)
                if to_date:
                    purchases_query += " AND DATE(date) <= ?"
                    purchases_params.append(to_date)
                
                purchases_query += " ORDER BY date DESC"
                self.db.cursor.execute(purchases_query, purchases_params)
                purchases_transactions = self.db.cursor.fetchall()
                
                for trans in purchases_transactions:
                    invoice_no, date_str, contact_name, total, paid, balance, payment_mode, status = trans
                    
                    try:
                        date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                        formatted_date = date_obj.strftime("%d/%m/%Y %H:%M")
                    except:
                        formatted_date = date_str
                    
                    balance_value = float(balance) if balance else 0
                    
                    values = (
                        invoice_no,
                        formatted_date,
                        'खरेदी',
                        contact_name if contact_name else "-",
                        f"₹{float(total):.2f}" if total else "₹0.00",
                        "₹0.00",
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
            messagebox.showerror("त्रुटी", f"व्यवहार शोध त्रुटी: {str(e)}")
    
    def load_customer_credit_data(self):
        """Load customer credit data"""
        try:
            for item in self.customer_credit_tree.get_children():
                self.customer_credit_tree.delete(item)
            
            self.db.cursor.execute('''
                SELECT name, credit_balance 
                FROM customers 
                WHERE credit_balance > 0 
                AND name NOT LIKE 'CUST-%'
                ORDER BY credit_balance DESC
            ''')
            customers = self.db.cursor.fetchall()
            
            for customer in customers:
                name, credit_balance = customer
                self.customer_credit_tree.insert('', tk.END, values=(
                    name,
                    f"₹{credit_balance:.2f}",
                    "₹0.00",
                    f"₹{credit_balance:.2f}"
                ))
        except Exception as e:
            print(f"Error loading customer credit data: {str(e)}")
    
    def search_customer_credit(self):
        """Search customer credit"""
        search_text = self.customer_credit_search.get().strip()
        
        for item in self.customer_credit_tree.get_children():
            self.customer_credit_tree.delete(item)
        
        try:
            query = '''
                SELECT name, credit_balance 
                FROM customers 
                WHERE credit_balance > 0 
                AND name NOT LIKE 'CUST-%'
            '''
            params = []
            
            if search_text:
                query += " AND name LIKE ?"
                params.append(f'%{search_text}%')
            
            query += " ORDER BY credit_balance DESC"
            self.db.cursor.execute(query, params)
            customers = self.db.cursor.fetchall()
            
            for customer in customers:
                name, credit_balance = customer
                self.customer_credit_tree.insert('', tk.END, values=(
                    name,
                    f"₹{credit_balance:.2f}",
                    "₹0.00",
                    f"₹{credit_balance:.2f}"
                ))
        except Exception as e:
            print(f"Error searching customer credit: {str(e)}")
    
    def load_supplier_credit_data(self):
        """Load supplier credit data"""
        try:
            for item in self.supplier_credit_tree.get_children():
                self.supplier_credit_tree.delete(item)
            
            self.db.cursor.execute('''
                SELECT name, credit_balance 
                FROM suppliers 
                WHERE credit_balance > 0
                ORDER BY credit_balance DESC
            ''')
            suppliers = self.db.cursor.fetchall()
            
            for supplier in suppliers:
                name, credit_balance = supplier
                self.supplier_credit_tree.insert('', tk.END, values=(
                    name,
                    f"₹{credit_balance:.2f}",
                    "₹0.00",
                    f"₹{credit_balance:.2f}"
                ))
        except Exception as e:
            print(f"Error loading supplier credit data: {str(e)}")
    
    def search_supplier_credit(self):
        """Search supplier credit"""
        search_text = self.supplier_credit_search.get().strip()
        
        for item in self.supplier_credit_tree.get_children():
            self.supplier_credit_tree.delete(item)
        
        try:
            query = '''
                SELECT name, credit_balance 
                FROM suppliers 
                WHERE credit_balance > 0
            '''
            params = []
            
            if search_text:
                query += " AND name LIKE ?"
                params.append(f'%{search_text}%')
            
            query += " ORDER BY credit_balance DESC"
            self.db.cursor.execute(query, params)
            suppliers = self.db.cursor.fetchall()
            
            for supplier in suppliers:
                name, credit_balance = supplier
                self.supplier_credit_tree.insert('', tk.END, values=(
                    name,
                    f"₹{credit_balance:.2f}",
                    "₹0.00",
                    f"₹{credit_balance:.2f}"
                ))
        except Exception as e:
            print(f"Error searching supplier credit: {str(e)}")
    
    def load_manual_credit_list(self):
        """Load manual credit list"""
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
                customers = self.db.cursor.fetchall()
                
                names = [row[0] for row in customers]
                self.manual_search_combo['values'] = names
                
                for name, credit, phone in customers:
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
                suppliers = self.db.cursor.fetchall()
                
                names = [row[0] for row in suppliers]
                self.manual_search_combo['values'] = names
                
                for name, credit, phone in suppliers:
                    self.manual_credit_tree.insert('', tk.END, values=(
                        name, 
                        f"₹{credit:.2f}", 
                        phone if phone else "-"
                    ))
        except Exception as e:
            print(f"Error loading manual credit list: {str(e)}")
    
    def search_manual_credit_list(self):
        """Search manual credit list"""
        search_text = self.manual_search_combo.get().strip()
        credit_type = self.credit_type_combo.get()
        
        for item in self.manual_credit_tree.get_children():
            self.manual_credit_tree.delete(item)
        
        try:
            if credit_type == 'ग्राहक':
                query = """
                    SELECT name, credit_balance, phone 
                    FROM customers 
                    WHERE name NOT LIKE 'CUST-%'
                """
                params = []
                
                if search_text:
                    query += " AND name LIKE ?"
                    params.append(f'%{search_text}%')
                
                query += " ORDER BY name"
                self.db.cursor.execute(query, params)
                customers = self.db.cursor.fetchall()
                
                for name, credit, phone in customers:
                    self.manual_credit_tree.insert('', tk.END, values=(
                        name, 
                        f"₹{credit:.2f}", 
                        phone if phone else "-"
                    ))
            else:
                query = """
                    SELECT name, credit_balance, phone 
                    FROM suppliers 
                    WHERE 1=1
                """
                params = []
                
                if search_text:
                    query += " AND name LIKE ?"
                    params.append(f'%{search_text}%')
                
                query += " ORDER BY name"
                self.db.cursor.execute(query, params)
                suppliers = self.db.cursor.fetchall()
                
                for name, credit, phone in suppliers:
                    self.manual_credit_tree.insert('', tk.END, values=(
                        name, 
                        f"₹{credit:.2f}", 
                        phone if phone else "-"
                    ))
        except Exception as e:
            print(f"Error searching manual credit list: {str(e)}")