import sqlite3
import tkinter as tk
from tkinter import messagebox, simpledialog, font
import os

# ===== Database Setup =====
def init_db():
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()

    # Create user table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')

    # Create products table (with min_required column)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            price REAL,
            quantity INTEGER,
            min_required INTEGER
        )
    ''')

    # Ensure default admin user exists
    cursor.execute("SELECT * FROM users WHERE username='vishwas'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (username, password, role) VALUES ('vishwas', 'admin', 'admin')")

    # Insert default products only if empty
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        products = [
            ("Mouse", "Electronics", 500, 25, 10),
            ("Notebook", "Stationery", 50, 5, 10),
            ("Pen", "Stationery", 10, 3, 5),
            ("Printer", "Electronics", 15000, 8, 4),
            ("Chair", "Furniture", 1200, 12, 6),
            ("Table", "Furniture", 3000, 2, 5),
            ("Keyboard", "Electronics", 800, 20, 5),
            ("Stapler", "Stationery", 120, 1, 3),
        ]
        cursor.executemany("INSERT INTO products (name, category, price, quantity, min_required) VALUES (?, ?, ?, ?, ?)", products)

    conn.commit()
    conn.close()

def login(username, password):
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

# ===== Product Functions =====
def add_product(name, category, price, quantity, min_required):
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (name, category, price, quantity, min_required) VALUES (?, ?, ?, ?, ?)",
                   (name, category, price, quantity, min_required))
    conn.commit()
    conn.close()

def view_products():
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()
    return products

def delete_product(product_id):
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE product_id=?", (product_id,))
    conn.commit()
    conn.close()

def edit_product(product_id, name, category, price, quantity, min_required):
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET name=?, category=?, price=?, quantity=?, min_required=? WHERE product_id=?",
                   (name, category, price, quantity, min_required, product_id))
    conn.commit()
    conn.close()

def low_stock():
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE quantity <= min_required")
    low = cursor.fetchall()
    conn.close()
    return low

# ===== GUI Application =====
class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory Management System")
        self.root.geometry("950x850")
        self.root.configure(bg="#f0f0ff")
        self.title_font = font.Font(family="Times New Roman", size=22, weight="bold")
        self.button_font = font.Font(size=20)
        self.label_font = font.Font(size=18)
        self.login_screen()

    def center_text(self, text):
        label = tk.Label(self.root, text=text, font=self.title_font, fg="#2c3e50", bg="#f0f0ff")
        label.pack(pady=30)

    def login_screen(self):
        self.clear_screen()
        self.center_text("Login to Inventory System")
        tk.Label(self.root, text="Username:", bg="#f0f0ff").pack()
        self.username = tk.Entry(self.root)
        self.username.pack()
        tk.Label(self.root, text="Password:", bg="#f0f0ff").pack()
        self.password = tk.Entry(self.root, show="*")
        self.password.pack()
        tk.Button(self.root, text="Login", command=self.authenticate, font=self.button_font, bg="#4caf50", fg="white").pack(pady=20)

    def authenticate(self):
        user = login(self.username.get(), self.password.get())
        if user:
            self.user = user
            self.main_menu()
        else:
            messagebox.showerror("Error", "Invalid credentials")

    def confirm_password(self):
        pwd = simpledialog.askstring("Password Required", "Re-enter your password:", show="*")
        if pwd != self.user[1]:
            messagebox.showerror("Error", "Incorrect password!")
            return False
        return True

    def main_menu(self):
        self.clear_screen()
        self.center_text(f"Welcome, {self.user[0].capitalize()} ({self.user[2].capitalize()})")
        tk.Button(self.root, text="View Products", command=self.view_products, font=self.button_font, bg="#2196f3", fg="white").pack(pady=12)
        tk.Button(self.root, text="Add Product", command=self.add_product, font=self.button_font, bg="#9c27b0", fg="white").pack(pady=12)
        tk.Button(self.root, text="Low Stock Alerts", command=self.low_stock_alerts, font=self.button_font, bg="#ff5722", fg="white").pack(pady=12)
        tk.Button(self.root, text="Generate Inventory Report", command=self.generate_report, font=self.button_font, bg="#795548", fg="white").pack(pady=12)
        tk.Button(self.root, text="Logout", command=self.login_screen, font=self.button_font, bg="#607d8b", fg="white").pack(pady=16)

    def view_products(self):
        self.clear_screen()
        self.center_text("All Products")
        canvas = tk.Canvas(self.root, bg="#f0f0ff", height=200, width=500)
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="#f0f0ff")
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True, padx=10)
        scrollbar.pack(side="right", fill="y")

        products = view_products()
        for prod in products:
            text = f"ID:{prod[0]} | {prod[1]} ({prod[2]}) - Rs.{prod[3]} | Qty: {prod[4]}"
            tk.Label(scroll_frame, text=text, font=self.label_font, bg="#f0f0ff").pack(pady=10)
            tk.Button(scroll_frame, text="Edit", command=lambda p=prod: self.edit_product(p), bg="#4caf50", fg="white").pack(pady=5)
            tk.Button(scroll_frame, text="Delete", command=lambda pid=prod[0]: self.delete_product(pid), bg="#f44336", fg="white").pack(pady=5)
            tk.Label(scroll_frame, text="-----------------------------", bg="#f0f0ff").pack()

        tk.Button(self.root, text="Back", command=self.main_menu, font=self.button_font, bg="#607d8b", fg="white").pack(pady=20)

    def delete_product(self, product_id):
        if not self.confirm_password():
            return
        delete_product(product_id)
        messagebox.showinfo("Deleted", "Product deleted successfully.")
        self.view_products()

    def edit_product(self, prod):
        self.clear_screen()
        self.center_text("Edit Product")
        entries = {}
        fields = ['Name', 'Category', 'Price', 'Quantity', 'Min Required']
        values = [prod[1], prod[2], prod[3], prod[4], prod[5]]
        for i, field in enumerate(fields):
            tk.Label(self.root, text=field, bg="#f0f0ff").pack()
            e = tk.Entry(self.root)
            e.insert(0, str(values[i]))
            e.pack()
            entries[field] = e

        def save_changes():
            if not self.confirm_password():
                return
            try:
                edit_product(
                    prod[0],
                    entries['Name'].get(),
                    entries['Category'].get(),
                    float(entries['Price'].get()),
                    int(entries['Quantity'].get()),
                    int(entries['Min Required'].get())
                )
                messagebox.showinfo("Success", "Product updated!")
                self.view_products()
            except:
                messagebox.showerror("Error", "Invalid input!")

        tk.Button(self.root, text="Save", command=save_changes, bg="#2196f3", fg="white").pack(pady=15)
        tk.Button(self.root, text="Back", command=self.view_products, bg="#607d8b", fg="white").pack(pady=15)

    def add_product(self):
        self.clear_screen()
        self.center_text("Add New Product")
        entries = {}
        for field in ['Name', 'Category', 'Price', 'Quantity', 'Min Required']:
            tk.Label(self.root, text=field, bg="#f0f0ff").pack()
            e = tk.Entry(self.root)
            e.pack()
            entries[field] = e

        def save():
            if not self.confirm_password():
                return
            try:
                add_product(
                    entries['Name'].get(),
                    entries['Category'].get(),
                    float(entries['Price'].get()),
                    int(entries['Quantity'].get()),
                    int(entries['Min Required'].get())
                )
                messagebox.showinfo("Success", "Product Added!")
                self.main_menu()
            except:
                messagebox.showerror("Error", "Invalid input!")

        tk.Button(self.root, text="Save", command=save, bg="#4caf50", fg="white").pack(pady=15)
        tk.Button(self.root, text="Back", command=self.main_menu, bg="#607d8b", fg="white").pack(pady=15)

    def generate_report(self):
        self.clear_screen()
        self.center_text("Inventory Summary Report")
        products = view_products()
        headings = "ID | Name | Category | Price | Qty | Min Req | Status"
        tk.Label(self.root, text=headings, font=self.label_font, bg="#cfd8dc").pack()
        for p in products:
            status = "LOW" if p[4] <= p[5] else "OK"
            line = f"{p[0]} | {p[1]} | {p[2]} | Rs.{p[3]} | {p[4]} | {p[5]} | {status}"
            fg = "#c62828" if status == "LOW" else "#2e7d32"
            tk.Label(self.root, text=line, font=self.label_font, fg=fg, bg="#f0f0ff").pack()
        tk.Button(self.root, text="Back", command=self.main_menu, font=self.button_font, bg="#607d8b", fg="white").pack(pady=20)

    def low_stock_alerts(self):
        self.clear_screen()
        self.center_text("Low Stock Products")
        low = low_stock()
        if low:
            for item in low:
                text = f"{item[1]} - Qty: {item[4]} (Min: {item[5]})"
                tk.Label(self.root, text=text, font=self.label_font, fg="#e53935", bg="#f0f0ff").pack()
        else:
            tk.Label(self.root, text="All items are above minimum level", font=self.label_font, bg="#f0f0ff").pack()
        tk.Button(self.root, text="Back", command=self.main_menu, font=self.button_font, bg="#607d8b", fg="white").pack(pady=20)

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

# Run App
init_db()
root = tk.Tk()
app = InventoryApp(root)
root.mainloop()
