import sqlite3
from tkinter import *
from tkinter import messagebox
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
import csv

# Ensure receipts directory exists
if not os.path.exists('receipts'):
    os.makedirs('receipts')

# Database setup
def init_db():
    with sqlite3.connect('receipts.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS receipts (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            date TEXT NOT NULL,
                            time TEXT NOT NULL,
                            seller TEXT NOT NULL,
                            items TEXT NOT NULL,
                            total REAL NOT NULL)''')
        conn.commit()

def generate_pdf(date, time, seller, items, total, receipt_id):
    # Set the width for 2-inch thermal paper, converted to points (1 inch = 72 points)
    paper_width = 2 * 72  # 2-inch width in points (approximately 144 points)
    paper_height = 500  # Start with an estimated height (this will be dynamic)
    pdf_filename = f"receipts/receipt_{receipt_id}.pdf"
    c = canvas.Canvas(pdf_filename, pagesize=(paper_width, paper_height))

    logo_path = "https://res.cloudinary.com/dfk8mcpwf/image/upload/v1729065069/mrk_logo_wv11pa.jpg"  # Path of your logo file
    logo_width = 70  # Increased width of the logo
    logo_height = 35  # Increased height of the logo

# Center the logo horizontally by subtracting half the logo's width from half the paper's width
    x_position = (paper_width - logo_width) / 2  # Center the logo on the thermal paper
    y_position = paper_height - logo_height - 5  # 5 points from the top edge

# Draw the logo at the calculated position
    c.drawImage(logo_path, x_position, y_position, width=logo_width, height=logo_height, mask='auto')

# Header for the receipt with a larger font for "MRK EMBROIDERY"
    c.setFont("Helvetica-Bold", 12)  # Increased font size for the logo text
    c.drawString(5, paper_height - 40, "MRK EMBROIDERY")  # Adjusted y position for logo text

# Reduced font size for contact information and other text
    c.setFont("Helvetica", 8)  # Slightly larger for contact info
    c.drawString(5, paper_height - 55, "IBAYO STREET")  # Adjusted y position
    c.drawString(5, paper_height - 70, "Contact: 09050643316")  # Adjusted y position
    c.drawString(5, paper_height - 85, "--------------------------------------------------")  # Adjusted y position

# Additional details like date, time, receipt number, and cashier
    c.setFont("Helvetica", 8)
    c.drawString(5, paper_height - 100, f"Date: {date}   Time: {time}")
    c.drawString(5, paper_height - 110, f"Receipt #: {receipt_id}")
    c.drawString(5, paper_height - 120, f"Cashier: {seller}")

# Start position for items
    y_position = paper_height - 150
    c.setFont("Helvetica", 8)

# Split items and draw them with consistent spacing and formatting
    item_lines = items.split(", ")  # Assuming items are passed as a comma-separated string
    for item in item_lines:
        item_details = item.split(" ")
        item_name = " ".join(item_details[:-2])  # Join all but the last two elements for the item name
        price = float(item_details[-2])  # Second last element for price
        quantity = int(item_details[-1])  # Last element for quantity
        subtotal = price * quantity

    # Print each item detail with improved formatting
    c.drawString(5, y_position, f"Item:      {item_name}")  # Item name
    c.drawString(5, y_position - 10, f"Price:     ₱{price:.2f}")  # Price
    c.drawString(5, y_position - 20, f"Quantity:  {quantity}")  # Quantity
    c.drawString(5, y_position - 30, f"Subtotal:  ₱{subtotal:.2f}")  # Subtotal

    y_position -= 50  # Adjust line height for the next item
    if y_position < 20:  # Check if there's enough space for more items
        c.showPage()  # Start a new page if necessary
        y_position = paper_height - 20  # Reset y_position for the new page

# Line separator before total
    c.drawString(5, y_position, "--------------------------------------------------")

# Display the total amount
    c.setFont("Helvetica-Bold", 10)  # Increased font size for the total
    c.drawString(5, y_position - 10, f"Total:     ₱{total:.2f}")

# Footer information (Thank you note or additional info)
    c.setFont("Helvetica", 7)
    c.drawString(5, y_position - 30, "Thank you for your purchase!")  # Thank you message
    c.drawString(5, y_position - 40, "Please visit us again!")  # Additional info

# Save the PDF
    c.save()

# Notify the user the PDF is saved
    messagebox.showinfo("PDF Saved", f"PDF receipt saved as {pdf_filename}")

def add_receipt_to_db(date, time, seller, items, total):
    with sqlite3.connect('receipts.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO receipts (date, time, seller, items, total)
                          VALUES (?, ?, ?, ?, ?)''', (date, time, seller, items, total))
        conn.commit()
        return cursor.lastrowid  # Return the receipt ID of the inserted row

# Function to save receipt data in CSV format
def save_receipt_to_csv(date, time, seller, items, total):
    csv_filename = "receipts/receipts.csv"
    file_exists = os.path.isfile(csv_filename)
    
    with open(csv_filename, "a", newline="") as csvfile:
        fieldnames = ["Date", "Time", "Seller", "Items", "Total"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()  # Write header only if the file is new
        
        writer.writerow({
            "Date": date,
            "Time": time,
            "Seller": seller,
            "Items": items,
            "Total": f"{total:.2f}"
        })

def calculate_total(event=None):
    try:
        price = float(entry_price.get())
        quantity = int(entry_quantity.get())
        subtotal = price * quantity
        entry_total.delete(0, END)
        entry_total.insert(0, f"{subtotal:.2f}")
    except ValueError:
        entry_total.delete(0, END)
        entry_total.insert(0, "Invalid input")

def add_product():
    product_name = entry_product_name.get().strip()
    price = entry_price.get().strip()
    quantity = entry_quantity.get().strip()

    if product_name and price and quantity:
        try:
            subtotal = float(price) * int(quantity)
            item_entry = f"{product_name} {price} {quantity}"
            listbox_items.insert(END, item_entry)  # Add product to the list
            calculate_total_receipt()  # Recalculate the total
            entry_product_name.delete(0, END)  # Clear the input fields
            entry_price.delete(0, END)
            entry_quantity.delete(0, END)
        except ValueError:
            messagebox.showerror("Invalid Input", "Price and quantity must be valid numbers.")
    else:
        messagebox.showerror("Missing Fields", "Please fill in all fields.")

def calculate_total_receipt():
    total = 0
    for item in listbox_items.get(0, END):
        price = float(item.split()[-2])  # Get the price from the item string
        quantity = int(item.split()[-1])  # Get the quantity from the item string
        subtotal = price * quantity
        total += subtotal
    entry_total.delete(0, END)
    entry_total.insert(0, f"{total:.2f}")

def submit_receipt():
    date = entry_date.get().strip()
    time = entry_time.get().strip()
    seller = entry_seller.get().strip()
    total = entry_total.get().strip()

    if date and time and seller and total:
        items = ', '.join(listbox_items.get(0, END))  # Join all items in the list
        try:
            total = float(total.replace(',', ''))  # Convert total to float
            receipt_id = add_receipt_to_db(date, time, seller, items, total)  # Save receipt to the database
            save_receipt_to_csv(date, time, seller, items, total)  # Save receipt to CSV file
            generate_pdf(date, time, seller, items, total, receipt_id)  # Generate PDF receipt
        except ValueError:
            messagebox.showerror("Invalid Input", "Total must be a valid number. Please check your input.")
    else:
        messagebox.showerror("Missing Fields", "Please fill in all fields.")

def view_receipts():
    with sqlite3.connect('receipts.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM receipts")
        rows = cursor.fetchall()

    view_window = Toplevel()
    view_window.title("All Receipts")

    if rows:
        for row in rows:
            Label(view_window, text=f"ID: {row[0]}, Date: {row[1]}, Time: {row[2]}, Seller: {row[3]}, Items: {row[4]}, Total: {row[5]}").pack()
    else:
        Label(view_window, text="No receipts found.").pack()

# Initialize database
init_db()

# Setup Tkinter GUI
root = Tk()
root.title("Receipt Management System")

Label(root, text="Date (MM/DD/YYYY)").grid(row=0, column=0)
entry_date = Entry(root)
entry_date.grid(row=0, column=1)

Label(root, text="Time (HH:MM)").grid(row=1, column=0)
entry_time = Entry(root)
entry_time.grid(row=1, column=1)

Label(root, text="Seller").grid(row=2, column=0)
entry_seller = Entry(root)
entry_seller.grid(row=2, column=1)

Label(root, text="Product Name").grid(row=3, column=0)
entry_product_name = Entry(root)
entry_product_name.grid(row=3, column=1)

Label(root, text="Price per item").grid(row=4, column=0)
entry_price = Entry(root)
entry_price.grid(row=4, column=1)

Label(root, text="Quantity").grid(row=5, column=0)
entry_quantity = Entry(root)
entry_quantity.grid(row=5, column=1)

# Button to add product to the list
add_product_button = Button(root, text="Add Product", command=add_product)
add_product_button.grid(row=6, column=0, pady=10)

# Listbox to show added products
listbox_items = Listbox(root, width=50)
listbox_items.grid(row=7, columnspan=2)

Label(root, text="Total Amount").grid(row=8, column=0)
entry_total = Entry(root)
entry_total.grid(row=8, column=1)

# Buttons for submitting and viewing receipts
submit_button = Button(root, text="Submit Receipt", command=submit_receipt)
submit_button.grid(row=9, column=0, pady=10)

view_button = Button(root, text="View Receipts", command=view_receipts)
view_button.grid(row=9, column=1, pady=10)

root.mainloop()
