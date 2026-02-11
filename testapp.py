# test_app.py
import tkinter as tk
from tkinter import ttk
from database import DatabaseManager

class TestApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Test App")
        self.root.geometry("1400x750")
        
        self.db = DatabaseManager()
        self.setup_ui()
    
    def setup_ui(self):
        # Create notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Simple dashboard
        tab1 = tk.Frame(self.notebook, bg='lightblue')
        tk.Label(tab1, text="डॅशबोर्ड", font=('Arial', 20)).pack(pady=20)
        tk.Label(tab1, text="हा एक साधा डॅशबोर्ड आहे").pack()
        self.notebook.add(tab1, text="डॅशबोर्ड")
        
        # Tab 2: Sales
        tab2 = tk.Frame(self.notebook, bg='lightgreen')
        tk.Label(tab2, text="नवीन विक्री", font=('Arial', 20)).pack(pady=20)
        tk.Label(tab2, text="विक्री येथे करा").pack()
        self.notebook.add(tab2, text="नवीन विक्री")
        
        # Tab 3: Purchases
        tab3 = tk.Frame(self.notebook, bg='lightyellow')
        tk.Label(tab3, text="नवीन खरेदी", font=('Arial', 20)).pack(pady=20)
        tk.Label(tab3, text="खरेदी येथे करा").pack()
        self.notebook.add(tab3, text="नवीन खरेदी")
        
        # Tab 4: Stock
        tab4 = tk.Frame(self.notebook, bg='lightpink')
        tk.Label(tab4, text="स्टॉक व्यवस्थापन", font=('Arial', 20)).pack(pady=20)
        tk.Label(tab4, text="स्टॉक व्यवस्थापन येथे करा").pack()
        self.notebook.add(tab4, text="स्टॉक व्यवस्थापन")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = TestApp()
    app.run()