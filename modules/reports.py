# modules/reports.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from tkcalendar import DateEntry

class ReportsModule:
    def __init__(self, db, parent_app):
        self.db = db
        self.parent_app = parent_app
    
    def create_reports_tab(self):
        """Create the reports tab content"""
        reports_frame = tk.Frame(self.parent_app.notebook, bg='white')
        
        main_container = tk.Frame(reports_frame, bg='white')
        main_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        header_frame = tk.Frame(main_container, bg='white')
        header_frame.pack(fill=tk.X, pady=(0, 15), padx=10)
        tk.Label(header_frame, text="📊 अहवाल", 
                font=('Arial', 20, 'bold'), bg='white').pack(side=tk.LEFT)
        
        self.reports_notebook = ttk.Notebook(main_container)
        self.reports_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Daily report tab
        daily_report_tab = tk.Frame(self.reports_notebook, bg='white')
        self.reports_notebook.add(daily_report_tab, text="दैनिक अहवाल")
        self.setup_daily_report_tab(daily_report_tab)
        
        # Monthly report tab
        monthly_report_tab = tk.Frame(self.reports_notebook, bg='white')
        self.reports_notebook.add(monthly_report_tab, text="मासिक अहवाल")
        self.setup_monthly_report_tab(monthly_report_tab)
        
        # Credit report tab
        credit_report_tab = tk.Frame(self.reports_notebook, bg='white')
        self.reports_notebook.add(credit_report_tab, text="उधारी अहवाल")
        self.setup_credit_report_tab(credit_report_tab)
        
        return reports_frame
    
    def setup_daily_report_tab(self, parent):
        """Setup daily report tab"""
        main_frame = tk.Frame(parent, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Date selection
        date_frame = tk.LabelFrame(main_frame, text="तारीख निवडा", 
                                  bg='white', font=('Arial', 10, 'bold'))
        date_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(date_frame, text="तारीख:", bg='white', 
                font=('Arial', 10)).pack(side=tk.LEFT, padx=10, pady=10)
        
        self.daily_date_picker = DateEntry(date_frame, width=15, 
                                          font=('Arial', 10), date_pattern='dd/mm/yyyy')
        self.daily_date_picker.pack(side=tk.LEFT, padx=5, pady=10)
        
        generate_btn = tk.Button(date_frame, text="📊 अहवाल तयार करा", bg='#0fcea7', fg='white',
                               font=('Arial', 10), command=self.generate_daily_report)
        generate_btn.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Report display frame
        report_frame = tk.LabelFrame(main_frame, text="दैनिक अहवाल", 
                                    bg='white', font=('Arial', 10, 'bold'))
        report_frame.pack(fill=tk.BOTH, expand=True)
        
        # Text widget for report display
        self.daily_report_text = tk.Text(report_frame, bg='white', font=('Courier New', 10),
                                        height=20, wrap=tk.WORD)
        scrollbar = tk.Scrollbar(report_frame, command=self.daily_report_text.yview)
        self.daily_report_text.configure(yscrollcommand=scrollbar.set)
        
        self.daily_report_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def setup_monthly_report_tab(self, parent):
        """Setup monthly report tab"""
        main_frame = tk.Frame(parent, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Month selection
        month_frame = tk.LabelFrame(main_frame, text="महिना निवडा", 
                                   bg='white', font=('Arial', 10, 'bold'))
        month_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(month_frame, text="महिना:", bg='white', 
                font=('Arial', 10)).pack(side=tk.LEFT, padx=10, pady=10)
        
        current_year = datetime.now().year
        months = ['जानेवारी', 'फेब्रुवारी', 'मार्च', 'एप्रिल', 'मे', 'जून',
                 'जुलै', 'ऑगस्ट', 'सप्टेंबर', 'ऑक्टोबर', 'नोव्हेंबर', 'डिसेंबर']
        
        self.month_combo = ttk.Combobox(month_frame, values=months, 
                                       width=15, font=('Arial', 10), state='readonly')
        self.month_combo.pack(side=tk.LEFT, padx=5, pady=10)
        self.month_combo.current(datetime.now().month - 1)
        
        tk.Label(month_frame, text="वर्ष:", bg='white', 
                font=('Arial', 10)).pack(side=tk.LEFT, padx=10, pady=10)
        
        years = list(range(current_year - 5, current_year + 1))
        self.year_combo = ttk.Combobox(month_frame, values=years, 
                                      width=10, font=('Arial', 10), state='readonly')
        self.year_combo.pack(side=tk.LEFT, padx=5, pady=10)
        self.year_combo.set(current_year)
        
        generate_btn = tk.Button(month_frame, text="📊 अहवाल तयार करा", bg='#0fcea7', fg='white',
                               font=('Arial', 10), command=self.generate_monthly_report)
        generate_btn.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Report display frame
        report_frame = tk.LabelFrame(main_frame, text="मासिक अहवाल", 
                                    bg='white', font=('Arial', 10, 'bold'))
        report_frame.pack(fill=tk.BOTH, expand=True)
        
        # Text widget for report display
        self.monthly_report_text = tk.Text(report_frame, bg='white', font=('Courier New', 10),
                                          height=20, wrap=tk.WORD)
        scrollbar = tk.Scrollbar(report_frame, command=self.monthly_report_text.yview)
        self.monthly_report_text.configure(yscrollcommand=scrollbar.set)
        
        self.monthly_report_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def setup_credit_report_tab(self, parent):
        """Setup credit report tab"""
        main_frame = tk.Frame(parent, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Report type selection
        type_frame = tk.LabelFrame(main_frame, text="अहवाल प्रकार", 
                                  bg='white', font=('Arial', 10, 'bold'))
        type_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(type_frame, text="प्रकार:", bg='white', 
                font=('Arial', 10)).pack(side=tk.LEFT, padx=10, pady=10)
        
        self.credit_type_combo = ttk.Combobox(type_frame, 
                                             values=['ग्राहक उधारी', 'पुरवठादार उधारी', 'सर्व उधारी'], 
                                             width=20, font=('Arial', 10), state='readonly')
        self.credit_type_combo.pack(side=tk.LEFT, padx=5, pady=10)
        self.credit_type_combo.current(0)
        
        generate_btn = tk.Button(type_frame, text="📊 अहवाल तयार करा", bg='#0fcea7', fg='white',
                               font=('Arial', 10), command=self.generate_credit_report)
        generate_btn.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Report display frame
        report_frame = tk.LabelFrame(main_frame, text="उधारी अहवाल", 
                                    bg='white', font=('Arial', 10, 'bold'))
        report_frame.pack(fill=tk.BOTH, expand=True)
        
        # Text widget for report display
        self.credit_report_text = tk.Text(report_frame, bg='white', font=('Courier New', 10),
                                         height=20, wrap=tk.WORD)
        scrollbar = tk.Scrollbar(report_frame, command=self.credit_report_text.yview)
        self.credit_report_text.configure(yscrollcommand=scrollbar.set)
        
        self.credit_report_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def generate_daily_report(self):
        """Generate daily report"""
        selected_date = self.daily_date_picker.get_date().strftime("%Y-%m-%d")
        
        self.daily_report_text.delete(1.0, tk.END)
        
        try:
            # Get sales for the day
            self.db.cursor.execute('''
                SELECT COUNT(*) as total_sales, 
                       SUM(total_amount) as total_sales_amount,
                       SUM(paid_amount) as total_paid,
                       SUM(balance_amount) as total_balance
                FROM sales 
                WHERE DATE(date) = ?
            ''', (selected_date,))
            
            sales_result = self.db.cursor.fetchone()
            total_sales = sales_result[0] or 0
            total_sales_amount = sales_result[1] or 0
            total_paid = sales_result[2] or 0
            total_balance = sales_result[3] or 0
            
            # Get purchases for the day
            self.db.cursor.execute('''
                SELECT COUNT(*) as total_purchases, 
                       SUM(total_amount) as total_purchases_amount
                FROM purchases 
                WHERE DATE(date) = ?
            ''', (selected_date,))
            
            purchases_result = self.db.cursor.fetchone()
            total_purchases = purchases_result[0] or 0
            total_purchases_amount = purchases_result[1] or 0
            
            # Get top selling products
            self.db.cursor.execute('''
                SELECT si.product_name, SUM(si.quantity) as total_quantity, 
                       SUM(si.total) as total_amount
                FROM sale_items si
                JOIN sales s ON si.sale_id = s.id
                WHERE DATE(s.date) = ?
                GROUP BY si.product_name
                ORDER BY total_quantity DESC
                LIMIT 10
            ''', (selected_date,))
            
            top_products = self.db.cursor.fetchall()
            
            # Generate report
            report = "=" * 60 + "\n"
            report += f"{'दैनिक अहवाल':^60}\n"
            report += f"{'तारीख: ' + selected_date:^60}\n"
            report += "=" * 60 + "\n\n"
            
            report += f"📊 एकूण विक्री: {total_sales}\n"
            report += f"💰 विक्री रक्कम: ₹{total_sales_amount:,.2f}\n"
            report += f"💳 जमा रक्कम: ₹{total_paid:,.2f}\n"
            report += f"📈 उर्वरित रक्कम: ₹{total_balance:,.2f}\n\n"
            
            report += f"🛒 एकूण खरेदी: {total_purchases}\n"
            report += f"💰 खरेदी रक्कम: ₹{total_purchases_amount:,.2f}\n\n"
            
            report += f"📈 निव्वळ उत्पन्न: ₹{total_paid - total_purchases_amount:,.2f}\n\n"
            
            if top_products:
                report += "🏆 टॉप 10 विकल्या गेलेले उत्पादने:\n"
                report += "-" * 60 + "\n"
                report += f"{'उत्पादन':<30} {'नग':<10} {'रक्कम':<15}\n"
                report += "-" * 60 + "\n"
                
                for product in top_products:
                    product_name, quantity, amount = product
                    report += f"{product_name[:28]:<30} {quantity:<10} ₹{amount:,.2f}\n"
            
            self.daily_report_text.insert(1.0, report)
            
        except Exception as e:
            messagebox.showerror("त्रुटी", f"अहवाल तयार करताना त्रुटी: {str(e)}")
    
    def generate_monthly_report(self):
        """Generate monthly report"""
        month_index = self.month_combo.current() + 1
        year = int(self.year_combo.get())
        month_str = f"{year}-{month_index:02d}"
        
        self.monthly_report_text.delete(1.0, tk.END)
        
        try:
            # Get sales for the month
            self.db.cursor.execute('''
                SELECT COUNT(*) as total_sales, 
                       SUM(total_amount) as total_sales_amount,
                       SUM(paid_amount) as total_paid,
                       SUM(balance_amount) as total_balance
                FROM sales 
                WHERE strftime('%Y-%m', date) = ?
            ''', (month_str,))
            
            sales_result = self.db.cursor.fetchone()
            total_sales = sales_result[0] or 0
            total_sales_amount = sales_result[1] or 0
            total_paid = sales_result[2] or 0
            total_balance = sales_result[3] or 0
            
            # Get purchases for the month
            self.db.cursor.execute('''
                SELECT COUNT(*) as total_purchases, 
                       SUM(total_amount) as total_purchases_amount
                FROM purchases 
                WHERE strftime('%Y-%m', date) = ?
            ''', (month_str,))
            
            purchases_result = self.db.cursor.fetchone()
            total_purchases = purchases_result[0] or 0
            total_purchases_amount = purchases_result[1] or 0
            
            # Get daily sales trend
            self.db.cursor.execute('''
                SELECT DATE(date) as sale_date, 
                       COUNT(*) as daily_sales,
                       SUM(total_amount) as daily_amount
                FROM sales 
                WHERE strftime('%Y-%m', date) = ?
                GROUP BY DATE(date)
                ORDER BY sale_date
            ''', (month_str,))
            
            daily_sales = self.db.cursor.fetchall()
            
            # Get category-wise sales
            self.db.cursor.execute('''
                SELECT p.category, 
                       SUM(si.quantity) as total_quantity,
                       SUM(si.total) as total_amount
                FROM sale_items si
                JOIN sales s ON si.sale_id = s.id
                JOIN products p ON si.product_name = p.name
                WHERE strftime('%Y-%m', s.date) = ?
                AND p.category IS NOT NULL
                GROUP BY p.category
                ORDER BY total_amount DESC
            ''', (month_str,))
            
            category_sales = self.db.cursor.fetchall()
            
            # Generate report
            month_name = self.month_combo.get()
            report = "=" * 60 + "\n"
            report += f"{'मासिक अहवाल':^60}\n"
            report += f"{'महिना: ' + month_name + ' ' + str(year):^60}\n"
            report += "=" * 60 + "\n\n"
            
            report += f"📊 एकूण विक्री: {total_sales}\n"
            report += f"💰 विक्री रक्कम: ₹{total_sales_amount:,.2f}\n"
            report += f"💳 जमा रक्कम: ₹{total_paid:,.2f}\n"
            report += f"📈 उर्वरित रक्कम: ₹{total_balance:,.2f}\n\n"
            
            report += f"🛒 एकूण खरेदी: {total_purchases}\n"
            report += f"💰 खरेदी रक्कम: ₹{total_purchases_amount:,.2f}\n\n"
            
            report += f"📈 निव्वळ उत्पन्न: ₹{total_paid - total_purchases_amount:,.2f}\n\n"
            
            if daily_sales:
                report += "📅 दैनंदिन विक्री ट्रेंड:\n"
                report += "-" * 60 + "\n"
                report += f"{'तारीख':<15} {'विक्री':<10} {'रक्कम':<15}\n"
                report += "-" * 60 + "\n"
                
                for daily in daily_sales:
                    sale_date, daily_count, daily_amount = daily
                    report += f"{sale_date:<15} {daily_count:<10} ₹{daily_amount:,.2f}\n"
                
                report += "\n"
            
            if category_sales:
                report += "🏷️ कॅटेगरी-वार विक्री:\n"
                report += "-" * 60 + "\n"
                report += f"{'कॅटेगिरी':<25} {'नग':<10} {'रक्कम':<15}\n"
                report += "-" * 60 + "\n"
                
                for category in category_sales:
                    cat_name, quantity, amount = category
                    if cat_name:
                        report += f"{cat_name[:23]:<25} {quantity:<10} ₹{amount:,.2f}\n"
            
            self.monthly_report_text.insert(1.0, report)
            
        except Exception as e:
            messagebox.showerror("त्रुटी", f"अहवाल तयार करताना त्रुटी: {str(e)}")
    
    def generate_credit_report(self):
        """Generate credit report"""
        report_type = self.credit_type_combo.get()
        
        self.credit_report_text.delete(1.0, tk.END)
        
        try:
            report = "=" * 60 + "\n"
            report += f"{'उधारी अहवाल':^60}\n"
            report += f"{'तारीख: ' + datetime.now().strftime('%d/%m/%Y'):^60}\n"
            report += "=" * 60 + "\n\n"
            
            if report_type in ['ग्राहक उधारी', 'सर्व उधारी']:
                # Get customer credits
                self.db.cursor.execute('''
                    SELECT name, credit_balance, phone
                    FROM customers 
                    WHERE credit_balance > 0 
                    AND name NOT LIKE 'CUST-%'
                    ORDER BY credit_balance DESC
                ''')
                
                customers = self.db.cursor.fetchall()
                
                if customers:
                    report += "👥 ग्राहक उधारी:\n"
                    report += "-" * 60 + "\n"
                    report += f"{'नाव':<25} {'फोन':<15} {'उधारी':<15}\n"
                    report += "-" * 60 + "\n"
                    
                    total_customer_credit = 0
                    for customer in customers:
                        name, credit, phone = customer
                        report += f"{name[:23]:<25} {phone[:13] if phone else '-':<15} ₹{credit:,.2f}\n"
                        total_customer_credit += credit
                    
                    report += "-" * 60 + "\n"
                    report += f"{'एकूण ग्राहक उधारी:':<40} ₹{total_customer_credit:,.2f}\n\n"
                else:
                    report += "👥 ग्राहक उधारी: कोणतीही उधारी नाही\n\n"
            
            if report_type in ['पुरवठादार उधारी', 'सर्व उधारी']:
                # Get supplier credits
                self.db.cursor.execute('''
                    SELECT name, credit_balance, phone
                    FROM suppliers 
                    WHERE credit_balance > 0
                    ORDER BY credit_balance DESC
                ''')
                
                suppliers = self.db.cursor.fetchall()
                
                if suppliers:
                    report += "🏭 पुरवठादार उधारी:\n"
                    report += "-" * 60 + "\n"
                    report += f"{'नाव':<25} {'फोन':<15} {'उधारी':<15}\n"
                    report += "-" * 60 + "\n"
                    
                    total_supplier_credit = 0
                    for supplier in suppliers:
                        name, credit, phone = supplier
                        report += f"{name[:23]:<25} {phone[:13] if phone else '-':<15} ₹{credit:,.2f}\n"
                        total_supplier_credit += credit
                    
                    report += "-" * 60 + "\n"
                    report += f"{'एकूण पुरवठादार उधारी:':<40} ₹{total_supplier_credit:,.2f}\n\n"
                else:
                    report += "🏭 पुरवठादार उधारी: कोणतीही उधारी नाही\n\n"
            
            if report_type == 'सर्व उधारी':
                # Calculate total credit
                total_credit = 0
                
                self.db.cursor.execute("SELECT SUM(credit_balance) FROM customers WHERE name NOT LIKE 'CUST-%'")
                customer_total = self.db.cursor.fetchone()[0] or 0
                
                self.db.cursor.execute("SELECT SUM(credit_balance) FROM suppliers")
                supplier_total = self.db.cursor.fetchone()[0] or 0
                
                total_credit = customer_total + supplier_total
                
                report += "=" * 60 + "\n"
                report += f"{'एकूण उधारी सारांश':^60}\n"
                report += "=" * 60 + "\n"
                report += f"📊 एकूण ग्राहक उधारी: ₹{customer_total:,.2f}\n"
                report += f"🏭 एकूण पुरवठादार उधारी: ₹{supplier_total:,.2f}\n"
                report += f"💰 एकूण उधारी: ₹{total_credit:,.2f}\n"
            
            self.credit_report_text.insert(1.0, report)
            
        except Exception as e:
            messagebox.showerror("त्रुटी", f"अहवाल तयार करताना त्रुटी: {str(e)}")