# modules/purchases.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class PurchasesModule:
    def __init__(self, db, parent_app):
        self.db = db
        self.parent_app = parent_app
        self.purchase_cart = []
    
    def create_purchases_tab(self):
        """Create the purchases tab content"""
        purchase_frame = tk.Frame(self.parent_app.notebook, bg='white')
        
        main_container = tk.LabelFrame(purchase_frame, text="🛒 नवीन खरेदी", bg='white', 
                                      font=('Arial', 12, 'bold'), bd=2, relief=tk.GROOVE)
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
        main_frame.grid_columnconfigure(1, weight=2)  # उजवा पॅनेल
        
        # Left panel - Supplier and product info
        left_panel = tk.Frame(main_frame, bg='white')
        left_panel.grid(row=0, column=0, sticky='nsew', padx=(0, 10))
        left_panel.grid_rowconfigure(0, weight=0)  # Supplier frame
        left_panel.grid_rowconfigure(1, weight=1)  # Product frame
        left_panel.grid_columnconfigure(0, weight=1)
        
        # Supplier frame
        supplier_frame = tk.LabelFrame(left_panel, text="पुरवठादार माहिती", bg='white', 
                                      font=('Arial', 10, 'bold'), bd=1, relief=tk.GROOVE)
        supplier_frame.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        
        for i in range(4):
            supplier_frame.grid_rowconfigure(i, weight=0)
        supplier_frame.grid_columnconfigure(0, weight=0)  # लेबल स्तंभ
        supplier_frame.grid_columnconfigure(1, weight=1)  # इंट्री स्तंभ
        supplier_frame.grid_columnconfigure(2, weight=0)  # बटण स्तंभ
        
        tk.Label(supplier_frame, text="पुरवठादार:", bg='white', font=('Arial', 10)).grid(
            row=0, column=0, padx=5, pady=5, sticky='w')
        self.supplier_combo = ttk.Combobox(supplier_frame, font=('Arial', 10))
        self.supplier_combo.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        
        new_supplier_btn = tk.Button(supplier_frame, text="+ नवीन", bg='#0fcea7', fg='white',
                                    font=('Arial', 9), command=self.add_new_supplier)
        new_supplier_btn.grid(row=0, column=2, padx=5, pady=5)
        
        tk.Label(supplier_frame, text="फोन:", bg='white', font=('Arial', 10)).grid(
            row=1, column=0, padx=5, pady=5, sticky='w')
        self.supplier_phone_label = tk.Label(supplier_frame, text="", bg='white', font=('Arial', 10))
        self.supplier_phone_label.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        
        tk.Label(supplier_frame, text="उधारी:", bg='white', font=('Arial', 10)).grid(
            row=2, column=0, padx=5, pady=5, sticky='w')
        self.supplier_credit_label = tk.Label(supplier_frame, text="₹0.00", bg='white', 
                                            font=('Arial', 10, 'bold'), fg='#e94560')
        self.supplier_credit_label.grid(row=2, column=1, padx=5, pady=5, sticky='w')
        
        # Product frame
        product_frame = tk.LabelFrame(left_panel, text="उत्पादन माहिती", bg='white', 
                                     font=('Arial', 10, 'bold'), bd=1, relief=tk.GROOVE)
        product_frame.grid(row=1, column=0, sticky='nsew')
        
        for i in range(12):
            product_frame.grid_rowconfigure(i, weight=0)
        product_frame.grid_columnconfigure(0, weight=0)  # लेबल स्तंभ
        product_frame.grid_columnconfigure(1, weight=1)  # इंट्री स्तंभ
        
        row_counter = 0
        
        # Category
        tk.Label(product_frame, text="कॅटेगिरी:", bg='white', font=('Arial', 10)).grid(
            row=row_counter, column=0, padx=5, pady=5, sticky='w')
        self.purchase_category_combo = ttk.Combobox(product_frame, font=('Arial', 10))
        self.purchase_category_combo.grid(row=row_counter, column=1, padx=5, pady=5, sticky='ew')
        row_counter += 1
        
        # Product
        tk.Label(product_frame, text="उत्पादन:", bg='white', font=('Arial', 10)).grid(
            row=row_counter, column=0, padx=5, pady=5, sticky='w')
        self.purchase_product_combo = ttk.Combobox(product_frame, font=('Arial', 10))
        self.purchase_product_combo.grid(row=row_counter, column=1, padx=5, pady=5, sticky='ew')
        row_counter += 1
        
        # Barcode
        tk.Label(product_frame, text="बारकोड:", bg='white', font=('Arial', 10)).grid(
            row=row_counter, column=0, padx=5, pady=5, sticky='w')
        self.purchase_barcode_entry = tk.Entry(product_frame, font=('Arial', 10))
        self.purchase_barcode_entry.grid(row=row_counter, column=1, padx=5, pady=5, sticky='ew')
        row_counter += 1
        
        # Current stock
        tk.Label(product_frame, text="सध्याचा स्टॉक:", bg='white', font=('Arial', 10)).grid(
            row=row_counter, column=0, padx=5, pady=5, sticky='w')
        self.current_stock_label = tk.Label(product_frame, text="0", bg='white', font=('Arial', 10))
        self.current_stock_label.grid(row=row_counter, column=1, padx=5, pady=5, sticky='w')
        row_counter += 1
        
        # Purchase price
        tk.Label(product_frame, text="खरेदी किंमत:", bg='white', font=('Arial', 10)).grid(
            row=row_counter, column=0, padx=5, pady=5, sticky='w')
        self.purchase_price_entry = tk.Entry(product_frame, font=('Arial', 10))
        self.purchase_price_entry.grid(row=row_counter, column=1, padx=5, pady=5, sticky='ew')
        row_counter += 1
        
        # Sale price
        tk.Label(product_frame, text="विक्री किंमत:", bg='white', font=('Arial', 10)).grid(
            row=row_counter, column=0, padx=5, pady=5, sticky='w')
        self.sale_price_entry = tk.Entry(product_frame, font=('Arial', 10))
        self.sale_price_entry.grid(row=row_counter, column=1, padx=5, pady=5, sticky='ew')
        row_counter += 1
        
        # Quantity
        tk.Label(product_frame, text="खरेदी नग:", bg='white', font=('Arial', 10)).grid(
            row=row_counter, column=0, padx=5, pady=5, sticky='w')
        self.purchase_quantity_entry = tk.Entry(product_frame, font=('Arial', 10))
        self.purchase_quantity_entry.grid(row=row_counter, column=1, padx=5, pady=5, sticky='ew')
        self.purchase_quantity_entry.insert(0, "1")
        row_counter += 1
        
        # Item total
        tk.Label(product_frame, text="एकूण किंमत:", bg='white', font=('Arial', 10)).grid(
            row=row_counter, column=0, padx=5, pady=5, sticky='w')
        self.purchase_item_total_label = tk.Label(product_frame, text="₹0.00", bg='white', font=('Arial', 10))
        self.purchase_item_total_label.grid(row=row_counter, column=1, padx=5, pady=5, sticky='w')
        row_counter += 1
        
        # Add to cart button
        add_product_btn = tk.Button(product_frame, text="➕ कार्टमध्ये ऍड", bg='#3a86ff', fg='white',
                                  font=('Arial', 10), command=self.add_product_to_purchase_cart)
        add_product_btn.grid(row=row_counter, column=0, columnspan=2, pady=10, sticky='ew')
        
        # Right panel - Cart and bill
        right_panel = tk.Frame(main_frame, bg='white')
        right_panel.grid(row=0, column=1, sticky='nsew')
        right_panel.grid_rowconfigure(0, weight=1)  # कार्ट फ्रेम
        right_panel.grid_rowconfigure(1, weight=0)  # बिल फ्रेम
        right_panel.grid_columnconfigure(0, weight=1)
        
        # Cart frame
        cart_frame = tk.LabelFrame(right_panel, text="खरेदी कार्ट", bg='white', 
                                  font=('Arial', 10, 'bold'), bd=1, relief=tk.GROOVE)
        cart_frame.grid(row=0, column=0, sticky='nsew', pady=(0, 10))
        cart_frame.grid_rowconfigure(0, weight=1)
        cart_frame.grid_columnconfigure(0, weight=1)
        
        columns = ('क्रमांक', 'उत्पादन', 'खरेदी किं.', 'विक्री किं.', 'प्रमाण', 'एकूण', 'काढा')
        self.purchase_cart_tree = ttk.Treeview(cart_frame, columns=columns, show='headings', height=10)
        
        column_widths = [50, 150, 80, 80, 60, 80, 60]
        for i, (col, width) in enumerate(zip(columns, column_widths)):
            self.purchase_cart_tree.heading(col, text=col)
            self.purchase_cart_tree.column(col, width=width, anchor='center')
        
        scrollbar = ttk.Scrollbar(cart_frame, orient=tk.VERTICAL, command=self.purchase_cart_tree.yview)
        self.purchase_cart_tree.configure(yscrollcommand=scrollbar.set)
        self.purchase_cart_tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')
        
        # Bill frame
        bill_frame = tk.LabelFrame(right_panel, text="बिल माहिती", bg='white', 
                                  font=('Arial', 10, 'bold'), bd=1, relief=tk.GROOVE)
        bill_frame.grid(row=1, column=0, sticky='ew')
        
        for i in range(6):
            bill_frame.grid_rowconfigure(i, weight=0)
        bill_frame.grid_columnconfigure(0, weight=0)  # लेबल स्तंभ
        bill_frame.grid_columnconfigure(1, weight=1)  # मूल्य स्तंभ
        
        # Total amount
        tk.Label(bill_frame, text="एकूण रक्कम:", bg='white', font=('Arial', 11)).grid(
            row=0, column=0, padx=10, pady=5, sticky='w')
        self.purchase_total_label = tk.Label(bill_frame, text="₹0.00", bg='white', 
                                           font=('Arial', 11, 'bold'), fg='#0fcea7')
        self.purchase_total_label.grid(row=0, column=1, padx=10, pady=5, sticky='w')
        
        # Paid amount
        tk.Label(bill_frame, text="जमा रक्कम:", bg='white', font=('Arial', 11)).grid(
            row=1, column=0, padx=10, pady=5, sticky='w')
        self.purchase_paid_entry = tk.Entry(bill_frame, font=('Arial', 10))
        self.purchase_paid_entry.grid(row=1, column=1, padx=10, pady=5, sticky='ew')
        self.purchase_paid_entry.insert(0, "0")
        
        # Balance amount
        tk.Label(bill_frame, text="उर्वरित:", bg='white', font=('Arial', 11)).grid(
            row=2, column=0, padx=10, pady=5, sticky='w')
        self.purchase_balance_label = tk.Label(bill_frame, text="₹0.00", bg='white', 
                                             font=('Arial', 11, 'bold'), fg='#7209b7')
        self.purchase_balance_label.grid(row=2, column=1, padx=10, pady=5, sticky='w')
        
        # Payment mode
        tk.Label(bill_frame, text="पेमेंट मोड:", bg='white', font=('Arial', 11)).grid(
            row=3, column=0, padx=10, pady=5, sticky='w')
        self.purchase_payment_mode = ttk.Combobox(bill_frame, 
                                                 values=['रोख', 'बँक ट्रान्सफर', 'चेक', 'उदारी', 'आंशिक जमा'], 
                                                 state='readonly', font=('Arial', 10))
        self.purchase_payment_mode.grid(row=3, column=1, padx=10, pady=5, sticky='ew')
        self.purchase_payment_mode.current(0)
        
        # Buttons
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
        
        return purchase_frame
    
    def add_new_supplier(self):
        """Add new supplier dialog"""
        dialog = tk.Toplevel(self.parent_app.root)
        dialog.title("नवीन पुरवठादार")
        dialog.geometry("400x250")
        dialog.configure(bg='white')
        dialog.transient(self.parent_app.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="नवीन पुरवठादार माहिती", font=('Arial', 14, 'bold'), bg='white').pack(pady=10)
        
        form_frame = tk.Frame(dialog, bg='white')
        form_frame.pack(pady=10, padx=20)
        
        tk.Label(form_frame, text="नाव*:", bg='white', font=('Arial', 10)).grid(
            row=0, column=0, padx=5, pady=5, sticky='w')
        name_entry = tk.Entry(form_frame, width=30, font=('Arial', 10))
        name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(form_frame, text="फोन:", bg='white', font=('Arial', 10)).grid(
            row=1, column=0, padx=5, pady=5, sticky='w')
        phone_entry = tk.Entry(form_frame, width=30, font=('Arial', 10))
        phone_entry.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(form_frame, text="पत्ता:", bg='white', font=('Arial', 10)).grid(
            row=2, column=0, padx=5, pady=5, sticky='w')
        address_entry = tk.Entry(form_frame, width=30, font=('Arial', 10))
        address_entry.grid(row=2, column=1, padx=5, pady=5)
        
        def save_supplier():
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("त्रुटी", "कृपया पुरवठादाराचे नाव प्रविष्ट करा")
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
                self.load_suppliers()
                self.supplier_combo.set(name)
            except Exception as e:
                messagebox.showerror("त्रुटी", f"पुरवठादार जोड त्रुटी: {str(e)}")
        
        button_frame = tk.Frame(dialog, bg='white')
        button_frame.pack(pady=20)
        
        save_btn = tk.Button(button_frame, text="💾 सेव्ह करा", bg='#0fcea7', fg='white',
                           font=('Arial', 10), command=save_supplier)
        save_btn.pack(side=tk.LEFT, padx=10)
        
        cancel_btn = tk.Button(button_frame, text="रद्द करा", bg='#e94560', fg='white',
                             font=('Arial', 10), command=dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=10)
    
    def load_suppliers(self):
        """Load suppliers for combobox"""
        try:
            self.db.cursor.execute("SELECT name FROM suppliers ORDER BY name")
            suppliers = [row[0] for row in self.db.cursor.fetchall()]
            self.supplier_combo['values'] = suppliers
            if suppliers:
                self.supplier_combo.current(0)
        except:
            self.supplier_combo['values'] = []
    
    def add_product_to_purchase_cart(self):
        """Add product to purchase cart"""
        product_name = self.purchase_product_combo.get()
        if not product_name:
            messagebox.showerror("त्रुटी", "कृपया उत्पादन निवडा")
            return
        
        try:
            purchase_price = float(self.purchase_price_entry.get())
            sale_price = float(self.sale_price_entry.get())
            quantity = int(self.purchase_quantity_entry.get())
            total = purchase_price * quantity
            
            cart_item = {
                'name': product_name,
                'barcode': self.purchase_barcode_entry.get(),
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
            self.calculate_purchase_total()
            
            # Reset fields
            self.purchase_quantity_entry.delete(0, tk.END)
            self.purchase_quantity_entry.insert(0, "1")
            self.purchase_item_total_label.config(text="₹0.00")
            self.purchase_product_combo.set('')
            self.purchase_barcode_entry.delete(0, tk.END)
            self.current_stock_label.config(text="0")
            self.purchase_price_entry.delete(0, tk.END)
            self.sale_price_entry.delete(0, tk.END)
            
        except ValueError:
            messagebox.showerror("त्रुटी", "कृपया वैध संख्या प्रविष्ट करा")
    
    def calculate_purchase_total(self):
        """Calculate total purchase amount"""
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
    
    def save_purchase(self):
        """Save purchase to database"""
        supplier_name = self.supplier_combo.get()
        payment_mode = self.purchase_payment_mode.get()
        
        if not supplier_name:
            messagebox.showerror("त्रुटी", "कृपया पुरवठादार निवडा")
            return
        
        if not self.purchase_cart:
            messagebox.showerror("त्रुटी", "कार्ट रिकामा आहे")
            return
        
        try:
            total = sum(item['total'] for item in self.purchase_cart)
            paid_text = self.purchase_paid_entry.get()
            
            try:
                paid = float(paid_text) if paid_text else 0
            except:
                paid = 0
            
            balance = total - paid
            if balance < 0:
                messagebox.showerror("त्रुटी", "जमा रक्कम एकूण रक्कमपेक्षा जास्त असू शकत नाही")
                return
            
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
            messagebox.showinfo("यशस्वी", f"खरेदी यशस्वीरित्या नोंदवली!\nबिल क्रमांक: {invoice_no}")
            self.clear_purchase_cart()
            
        except Exception as e:
            messagebox.showerror("त्रुटी", f"खरेदी सेव त्रुटी: {str(e)}")
    
    def clear_purchase_cart(self):
        """Clear purchase cart"""
        self.purchase_cart = []
        for item in self.purchase_cart_tree.get_children():
            self.purchase_cart_tree.delete(item)
        
        self.purchase_total_label.config(text="₹0.00")
        self.purchase_balance_label.config(text="₹0.00")
        self.purchase_paid_entry.delete(0, tk.END)
        self.purchase_paid_entry.insert(0, "0")
        self.purchase_payment_mode.set('रोख')
        
    # modules/purchases.py च्या शेवटी add करा:
    def get_purchases_frame(self):
        """Get the purchases frame for the notebook"""
        return self.create_purchases_tab()