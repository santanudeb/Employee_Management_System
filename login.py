from customtkinter import *
from PIL import Image
from tkinter import messagebox
import database

# # # # # # # # # # # # # # # # # # # # # function part start # # # # # # # # # # # # # # # # # # # # #
def open_login():

    # Create login window
    root = CTk()

    root.geometry('930x478')
    root.resizable(False, False)
    root.title("Employee Management Login")

    # Login background image
    login_image = CTkImage(
        Image.open("login_image.png"),
        size=(930, 478)
    )

    login_imageLabel = CTkLabel(
        root,
        image=login_image,
        text=''
    )

    login_imageLabel.place(x=0, y=0)

    # Login function
    def login():

        username = usernameEntry.get()
        password = passwordEntry.get()

        if username == "" or password == "":
            messagebox.showerror(
                "Error",
                "Please enter both username and password"
            )


        elif database.verify_login(username, password):

            messagebox.showinfo(

                "Success",

                "Logged in successfully"

            )

            root.destroy()

            import ems

        else:

            messagebox.showerror(
                'Error',
                'Wrong credentials'
            )

    def change_password():

        change_window = CTkToplevel(root)
        change_window.geometry("400x400")
        change_window.resizable(False, False)
        change_window.title("Change Password")

        # Keep Change Password above the login window.
        change_window.transient(root)
        change_window.grab_set()
        change_window.lift()
        change_window.focus_force()
        change_window.attributes("-topmost", True)

        # Keep it above login while opening, then return normal top-level behavior.
        change_window.after(
            100,
            lambda: change_window.attributes("-topmost", False)
        )

        title = CTkLabel(
            change_window,
            text="CHANGE PASSWORD",
            font=("Arial", 20, "bold")
        )
        title.pack(pady=(30, 20))

        username = CTkEntry(
            change_window,
            width=280,
            placeholder_text="Username"
        )
        username.pack(pady=8)

        current_password = CTkEntry(
            change_window,
            width=280,
            placeholder_text="Current Password",
            show="*"
        )
        current_password.pack(pady=8)

        new_password = CTkEntry(
            change_window,
            width=280,
            placeholder_text="New Password",
            show="*"
        )
        new_password.pack(pady=8)

        confirm_password = CTkEntry(
            change_window,
            width=280,
            placeholder_text="Confirm New Password",
            show="*"
        )
        confirm_password.pack(pady=8)

        def update_password():

            user = username.get()
            current = current_password.get()
            new = new_password.get()
            confirm = confirm_password.get()

            if user == "" or current == "" or new == "" or confirm == "":
                messagebox.showerror(
                    "Error",
                    "Please fill in all fields"
                )
                return

            if not database.verify_login(user, current):
                messagebox.showerror(
                    "Error",
                    "Current password is incorrect"
                )
                return

            if new != confirm:
                messagebox.showerror(
                    "Error",
                    "New passwords do not match"
                )
                return

            if len(new) < 6:
                messagebox.showerror(
                    "Error",
                    "Password must contain at least 6 characters"
                )
                return

            if database.change_password(user, new):
                messagebox.showinfo(
                    "Success",
                    "Password changed successfully"
                )

                change_window.destroy()

        save_button = CTkButton(
            change_window,
            text="Change Password",
            width=280,
            command=update_password
        )

        save_button.pack(pady=20)

    # # # # # # # # # # # # # # # # # # # # # function part end # # # # # # # # # # # # # # # # # # # # #

    # # # # # # # # # # # # # # # # # # # # # button & input part start # # # # # # # # # # # # # # # # #
    # Header
    headingLabel = CTkLabel(
        root,
        text="Employee Management Login",
        bg_color='#EFF4FC',
        font=('Arial', 13, 'bold'),
        text_color='#2860B6'
    )

    headingLabel.place(x=175, y=250)

    # Username
    usernameEntry = CTkEntry(
        root,
        placeholder_text='Enter Your Username',
        bg_color='#EFF4FC',
        width=200
    )

    usernameEntry.place(x=175, y=285)

    # Password
    passwordEntry = CTkEntry(
        root,
        placeholder_text='Enter Your Password',
        bg_color='#EFF4FC',
        width=200,
        show='*'
    )

    passwordEntry.place(x=175, y=315)

    # Login button
    loginButton = CTkButton(
        root,
        text='Login',
        bg_color='#1350C5',
        width=200,
        cursor='hand2',
        command=login
    )

    loginButton.place(x=175, y=350)

    # Change Password button
    changePasswordButton = CTkButton(
        root,
        text="Change Password",
        width=200,
        command=change_password
    )

    changePasswordButton.place(
        x=175,
        y=385
    )

    root.mainloop()

    # # # # # # # # # # # # # # # # # # # # # button & input part end # # # # # # # # # # # # # # # # #

# # # # # # # # # # # # # # # # # # # # # # Start application # # # # # # # # # # # # # # # # # # # # #
if __name__ == "__main__":
    open_login()