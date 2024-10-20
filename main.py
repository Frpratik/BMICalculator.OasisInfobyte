import tkinter as tk
from tkinter import messagebox
import sqlite3
import matplotlib.pyplot as plt
import csv
import os

# Database setup
def setup_database():
    conn = sqlite3.connect('bmi_calculator.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bmi_data (
            id INTEGER PRIMARY KEY,
            user_name TEXT,
            weight REAL,
            height REAL,
            bmi REAL,
            category TEXT
        )
    ''')
    conn.commit()
    conn.close()

# BMI calculation
def calculate_bmi(weight, height):
    return weight / (height ** 2)

# BMI category determination
def get_bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif 18.5 <= bmi < 24.9:
        return "Normal weight"
    elif 25 <= bmi < 29.9:
        return "Overweight"
    else:
        return "Obesity"

# Save BMI data to the database
def save_data(weight, height, bmi, category, user_name):
    conn = sqlite3.connect('bmi_calculator.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO bmi_data (user_name, weight, height, bmi, category) VALUES (?, ?, ?, ?, ?)', 
                   (user_name, weight, height, bmi, category))
    conn.commit()
    conn.close()

# Calculate and display BMI
def calculate_and_display():
    try:
        weight = float(weight_entry.get())
        height = float(height_entry.get())
        user_name = user_name_entry.get().strip()  # Get user name and strip spaces
        
        if weight <= 0 or height <= 0:
            raise ValueError("Weight and height must be positive numbers.")

        bmi = calculate_bmi(weight, height)
        category = get_bmi_category(bmi)
        
        save_data(weight, height, bmi, category, user_name)
        
        result_label.config(text=f"{user_name}, your BMI: {bmi:.2f}, Category: {category}")
        
    except ValueError as e:
        messagebox.showerror("Input Error", str(e))

# View historical BMI data
def view_history():
    conn = sqlite3.connect('bmi_calculator.db')
    cursor = conn.cursor()
    cursor.execute('SELECT user_name, weight, height, bmi, category FROM bmi_data')
    records = cursor.fetchall()
    conn.close()
    
    if not records:
        messagebox.showinfo("History", "No records found.")
        return
    
    # Prepare data for plotting
    user_names = list(set(record[0] for record in records))
    bmis = {user: [] for user in user_names}
    
    for record in records:
        bmis[record[0]].append(record[3])  # Append BMI for each user

    plt.figure(figsize=(10, 5))
    for user in user_names:
        plt.plot(bmis[user], marker='o', label=user)
        
    plt.title("BMI History", fontsize=16)
    plt.xlabel("Entry Number", fontsize=12)
    plt.ylabel("BMI", fontsize=12)
    plt.xticks(range(len(bmis[user_names[0]])), range(1, len(bmis[user_names[0]]) + 1))
    plt.grid()
    plt.legend()
    plt.show()

# Export historical data to CSV
def export_to_csv():
    conn = sqlite3.connect('bmi_calculator.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM bmi_data')
    records = cursor.fetchall()
    conn.close()
    
    if not records:
        messagebox.showinfo("Export", "No records to export.")
        return
    
    filename = "bmi_data.csv"
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['ID', 'User Name', 'Weight (kg)', 'Height (m)', 'BMI', 'Category'])
        writer.writerows(records)
    
    messagebox.showinfo("Export", f"Data exported successfully to {filename}.")

# Create the main window
root = tk.Tk()
root.title("BMI Calculator")
root.geometry("400x400")
root.config(bg="#f0f0f0")

# Frame for the input fields
input_frame = tk.Frame(root, bg="#ffffff", padx=20, pady=20)
input_frame.pack(pady=20)

# Title label
title_label = tk.Label(root, text="BMI Calculator", font=("Helvetica", 18), bg="#f0f0f0", fg="#333333")
title_label.pack(pady=10)

# User identification
tk.Label(input_frame, text="User Name:", font=("Helvetica", 12), bg="#ffffff").grid(row=0, column=0)
user_name_entry = tk.Entry(input_frame, font=("Helvetica", 12))
user_name_entry.grid(row=0, column=1, padx=10)

# Input fields
tk.Label(input_frame, text="Weight (kg):", font=("Helvetica", 12), bg="#ffffff").grid(row=1, column=0)
weight_entry = tk.Entry(input_frame, font=("Helvetica", 12))
weight_entry.grid(row=1, column=1, padx=10)

tk.Label(input_frame, text="Height (m):", font=("Helvetica", 12), bg="#ffffff").grid(row=2, column=0)
height_entry = tk.Entry(input_frame, font=("Helvetica", 12))
height_entry.grid(row=2, column=1, padx=10)

# Result label
result_label = tk.Label(root, text="", font=("Helvetica", 12), bg="#f0f0f0", fg="#333333")
result_label.pack(pady=10)

# Buttons
button_frame = tk.Frame(root, bg="#f0f0f0")
button_frame.pack(pady=10)

calculate_button = tk.Button(button_frame, text="Calculate BMI", command=calculate_and_display, 
                              font=("Helvetica", 12), bg="#007bff", fg="white", padx=10)
calculate_button.grid(row=0, column=0, padx=10)

history_button = tk.Button(button_frame, text="View History", command=view_history, 
                           font=("Helvetica", 12), bg="#28a745", fg="white", padx=10)
history_button.grid(row=0, column=1, padx=10)

export_button = tk.Button(button_frame, text="Export to CSV", command=export_to_csv, 
                          font=("Helvetica", 12), bg="#ffc107", fg="black", padx=10)
export_button.grid(row=0, column=2, padx=10)

# Initialize the database
setup_database()

# Start the GUI main loop
root.mainloop()
