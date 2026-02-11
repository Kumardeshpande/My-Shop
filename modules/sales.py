# modules/sales.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import tempfile
import sys
import subprocess
import os
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from tkcalendar import DateEntry

class SalesModule:
    def __init__(self, db, parent_app):
        self.db = db
        self.parent_app = parent_app
        self.sale_cart = []
    
    def create_sales_tab(self):
        """Create the sales tab content"""
        sales_frame = tk.Frame(self.parent_app.notebook, bg='white')
        
        main_container = tk.LabelFrame(sales_frame, text="💰 नवीन विक्री", bg='white', 
                                      font=('Arial', 12, 'bold'), bd=2, relief=tk.GROOVE)
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
        main_frame.grid_columnconfigure(1, weight=2)  # उजवा पॅनेल
        
        # Left panel - Product info
        left_panel = tk.LabelFrame(main_frame, text="उत्पादन माहिती", bg='white', 
                                  font=('Arial', 10, 'bold'), bd=1, relief=tk.GROOVE)
        left_panel.grid(row=0, column=0, sticky='nsew', padx=(0, 10))
        
        for i in range(12):
            left_panel.grid_rowconfigure(i, weight=0)
        left_panel.grid_columnconfigure(0, weight=0)  # लेबल स्तंभ
        left_panel.grid_columnconfigure(1, weight=1)  # इंट्री स्तंभ
        
        # Date
        tk.Label(left_panel, text="तारीख:", bg='white', font=('Arial', 10)).grid(
            row=0, column=0, padx=5, pady=5, sticky='w')
        self.sales_date_entry = DateEntry(left_panel, width=15, font=('Arial', 10), 
                                         date_pattern='dd/mm/yyyy')
        self.sales_date_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        
        # Customer
        tk.Label(left_panel, text="ग्राहक:", bg='white', font=('Arial', 10)).grid(
            row=1, column=0, padx=5, pady=5, sticky='w')
        self.customer_combo = ttk.Combobox(left_panel, font=('Arial', 10))
        self.customer_combo.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        
        # Barcode
        tk.Label(left_panel, text="बारकोड:", bg='white', font=('Arial', 10)).grid(
            row=2, column=0, padx=5, pady=5, sticky='w')
        self.barcode_search_entry = tk.Entry(left_panel, font=('Arial', 10))
        self.barcode_search_entry.grid(row=2, column=1, padx=5, pady=5, sticky='ew')
        
        # Category
        tk.Label(left_panel, text="कॅटेगिरी:", bg='white', font=('Arial', 10)).grid(
            row=3, column=0, padx=5, pady=5, sticky='w')
        self.sales_category_combo = ttk.Combobox(left_panel, font=('Arial', 10))
        self.sales_category_combo.grid(row=3, column=1, padx=5, pady=5, sticky='ew')
        
        # Product
        tk.Label(left_panel, text="उत्पादन:", bg='white', font=('Arial', 10)).grid(
            row=4, column=0, padx=5, pady=5, sticky='w')
        self.product_combo = ttk.Combobox(left_panel, font=('Arial', 10))
        self.product_combo.grid(row=4, column=1, padx=5, pady=5, sticky='ew')
        
        # Available stock
        tk.Label(left_panel, text="उपलब्ध स्टॉक:", bg='white', font=('Arial', 10)).grid(
            row=5, column=0, padx=5, pady=5, sticky='w')
        self.available_stock_label = tk.Label(left_panel, text="0", bg='white', font=('Arial', 10))
        self.available_stock_label.grid(row=5, column=1, padx=5, pady=5, sticky='w')
        
        # Purchase price
        tk.Label(left_panel, text="खरेदी किंमत:", bg='white', font=('Arial', 10)).grid(
            row=6, column=0, padx=5, pady=5, sticky='w')
        self.purchase_price_label = tk.Label(left_panel, text="₹0.00", bg='white', font=('Arial', 10))
        self.purchase_price_label.grid(row=6, column=1, padx=5, pady=5, sticky='w')
        
        # Sale price
        tk.Label(left_panel, text="विक्री किंमत:", bg='white', font=('Arial', 10)).grid(
            row=7, column=0, padx=5, pady=5, sticky='w')
        self.price_label = tk.Label(left_panel, text="₹0.00", bg='white', font=('Arial', 10))
        self.price_label.grid(row=7, column=1, padx=5, pady=5, sticky='w')
        
        # Quantity
        tk.Label(left_panel, text="नग:", bg='white', font=('Arial', 10)).grid(
            row=8, column=0, padx=5, pady=5, sticky='w')
        self.quantity_entry = tk.Entry(left_panel, font=('Arial', 10))
        self.quantity_entry.grid(row=8, column=1, padx=5, pady=5, sticky='ew')
        self.quantity_entry.insert(0, "1")
        
        # Item total
        tk.Label(left_panel, text="एकूण:", bg='white', font=('Arial', 10)).grid(
            row=9, column=0, padx=5, pady=5, sticky='w')
        self.item_total_label = tk.Label(left_panel, text="₹0.00", bg='white', font=('Arial', 10))
        self.item_total_label.grid(row=9, column=1, padx=5, pady=5, sticky='w')
        
        # Add to cart button
        add_to_cart_btn = tk.Button(left_panel, text="➕ कार्टमध्ये ऍड", bg='#3a86ff', fg='white',
                                  font=('Arial', 10), command=self.add_product_to_cart)
        add_to_cart_btn.grid(row=10, column=0, columnspan=2, pady=10, sticky='ew')
        
        # Right panel - Cart and bill
        right_panel = tk.Frame(main_frame, bg='white')
        right_panel.grid(row=0, column=1, sticky='nsew')
        right_panel.grid_rowconfigure(0, weight=1)  # कार्ट फ्रेम
        right_panel.grid_rowconfigure(1, weight=0)  # बिल फ्रेम
        right_panel.grid_columnconfigure(0, weight=1)
        
        # Cart frame
        cart_frame = tk.LabelFrame(right_panel, text="विक्री कार्ट", bg='white', 
                                  font=('Arial', 10, 'bold'), bd=1, relief=tk.GROOVE)
        cart_frame.grid(row=0, column=0, sticky='nsew', pady=(0, 10))
        cart_frame.grid_rowconfigure(0, weight=1)
        cart_frame.grid_columnconfigure(0, weight=1)
        
        columns = ('क्रमांक', 'उत्पादन', 'किंमत', 'प्रमाण', 'एकूण', 'काढा')
        self.cart_tree = ttk.Treeview(cart_frame, columns=columns, show='headings', height=10)
        
        column_widths = [50, 150, 80, 80, 100, 80]
        for i, (col, width) in enumerate(zip(columns, column_widths)):
            self.cart_tree.heading(col, text=col)
            self.cart_tree.column(col, width=width, anchor='center')
        
        scrollbar = ttk.Scrollbar(cart_frame, orient=tk.VERTICAL, command=self.cart_tree.yview)
        self.cart_tree.configure(yscrollcommand=scrollbar.set)
        self.cart_tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')
        
        # Bill frame
        bill_frame = tk.LabelFrame(right_panel, text="बिल माहिती", bg='white', 
                                  font=('Arial', 10, 'bold'), bd=1, relief=tk.GROOVE)
        bill_frame.grid(row=1, column=0, sticky='ew')
        
        for i in range(7):
            bill_frame.grid_rowconfigure(i, weight=0)
        bill_frame.grid_columnconfigure(0, weight=0)  # लेबल स्तंभ
        bill_frame.grid_columnconfigure(1, weight=1)  # मूल्य स्तंभ
        
        # Total amount
        tk.Label(bill_frame, text="एकूण बिल:", bg='white', font=('Arial', 11)).grid(
            row=0, column=0, padx=10, pady=5, sticky='w')
        self.total_amount_label = tk.Label(bill_frame, text="₹0.00", bg='white', 
                                          font=('Arial', 11, 'bold'), fg='#0fcea7')
        self.total_amount_label.grid(row=0, column=1, padx=10, pady=5, sticky='w')
        
        # Discount
        tk.Label(bill_frame, text="सवलत:", bg='white', font=('Arial', 11)).grid(
            row=1, column=0, padx=10, pady=5, sticky='w')
        
        discount_frame = tk.Frame(bill_frame, bg='white')
        discount_frame.grid(row=1, column=1, padx=10, pady=5, sticky='w')
        discount_frame.grid_columnconfigure(0, weight=1)
        discount_frame.grid_columnconfigure(1, weight=0)
        
        self.discount_entry = tk.Entry(discount_frame, width=10, font=('Arial', 10))
        self.discount_entry.grid(row=0, column=0, sticky='ew')
        self.discount_entry.insert(0, "0")
        
        self.discount_type = ttk.Combobox(discount_frame, values=['₹', '%'], width=5, 
                                         state='readonly', font=('Arial', 10))
        self.discount_type.grid(row=0, column=1, padx=5, sticky='ew')
        self.discount_type.current(0)
        
        # Final total
        tk.Label(bill_frame, text="सवलतीनंतर बिल:", bg='white', font=('Arial', 11)).grid(
            row=2, column=0, padx=10, pady=5, sticky='w')
        self.final_total_label = tk.Label(bill_frame, text="₹0.00", bg='white', 
                                         font=('Arial', 11, 'bold'), fg='#f0a500')
        self.final_total_label.grid(row=2, column=1, padx=10, pady=5, sticky='w')
        
        # Paid amount
        tk.Label(bill_frame, text="जमा रक्कम:", bg='white', font=('Arial', 11)).grid(
            row=3, column=0, padx=10, pady=5, sticky='w')
        self.paid_amount_entry = tk.Entry(bill_frame, width=15, font=('Arial', 10))
        self.paid_amount_entry.grid(row=3, column=1, padx=10, pady=5, sticky='ew')
        
        # Balance amount
        tk.Label(bill_frame, text="बाकी रक्कम:", bg='white', font=('Arial', 11)).grid(
            row=4, column=0, padx=10, pady=5, sticky='w')
        self.balance_label = tk.Label(bill_frame, text="₹0.00", bg='white', 
                                     font=('Arial', 11, 'bold'), fg='#7209b7')
        self.balance_label.grid(row=4, column=1, padx=10, pady=5, sticky='w')
        
        # Payment mode
        tk.Label(bill_frame, text="पेमेंट मोड:", bg='white', font=('Arial', 11)).grid(
            row=5, column=0, padx=10, pady=5, sticky='w')
        self.payment_mode = ttk.Combobox(bill_frame, values=['रोख', 'UPI', 'उदारी', 'आंशिक जमा'], 
                                        width=15, state='readonly', font=('Arial', 10))
        self.payment_mode.grid(row=5, column=1, padx=10, pady=5, sticky='ew')
        self.payment_mode.current(0)
        
        # Buttons
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
        
        return sales_frame
    
    def load_categories_for_sale(self):
        """Load categories for sales tab"""
        try:
            self.db.cursor.execute("SELECT DISTINCT category FROM products WHERE category IS NOT NULL AND category != '' ORDER BY category")
            categories = [row[0] for row in self.db.cursor.fetchall()]
            self.sales_category_combo['values'] = categories
        except:
            self.sales_category_combo['values'] = []
    
    def load_products_by_category(self):
        """Load products by selected category"""
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
        """Load product details when selected"""
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
    
    def calculate_item_total(self):
        """Calculate item total price"""
        try:
            price_text = self.price_label.cget("text").replace('₹', '')
            price = float(price_text)
            quantity = int(self.quantity_entry.get())
            total = price * quantity
            self.item_total_label.config(text=f"₹{total:.2f}")
        except:
            self.item_total_label.config(text="₹0.00")
    
    def add_product_to_cart(self):
        """Add product to sales cart"""
        product_name = self.product_combo.get()
        if not product_name:
            messagebox.showerror("त्रुटी", "कृपया उत्पादन निवडा")
            return
        
        try:
            available_stock = int(self.available_stock_label.cget("text"))
            price_text = self.price_label.cget("text").replace('₹', '')
            price = float(price_text)
            quantity = int(self.quantity_entry.get())
            
            if quantity > available_stock:
                messagebox.showerror("त्रुटी", f"स्टॉक अपुरा! उपलब्ध: {available_stock}")
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
            
            # Reset fields
            self.quantity_entry.delete(0, tk.END)
            self.quantity_entry.insert(0, "1")
            self.item_total_label.config(text="₹0.00")
            self.product_combo.set('')
            self.price_label.config(text="₹0.00")
            self.purchase_price_label.config(text="₹0.00")
            self.available_stock_label.config(text="0")
            self.barcode_search_entry.delete(0, tk.END)
            
        except ValueError:
            messagebox.showerror("त्रुटी", "कृपया वैध प्रमाण प्रविष्ट करा")
    
    def calculate_sale_total(self):
        """Calculate total sale amount"""
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
        
        # Update paid amount if cart has items
        if self.sale_cart:
            self.paid_amount_entry.delete(0, tk.END)
            self.paid_amount_entry.insert(0, str(final_total))
            self.balance_label.config(text="₹0.00")
    
    def save_sale(self):
        """Save sale to database"""
        customer_name = self.customer_combo.get()
        payment_mode = self.payment_mode.get()
        
        if not customer_name:
            messagebox.showerror("त्रुटी", "कृपया ग्राहक नाव प्रविष्ट करा")
            return
        
        if not self.sale_cart:
            messagebox.showerror("त्रुटी", "कार्ट रिकामा आहे")
            return
        
        try:
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
            
            self.db.conn.commit()
            messagebox.showinfo("यशस्वी", f"विक्री यशस्वीरित्या नोंदवली गेली!\nबिल क्रमांक: {invoice_no}")
            
            # Clear cart after successful sale
            self.clear_sale_cart()
            
        except Exception as e:
            messagebox.showerror("त्रुटी", f"विक्री नोंदवताना त्रुटी: {str(e)}")
            self.db.conn.rollback()