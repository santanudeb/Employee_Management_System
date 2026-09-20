import pymysql
from tkinter import messagebox
import hashlib

# # # # # # # # # # # # # # # # # # # # # function part start # # # # # # # # # # # # # # # # # # # # #
def connect_database():
    try:
        db_connect = pymysql.connect(
            host="localhost",
            user="root",
            password="1234"
        )

        db_cursor = db_connect.cursor()

        # Create database
        db_cursor.execute(
            "CREATE DATABASE IF NOT EXISTS employee_data"
        )

        # Select database
        db_cursor.execute(
            "USE employee_data"
        )

        # Create employee table
        db_cursor.execute("""
            CREATE TABLE IF NOT EXISTS data (
                ID VARCHAR(10) PRIMARY KEY,
                Name VARCHAR(30),
                Phone VARCHAR(10),
                Role VARCHAR(30),
                Gender VARCHAR(10),
                Salary DECIMAL(10,2)
            )
        """)

        # Create users table
        db_cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username VARCHAR(50) PRIMARY KEY,
                password_hash VARCHAR(255) NOT NULL
            )
        """)

        db_connect.commit()

        return db_connect, db_cursor

    except Exception as e:
        messagebox.showerror(
            "Database Error",
            f"Connection Error:\n{e}"
        )
        return None, None

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_default_user():
    db_connect, db_cursor = connect_database()

    if db_connect is None:
        return
    try:
        password_hash = hash_password("admin")

        query = """
            INSERT IGNORE INTO users (username, password_hash)
            VALUES (%s, %s)
        """

        db_cursor.execute(
            query,
            ("admin", password_hash)
        )

        db_connect.commit()

    finally:
        db_cursor.close()
        db_connect.close()

def verify_login(username, password):
    db_connect, db_cursor = connect_database()

    if db_connect is None:
        return False
    try:
        query = """
            SELECT password_hash
            FROM users
            WHERE username = %s
        """

        db_cursor.execute(query, (username,))
        result = db_cursor.fetchone()

        if result is None:
            return False

        stored_hash = result[0]
        entered_hash = hash_password(password)

        return stored_hash == entered_hash

    finally:
        db_cursor.close()
        db_connect.close()

def change_password(username, new_password):
    db_connect, db_cursor = connect_database()

    if db_connect is None:
        return False
    try:
        password_hash = hash_password(new_password)

        query = """
            UPDATE users
            SET password_hash = %s
            WHERE username = %s
        """

        db_cursor.execute(
            query,
            (password_hash, username)
        )

        db_connect.commit()

        return db_cursor.rowcount > 0

    except Exception as e:
        db_connect.rollback()

        messagebox.showerror(
            "Database Error",
            f"Could not change password:\n{e}"
        )

        return False

    finally:
        db_cursor.close()
        db_connect.close()

def insert(emp_id, name, phone, role, gender, salary):
    db_connect, db_cursor = connect_database()

    if db_connect is None:
        return
    try:
        query = """
            INSERT INTO data
            (ID, Name, Phone, Role, Gender, Salary)
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        values = (
            emp_id,
            name,
            phone,
            role,
            gender,
            salary
        )

        db_cursor.execute(query, values)

        db_connect.commit()

    except Exception as e:
        db_connect.rollback()

        messagebox.showerror(
            "Database Error",
            f"Could not add employee:\n{e}"
        )

    finally:
        db_cursor.close()
        db_connect.close()

def id_exists(emp_id):
    db_connect, db_cursor = connect_database()

    query = "SELECT ID FROM data WHERE ID = %s"

    db_cursor.execute(query, (emp_id,))

    result = db_cursor.fetchone()

    db_cursor.close()
    db_connect.close()

    return result is not None

def fetch_employees():
    db_connect, db_cursor = connect_database()

    query = "SELECT * FROM data"

    db_cursor.execute(query)

    result = db_cursor.fetchall()

    db_cursor.close()
    db_connect.close()

    return result

def update(new_id, new_name, new_phone, new_role, new_gender, new_salary):
    db_connect, db_cursor = connect_database()

    query = """
            UPDATE data
            SET Name = %s,
                Phone = %s,
                Role = %s,
                Gender = %s,
                Salary = %s
            WHERE ID = %s
        """

    values = (
        new_name,
        new_phone,
        new_role,
        new_gender,
        new_salary,
        new_id
    )

    db_cursor.execute(query, values)

    db_connect.commit()

    db_cursor.close()
    db_connect.close()

def delete(emp_id):
    db_connect, db_cursor = connect_database()

    try:
        # Make sure deleted table exists
        db_cursor.execute("""
            CREATE TABLE IF NOT EXISTS deleted_employees (
                ID VARCHAR(10) PRIMARY KEY,
                Name VARCHAR(30),
                Phone VARCHAR(10),
                Role VARCHAR(30),
                Gender VARCHAR(10),
                Salary DECIMAL(10,2),
                Deleted_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Get employee before deleting
        db_cursor.execute(
            "SELECT ID, Name, Phone, Role, Gender, Salary "
            "FROM data WHERE ID = %s",
            (emp_id,)
        )

        employee = db_cursor.fetchone()

        if employee is None:
            return False

        # Move employee to deleted table
        db_cursor.execute("""
            INSERT INTO deleted_employees
            (ID, Name, Phone, Role, Gender, Salary)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, employee)

        # Delete from active employee table
        db_cursor.execute(
            "DELETE FROM data WHERE ID = %s",
            (emp_id,)
        )

        db_connect.commit()

        return True

    except Exception as e:
        db_connect.rollback()
        messagebox.showerror(
            "Database Error",
            f"Could not delete employee:\n{e}"
        )

        return False

    finally:
        db_cursor.close()
        db_connect.close()

def search_employee(searchOption, searchValue):
    db_connect, db_cursor = connect_database()

    query = f"""
        SELECT * FROM data
        WHERE {searchOption} = %s
    """

    db_cursor.execute(query, (searchValue,))

    result = db_cursor.fetchall()

    db_cursor.close()
    db_connect.close()

    return result

def delete_all_employee():
    db_connect, db_cursor = connect_database()

    query = """
                TRUNCATE TABLE data   
            """

    db_cursor.execute(query)

    db_connect.commit()

    db_cursor.close()
    db_connect.close()

def create_deleted_table():
    db_connect, db_cursor = connect_database()

    query = """
        CREATE TABLE IF NOT EXISTS deleted_employees (
            ID VARCHAR(10) PRIMARY KEY,
            Name VARCHAR(30),
            Phone VARCHAR(10),
            Role VARCHAR(30),
            Gender VARCHAR(10),
            Salary DECIMAL(10,2),
            Deleted_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """

    db_cursor.execute(query)
    db_connect.commit()

    db_cursor.close()
    db_connect.close()

def fetch_deleted_employees():
    db_connect, db_cursor = connect_database()

    query = """
        SELECT ID, Name, Phone, Role, Gender, Salary, Deleted_At
        FROM deleted_employees
        ORDER BY Deleted_At DESC
    """

    db_cursor.execute(query)
    result = db_cursor.fetchall()

    db_cursor.close()
    db_connect.close()

    return result

def restore_employee(emp_id):
    db_connect, db_cursor = connect_database()

    try:
        # Get employee from deleted table
        db_cursor.execute("""
            SELECT ID, Name, Phone, Role, Gender, Salary
            FROM deleted_employees
            WHERE ID = %s
        """, (emp_id,))

        employee = db_cursor.fetchone()

        if employee is None:
            return False

        # Check whether ID already exists
        db_cursor.execute(
            "SELECT ID FROM data WHERE ID = %s",
            (emp_id,)
        )

        if db_cursor.fetchone() is not None:

            messagebox.showerror(
                "Restore Error",
                f"Employee ID {emp_id} already exists."
            )

            return False

        # Put employee back into active table
        db_cursor.execute("""
            INSERT INTO data
            (ID, Name, Phone, Role, Gender, Salary)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, employee)

        # Remove from deleted table
        db_cursor.execute(
            "DELETE FROM deleted_employees WHERE ID = %s",
            (emp_id,)
        )

        db_connect.commit()

        return True

    except Exception as e:
        db_connect.rollback()

        messagebox.showerror(
            "Database Error",
            f"Could not restore employee:\n{e}"
        )

        return False

    finally:

        db_cursor.close()
        db_connect.close()

# # # # # # # # # # # # # # # # # # # # # function part end # # # # # # # # # # # # # # # # # # # # #

# Calling functions
create_default_user()