from tkinter import ttk,messagebox
from customtkinter import *
from PIL import Image, ImageTk
import database
import csv
from tkinter import filedialog
from openpyxl import Workbook
import os
import sys
import subprocess
from datetime import datetime

set_appearance_mode("light")

# # # # # # # # # # # # # # # # # # # # # function part start # # # # # # # # # # # # # # # # # # # # #
def only_numbers(value):
    return value.isdigit() or value == ""

def only_10_digits(value):
    return value.isdigit() and len(value) <= 10 or value == ""

def salary_validation(value):
    if value == "":
        return True
    try:
        float(value)
        return True
    except ValueError:
        return False

def change_theme():
    if theme_switch.get() == 1:
        set_appearance_mode("dark")
    else:
        set_appearance_mode("light")

def export_csv():
    employees = tree.get_children()

    if not employees:
        messagebox.showwarning(
            "Export",
            "There is no employee data to export."
        )
        return

    file_path = filedialog.asksaveasfilename(
        title="Save Employee Data",
        defaultextension=".csv",
        initialfile="employees.csv",
        filetypes=[
            ("CSV Files (*.csv)", "*.csv"),
            ("All Files (*.*)", "*.*")
        ]
    )

    if not file_path:
        return

    with open(file_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow([
            "Id",
            "Name",
            "Phone",
            "Role",
            "Gender",
            "Salary"
        ])

        for employee in employees:
            writer.writerow(tree.item(employee)["values"])

    messagebox.showinfo(
        "Export Successful",
        "Employee data exported to CSV successfully."
    )

def export_excel():
    employees = tree.get_children()

    if not employees:
        messagebox.showwarning(
            "Export",
            "There is no employee data to export."
        )
        return

    file_path = filedialog.asksaveasfilename(
        title="Save Employee Data",
        defaultextension=".xlsx",
        initialfile="employees.xlsx",
        filetypes=[
            ("Excel Files (*.xlsx)", "*.xlsx"),
            ("All Files (*.*)", "*.*")
        ]
    )

    if not file_path:
        return

    workbook = Workbook()
    worksheet = workbook.active

    if worksheet is None:
        return

    worksheet.title = "Employees"

    headers = [
        "Id",
        "Name",
        "Phone",
        "Role",
        "Gender",
        "Salary"
    ]

    worksheet.append(headers)

    for employee in employees:
        employee_data = tree.item(employee, "values")
        worksheet.append(list(employee_data))

    workbook.save(file_path)

    messagebox.showinfo(
        "Export Successful",
        "Employee data exported to Excel successfully."
    )

def export_data():
    if exportBox.get() == "CSV":
        export_csv()
    elif exportBox.get() == "Excel":
        export_excel()
    else:
        pass

def log_out():

    result = messagebox.askyesno(
        "Confirm",
        "Are you sure you want to log out?"
    )

    if result:

        messagebox.showinfo(
            "Success",
            "Logged out successfully"
        )

        # Get the full path of login.py
        login_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "login.py"
        )

        # Open login.py BEFORE closing the EMS window
        subprocess.Popen(
            [sys.executable, login_path],
            cwd=os.path.dirname(os.path.abspath(__file__))
        )

        # Now close EMS
        window.destroy()

def open_dashboard():
    import dashboard
    dashboard.open_dashboard(window, tree)


def open_ask_ai():
    import askAI
    askAI.open_ask_ai(window)

def search_employee():
    if searchEntry.get() == "":
        messagebox.showerror("Error","Please enter a value to search")
    elif searchBox.get() == "Search By":
        messagebox.showerror("Error","Please select an option to search")
    else:
        searched_employee_data=database.search_employee(searchBox.get(), searchEntry.get())
        tree.delete(*tree.get_children())
        for employee in searched_employee_data:
            tree.insert("", "end", values=employee)

def treeview_data():
    all_employees=database.fetch_employees()
    tree.delete(*tree.get_children())
    for employee in all_employees:
        tree.insert("","end",values=employee)

def showall_employee():
    treeview_data()
    searchEntry.delete(0, "end")
    searchBox.set("Search By")

def delete_all_employee():

    result = messagebox.askyesno(
        title="Confirm",
        message=(
            "Are you sure you want to delete ALL employees? "
            "All deleted employees will be moved to "
            "Restore Employee so they can be restored later."
        )
    )

    if not result:
        return

    employees = database.fetch_employees()

    if not employees:
        messagebox.showwarning(
            "Delete All",
            "There are no employees to delete."
        )
        return

    deleted_count = 0

    for employee in employees:
        employee_id = employee[0]

        try:
            deleted = database.delete(employee_id)

            if deleted:
                deleted_count += 1

        except Exception as e:
            messagebox.showerror(
                "Delete All Error",
                f"Could not delete employee {employee_id}.{e}"
            )

    # Refresh main employee table
    treeview_data()

    # Clear search controls
    searchEntry.delete(0, "end")
    searchBox.set("Search By")

    # Clear form
    clear(True)

    if deleted_count == len(employees):
        messagebox.showinfo(
            "Delete All Successful",
            f"{deleted_count} employee records were deleted. "
            "All deleted employees are now available in "
            "Restore Employee."
        )
    else:
        messagebox.showwarning(
            "Delete All Completed",
            f"{deleted_count} of {len(employees)} employees were deleted. "
            "The deleted employees are available in Restore Employee."
        )

def delete_employee():

    selected_item = tree.selection()

    if not selected_item:

        messagebox.showwarning(
            "Delete Employee",
            "Please select an employee to delete."
        )

        return

    employee_id = idEntry.get()

    result = messagebox.askyesno(
        "Confirm Delete",
        f"Are you sure you want to delete employee {employee_id}?"
    )

    if result:

        deleted = database.delete(employee_id)

        if deleted:

            treeview_data()
            clear(True)

            messagebox.showinfo(
                "Success",
                "Employee deleted successfully. "
                "You can restore this employee using "
                "'Restore Employee'."
            )

def restore_employee_window():

    restore_window = CTkToplevel(window)

    restore_window.title("Restore Employee")
    restore_window.geometry("850x500")
    restore_window.resizable(False, False)

    restore_window.transient(window)
    restore_window.grab_set()

    title = CTkLabel(
        restore_window,
        text="RESTORE DELETED EMPLOYEE",
        font=("Arial", 22, "bold"),
        text_color=("#174A7E", "#4DA6FF")
    )

    title.pack(pady=(20, 5))

    subtitle = CTkLabel(
        restore_window,
        text="Select an employee and click Restore",
        font=("Arial", 12),
        text_color=("#6B7280", "#B8B8B8")
    )

    subtitle.pack(pady=(0, 15))

    restore_tree = ttk.Treeview(
        restore_window,
        columns=(
            "Id",
            "Name",
            "Phone",
            "Role",
            "Gender",
            "Salary",
            "Deleted At"
        ),
        show="headings",
        height=14
    )

    headings = {
        "Id": "ID",
        "Name": "Name",
        "Phone": "Phone",
        "Role": "Role",
        "Gender": "Gender",
        "Salary": "Salary",
        "Deleted At": "Deleted At"
    }

    widths = {
        "Id": 80,
        "Name": 120,
        "Phone": 110,
        "Role": 140,
        "Gender": 80,
        "Salary": 100,
        "Deleted At": 160
    }

    for column in headings:

        restore_tree.heading(
            column,
            text=headings[column]
        )

        restore_tree.column(
            column,
            width=widths[column],
            anchor="center"
        )

    # Restore action bar

    action_frame = CTkFrame(
        restore_window,
        height=70,
        fg_color="transparent"
    )
    action_frame.pack(
        side="bottom",
        fill="x",
        padx=20,
        pady=(5, 15)
    )
    action_frame.pack_propagate(False)

    # Center the action buttons as a group.
    button_container = CTkFrame(
        action_frame,
        fg_color="transparent"
    )
    button_container.place(
        relx=0.5,
        rely=0.5,
        anchor="center"
    )

    # Treeview
    restore_tree.pack(
        padx=20,
        pady=(5, 5),
        fill="both",
        expand=True
    )

    def load_deleted_employees():

        restore_tree.delete(
            *restore_tree.get_children()
        )

        deleted_employees = database.fetch_deleted_employees()

        for employee in deleted_employees:

            restore_tree.insert(
                "",
                "end",
                values=employee
            )

    def restore_all_employees():

        deleted_employees = database.fetch_deleted_employees()

        if not deleted_employees:
            messagebox.showinfo(
                "Restore All",
                "There are no deleted employees to restore."
            )
            return

        result = messagebox.askyesno(
            "Confirm Restore All",
            f"Restore all {len(deleted_employees)} deleted employees? "
            "All available deleted employee records will be restored "
            "to the employee database."
        )

        if not result:
            return

        restored_count = 0
        failed_count = 0

        # Restore Employee button.
        for employee in deleted_employees:
            employee_id = employee[0]

            try:
                restored = database.restore_employee(employee_id)

                if restored:
                    restored_count += 1
                else:
                    failed_count += 1

            except Exception:
                failed_count += 1

        # Refresh both tables
        load_deleted_employees()
        treeview_data()

        # Clear the employee form
        clear(True)

        if failed_count == 0:
            messagebox.showinfo(
                "Restore All Successful",
                f"{restored_count} employee records have been restored "
                "successfully."
            )
        else:
            messagebox.showwarning(
                "Restore All Completed",
                f"{restored_count} employee records restored. "
                f"{failed_count} record(s) could not be restored."
            )

    # Restore selected employee
    def restore_selected():

        selected = restore_tree.selection()

        if not selected:

            messagebox.showwarning(
                "Restore Employee",
                "Please select an employee to restore."
            )

            return

        values = restore_tree.item(
            selected[0],
            "values"
        )

        employee_id = values[0]

        result = messagebox.askyesno(
            "Confirm Restore",
            f"Restore employee {employee_id}?"
        )

        if result:

            restored = database.restore_employee(
                employee_id
            )

            if restored:

                load_deleted_employees()
                treeview_data()

                messagebox.showinfo(
                    "Success",
                    "Employee restored successfully."
                )

    # Restore Employee Button
    restore_button = CTkButton(
        button_container,
        text="Restore Employee",
        command=restore_selected,
        width=170,
        height=42,
        corner_radius=8,
        font=("Arial", 13, "bold"),
        fg_color=("#16A34A", "#22C55E"),
        hover_color=("#15803D", "#16A34A")
    )

    restore_button.pack(
        side="left",
        padx=(0, 8),
        pady=10
    )

    # Restore All Employee Button
    restore_all_button = CTkButton(
        button_container,
        text="Restore All",
        command=restore_all_employees,
        width=130,
        height=42,
        corner_radius=8,
        font=("Arial", 13, "bold"),
        fg_color=("#2563EB", "#3B82F6"),
        hover_color=("#1D4ED8", "#2563EB")
    )

    restore_all_button.pack(
        side="left",
        padx=8,
        pady=10
    )

    # Close Button
    close_button = CTkButton(
        button_container,
        text="Close",
        command=restore_window.destroy,
        width=100,
        height=42,
        corner_radius=8,
        font=("Arial", 13, "bold"),
        fg_color=("#64748B", "#475569"),
        hover_color=("#475569", "#64748B")
    )

    close_button.pack(
        side="left",
        padx=8,
        pady=10
    )

    load_deleted_employees()

def update_employee():
    selected_item=tree.selection()
    if not selected_item:
        print("Error Please select an employee to update")
    else:
        database.update(idEntry.get(),nameEntry.get(),phoneEntry.get(),roleBox.get(),genderBox.get(),salaryEntry.get())
        treeview_data()
        clear()
        messagebox.showinfo("Success","Employee updated successfully")

def selection(event):
    selected_item=tree.selection()
    if selected_item:
        row=tree.item(selected_item[0],"values")
        clear()
        idEntry.insert(0,row[0])
        nameEntry.insert(0, row[1])
        phoneEntry.insert(0, row[2])
        roleBox.set(row[3])
        genderBox.set(row[4])
        salaryEntry.insert(0, str(row[5]))

def clear(value=False):
    if value:
        tree.selection_remove(tree.focus())
    idEntry.delete(0, "end")
    nameEntry.delete(0, "end")
    phoneEntry.delete(0, "end")
    roleBox.set("")
    genderBox.set("")
    salaryEntry.delete(0, "end")

def add_employee():
    if idEntry.get() == "" or nameEntry.get() == "" or phoneEntry.get() == "" or roleBox.get() == ""  or genderBox.get() == "" or salaryEntry.get() == "":
        messagebox.showerror("Error","Please enter all required information")
    elif database.id_exists(idEntry.get()):
        messagebox.showerror("Error", "ID already exists")
    else:
        database.insert(idEntry.get(), nameEntry.get(), phoneEntry.get(), roleBox.get(), genderBox.get(), salaryEntry.get())
        treeview_data()
        clear()
        messagebox.showinfo("Success","Employee added successfully")

def backup_database():
    # Ask user where to save the backup
    file_path = filedialog.asksaveasfilename(
        title="Save Database Backup",
        defaultextension=".sql",
        initialfile=f"employee_data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql",
        filetypes=[
            ("SQL Backup Files (*.sql)", "*.sql"),
            ("All Files (*.*)", "*.*")
        ]
    )

    if not file_path:
        return
    try:
        # MySQL database details
        host = "localhost"
        user = "root"
        password = "1234"
        database_name = "employee_data"

        # Full path to mysqldump.exe
        mysqldump_path = r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe"

        # Run mysqldump
        command = [
            mysqldump_path,
            f"--host={host}",
            f"--user={user}",
            f"--password={password}",
            database_name
        ]

        with open(file_path, "w", encoding="utf-8") as backup_file:

            result = subprocess.run(
                command,
                stdout=backup_file,
                stderr=subprocess.PIPE,
                text=True
            )

        if result.returncode == 0:
            messagebox.showinfo(
                "Backup Successful",
                f"Database backup created successfully."
                f"Location:\n{file_path}"
            )
        else:
            messagebox.showerror(
                "Backup Failed",
                f"Could not create database backup."
                f"{result.stderr}"
            )

    except FileNotFoundError:
        messagebox.showerror(
            "Backup Error",
            "mysqldump was not found."
            "Please make sure MySQL Server is installed "
            "and mysqldump is available."
        )

    except Exception as e:
        messagebox.showerror(
            "Backup Error",
            f"An error occurred:\n{e}"
        )

# # # # # # # # # # # # # # # # # # # # # function part end # # # # # # # # # # # # # # # # # # # # #

# # # # # # # # # # # # # # # # # # # # # gui part start # # # # # # # # # # # # # # # # # # # # #
window = CTk()
window.geometry("1280x760")
window.resizable(False, False)
window.title("Employee Management System")
window.configure(fg_color=("#F3F5F8", "#111827"))

# ttk Treeview styling
style = ttk.Style()
try:
    style.theme_use("clam")
except:
    pass

def update_treeview_style():
    if get_appearance_mode() == "Dark":
        style.configure(
            "Treeview",
            background="#1F2937",
            foreground="#F9FAFB",
            fieldbackground="#1F2937",
            font=("Arial", 10),
            rowheight=34,
            borderwidth=0
        )
        style.configure(
            "Treeview.Heading",
            background="#374151",
            foreground="#F9FAFB",
            font=("Arial", 10, "bold"),
            relief="flat"
        )
        style.map(
            "Treeview",
            background=[("selected", "#2563EB")],
            foreground=[("selected", "#FFFFFF")]
        )
    else:
        style.configure(
            "Treeview",
            background="#FFFFFF",
            foreground="#1F2937",
            fieldbackground="#FFFFFF",
            font=("Arial", 10),
            rowheight=34,
            borderwidth=0
        )
        style.configure(
            "Treeview.Heading",
            background="#E8EEF7",
            foreground="#174A7E",
            font=("Arial", 10, "bold"),
            relief="flat"
        )
        style.map(
            "Treeview",
            background=[("selected", "#DBEAFE")],
            foreground=[("selected", "#111827")]
        )

update_treeview_style()

# Override theme function so ttk changes with CustomTkinter.
def change_theme():
    if theme_switch.get() == 1:
        set_appearance_mode("dark")
    else:
        set_appearance_mode("light")
    window.after(50, update_treeview_style)
    window.after(50, update_treeview_rows)

# Color helpers
CARD = ("#FFFFFF", "#1F2937")
PANEL = ("#FFFFFF", "#111827")
INPUT = ("#FFFFFF", "#374151")
BORDER = ("#D1D5DB", "#4B5563")
TEXT = ("#1F2937", "#F9FAFB")
MUTED = ("#6B7280", "#9CA3AF")
PRIMARY = ("#2563EB", "#3B82F6")
DANGER = ("#DC2626", "#EF4444")
SUCCESS = ("#16A34A", "#22C55E")

# # # Main application layout # # #

# Sidebar
sidebar = CTkFrame(
    window,
    width=220,
    height=760,
    corner_radius=0,
    fg_color=("#172A46", "#0F172A")
)
sidebar.place(x=0, y=0)
sidebar.pack_propagate(False)

# Brand
brand_icon = CTkLabel(
    sidebar,
    text="EMS",
    font=("Arial", 24, "bold"),
    text_color="#FFFFFF"
)
brand_icon.place(x=28, y=28)

brand_title = CTkLabel(
    sidebar,
    text="Employee Management",
    font=("Arial", 13, "bold"),
    text_color="#DCE8F7"
)
brand_title.place(x=28, y=62)

brand_subtitle = CTkLabel(
    sidebar,
    text="Management System",
    font=("Arial", 11),
    text_color="#94A3B8"
)
brand_subtitle.place(x=28, y=84)

sidebar_separator = CTkFrame(
    sidebar,
    height=1,
    width=164,
    fg_color="#334155"
)
sidebar_separator.place(x=28, y=120)

# Sidebar section label
nav_label = CTkLabel(
    sidebar,
    text="NAVIGATION",
    font=("Arial", 10, "bold"),
    text_color="#64748B"
)
nav_label.place(x=28, y=142)

# Sidebar buttons
def sidebar_button(text, command, y, active=False):
    button = CTkButton(
        sidebar,
        text=text,
        command=command,
        width=164,
        height=42,
        corner_radius=8,
        anchor="w",
        font=("Arial", 12, "bold"),
        fg_color=("#2563EB" if active else "transparent"),
        hover_color=("#1D4ED8" if active else "#243B5A"),
        text_color="#FFFFFF"
    )
    button.place(x=28, y=y)
    return button

sidebar_button("  Employees", lambda: clear(False), 170, True)
sidebar_button("  Dashboard", open_dashboard, 220)
sidebar_button("  Database Backup", backup_database, 270)
sidebar_button("  Restore Employee", restore_employee_window, 320)
sidebar_button("  Ask AI", open_ask_ai, 370)

# Sidebar bottom
sidebar_separator2 = CTkFrame(
    sidebar,
    height=1,
    width=164,
    fg_color="#334155"
)
sidebar_separator2.place(x=28, y=610)

theme_switch = CTkSwitch(
    sidebar,
    text="Dark Mode",
    command=change_theme,
    font=("Arial", 11, "bold"),
    text_color="#E2E8F0",
    progress_color="#2563EB",
    button_color="#CBD5E1",
    button_hover_color="#FFFFFF"
)
theme_switch.place(x=28, y=630)

logoutButton = CTkButton(
    sidebar,
    command=log_out,
    text="  Log Out",
    width=164,
    height=42,
    corner_radius=8,
    anchor="w",
    font=("Arial", 12, "bold"),
    fg_color="transparent",
    hover_color="#7F1D1D",
    text_color="#FCA5A5"
)
logoutButton.place(x=28, y=685)

# Main content
content = CTkFrame(
    window,
    width=1060,
    height=760,
    corner_radius=0,
    fg_color=("#F3F5F8", "#111827")
)
content.place(x=220, y=0)
content.pack_propagate(False)

# Header
header = CTkFrame(
    content,
    width=1010,
    height=76,
    corner_radius=14,
    fg_color=CARD
)
header.place(x=25, y=20)
header.pack_propagate(False)

# Title Label
titleLabel = CTkLabel(
    header,
    text="Employees",
    font=("Arial", 24, "bold"),
    text_color=("#174A7E", "#60A5FA")
)
titleLabel.place(x=24, y=13)

# Subtitle Label
subtitleLabel = CTkLabel(
    header,
    text="Manage employee records, information and data",
    font=("Arial", 11),
    text_color=MUTED
)
subtitleLabel.place(x=25, y=45)

# Top-right quick action
quick_add = CTkButton(
    header,
    text="+  Add Employee",
    command=lambda: clear(True),
    width=145,
    height=38,
    corner_radius=8,
    font=("Arial", 12, "bold"),
    fg_color=PRIMARY,
    hover_color=("#1D4ED8", "#2563EB")
)
quick_add.place(x=820, y=19)

# Employee information card
form_card = CTkFrame(
    content,
    width=335,
    height=535,
    corner_radius=14,
    fg_color=CARD
)
form_card.place(x=25, y=112)
form_card.pack_propagate(False)

form_title = CTkLabel(
    form_card,
    text="EMPLOYEE INFORMATION",
    font=("Arial", 14, "bold"),
    text_color=("#174A7E", "#60A5FA")
)
form_title.place(x=22, y=20)

form_hint = CTkLabel(
    form_card,
    text="Add or update employee details",
    font=("Arial", 10),
    text_color=MUTED
)
form_hint.place(x=22, y=45)

# Form helper
def form_label(parent, text, x, y):
    return CTkLabel(
        parent,
        text=text,
        font=("Arial", 11, "bold"),
        text_color=TEXT
    )

# ID
form_label(form_card, "Employee ID", 22, 78).place(x=22, y=78)
idEntry = CTkEntry(
    form_card, width=290, height=36, font=("Arial", 12),
    corner_radius=7, fg_color=INPUT, text_color=TEXT,
    border_color=BORDER, border_width=1,
    placeholder_text="e.g. EMP001"
)
idEntry.place(x=22, y=101)

# Name
form_label(form_card, "Full Name", 22, 145).place(x=22, y=145)
nameEntry = CTkEntry(
    form_card, width=290, height=36, font=("Arial", 12),
    corner_radius=7, fg_color=INPUT, text_color=TEXT,
    border_color=BORDER, border_width=1,
    placeholder_text="Employee name"
)
nameEntry.place(x=22, y=168)

# Phone
form_label(form_card, "Phone Number", 22, 212).place(x=22, y=212)
phone_validation = window.register(only_10_digits)
phoneEntry = CTkEntry(
    form_card, width=290, height=36, font=("Arial", 12),
    corner_radius=7, fg_color=INPUT, text_color=TEXT,
    border_color=BORDER, border_width=1,
    validate="key", validatecommand=(phone_validation, "%P"),
    placeholder_text="10-digit phone number"
)
phoneEntry.place(x=22, y=235)

# Role
form_label(form_card, "Role", 22, 279).place(x=22, y=279)
role_options = [
    "Software Developer", "Data Analyst", "HR Manager",
    "Project Manager", "Accountant", "Marketing Executive",
    "Sales Executive", "Business Analyst", "UI/UX Designer",
    "System Administrator"
]
roleBox = CTkComboBox(
    form_card, values=role_options, width=290, height=36,
    font=("Arial", 12), corner_radius=7,
    fg_color=INPUT, text_color=TEXT,
    border_color=BORDER, border_width=1
)
roleBox.place(x=22, y=302)
roleBox.set("")

# Gender
form_label(form_card, "Gender", 22, 346).place(x=22, y=346)
gender_options = ["Male", "Female"]
genderBox = CTkComboBox(
    form_card, values=gender_options, width=290, height=36,
    font=("Arial", 12), corner_radius=7,
    fg_color=INPUT, text_color=TEXT,
    border_color=BORDER, border_width=1
)
genderBox.place(x=22, y=369)
genderBox.set("")

# Salary
form_label(form_card, "Salary", 22, 413).place(x=22, y=413)
salary_validation_cmd = window.register(salary_validation)
salaryEntry = CTkEntry(
    form_card, width=290, height=36, font=("Arial", 12),
    corner_radius=7, fg_color=INPUT, text_color=TEXT,
    border_color=BORDER, border_width=1,
    validate="key", validatecommand=(salary_validation_cmd, "%P"),
    placeholder_text="e.g. 85000"
)
salaryEntry.place(x=22, y=436)

# Form actions
newButton = CTkButton(
    form_card,
    command=lambda: clear(True),
    text="Clear",
    width=88,
    height=34,
    corner_radius=7,
    font=("Arial", 11, "bold"),
    fg_color=("#64748B", "#475569"),
    hover_color=("#475569", "#64748B")
)
newButton.place(x=22, y=486)

# Add Button
addButton = CTkButton(
    form_card,
    command=add_employee,
    text="Add",
    width=88,
    height=34,
    corner_radius=7,
    font=("Arial", 11, "bold"),
    fg_color=SUCCESS,
    hover_color=("#15803D", "#16A34A")
)
addButton.place(x=123, y=486)

# Update Button
updateButton = CTkButton(
    form_card,
    command=update_employee,
    text="Update",
    width=88,
    height=34,
    corner_radius=7,
    font=("Arial", 11, "bold"),
    fg_color=PRIMARY,
    hover_color=("#1D4ED8", "#2563EB")
)
updateButton.place(x=224, y=486)

# Employee table card
table_card = CTkFrame(
    content,
    width=675,
    height=535,
    corner_radius=14,
    fg_color=CARD
)
table_card.place(x=365, y=112)
table_card.pack_propagate(False)

table_title = CTkLabel(
    table_card,
    text="EMPLOYEE DIRECTORY",
    font=("Arial", 14, "bold"),
    text_color=("#174A7E", "#60A5FA")
)
table_title.place(x=20, y=18)

# Search
searchBox = CTkComboBox(
    table_card,
    values=["Id", "Name", "Phone", "Role", "Gender", "Salary"],
    width=115,
    height=34,
    font=("Arial", 11),
    corner_radius=7,
    state="readonly",
    fg_color=INPUT,
    text_color=TEXT,
    border_color=BORDER,
    border_width=1
)
searchBox.place(x=20, y=52)
searchBox.set("Search By")

searchEntry = CTkEntry(
    table_card,
    width=200,
    height=34,
    font=("Arial", 11),
    corner_radius=7,
    fg_color=INPUT,
    text_color=TEXT,
    border_color=BORDER,
    border_width=1,
    placeholder_text="Search employees..."
)
searchEntry.place(x=145, y=52)

searchButton = CTkButton(
    table_card,
    command=search_employee,
    text="Search",
    width=82,
    height=34,
    corner_radius=7,
    font=("Arial", 11, "bold"),
    fg_color=PRIMARY,
    hover_color=("#1D4ED8", "#2563EB")
)
searchButton.place(x=355, y=52)

showallButton = CTkButton(
    table_card,
    command=showall_employee,
    text="Show All",
    width=82,
    height=34,
    corner_radius=7,
    font=("Arial", 11, "bold"),
    fg_color=("#64748B", "#475569"),
    hover_color=("#475569", "#64748B")
)
showallButton.place(x=447, y=52)

# Treeview
tree = ttk.Treeview(
    table_card,
    columns=("Id", "Name", "Phone", "Role", "Gender", "Salary"),
    show="headings",
    selectmode="browse"
)

columns = {
    "Id": ("ID", 75),
    "Name": ("Name", 125),
    "Phone": ("Phone", 110),
    "Role": ("Role", 145),
    "Gender": ("Gender", 75),
    "Salary": ("Salary", 105)
}

for col, (heading, width) in columns.items():
    tree.heading(col, text=heading)
    tree.column(col, width=width, anchor="center")

tree.place(x=20, y=100, width=620, height=355)

scrollbar = ttk.Scrollbar(
    table_card,
    orient="vertical",
    command=tree.yview
)
scrollbar.place(x=640, y=100, width=16, height=355)
tree.config(yscrollcommand=scrollbar.set)

# Alternating rows - Keeping Treeview row colors readable in both light and dark modes.
def update_treeview_rows():
    if get_appearance_mode() == "Dark":
        tree.tag_configure(
            "oddrow",
            background="#1F2937",
            foreground="#F9FAFB"
        )
        tree.tag_configure(
            "evenrow",
            background="#273449",
            foreground="#F9FAFB"
        )
    else:
        tree.tag_configure(
            "oddrow",
            background="#F8FAFC",
            foreground="#1F2937"
        )
        tree.tag_configure(
            "evenrow",
            background="#FFFFFF",
            foreground="#1F2937"
        )

update_treeview_rows()

# Delete Employee Button
deleteButton = CTkButton(
    table_card,
    command=delete_employee,
    text="Delete Selected",
    width=125,
    height=34,
    corner_radius=7,
    font=("Arial", 11, "bold"),
    fg_color=DANGER,
    hover_color=("#B91C1C", "#DC2626")
)
deleteButton.place(x=20, y=472)

# Delete All Employee Button
deleteallButton = CTkButton(
    table_card,
    command=delete_all_employee,
    text="Delete All",
    width=105,
    height=34,
    corner_radius=7,
    font=("Arial", 11, "bold"),
    fg_color=("#991B1B", "#B91C1C"),
    hover_color=("#7F1D1D", "#991B1B")
)
deleteallButton.place(x=155, y=472)

# Export Employee Options
export_options = ["CSV", "Excel"]
exportBox = CTkComboBox(
    table_card,
    values=export_options,
    width=100,
    height=34,
    font=("Arial", 11),
    corner_radius=7,
    state="readonly",
    fg_color=INPUT,
    text_color=TEXT,
    border_color=BORDER,
    border_width=1
)
exportBox.place(x=270, y=472)
exportBox.set("Export")

# Export Employee Button
exportButton = CTkButton(
    table_card,
    command=export_data,
    text="Export",
    width=82,
    height=34,
    corner_radius=7,
    font=("Arial", 11, "bold"),
    fg_color=("#475569", "#475569"),
    hover_color=("#334155", "#64748B")
)
exportButton.place(x=380, y=472)

# Bottom status bar
status_bar = CTkFrame(
    content,
    width=1010,
    height=60,
    corner_radius=12,
    fg_color=CARD
)
status_bar.place(x=25, y=662)
status_bar.pack_propagate(False)

status_dot = CTkLabel(
    status_bar,
    text="●",
    font=("Arial", 12),
    text_color="#22C55E"
)
status_dot.place(x=18, y=19)

status_label = CTkLabel(
    status_bar,
    text="Database Connected",
    font=("Arial", 11, "bold"),
    text_color=TEXT
)
status_label.place(x=35, y=18)

status_hint = CTkLabel(
    status_bar,
    text="Select an employee from the table to edit or delete",
    font=("Arial", 10),
    text_color=MUTED
)
status_hint.place(x=190, y=18)

# Refresh and event bindings
def treeview_data():
    all_employees = database.fetch_employees()
    tree.delete(*tree.get_children())

    for index, employee in enumerate(all_employees):
        tag = "evenrow" if index % 2 == 0 else "oddrow"
        tree.insert("", "end", values=employee, tags=(tag,))

# Re-define search-independent tree refresh above, preserving
# the existing employee CRUD functions.
treeview_data()
tree.bind("<ButtonRelease-1>", selection)

# Keyboard convenience 
window.bind("<Escape>", lambda event: clear(True))

# Keep the application running.
window.mainloop()