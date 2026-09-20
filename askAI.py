import threading
import re
import os
from decimal import Decimal
from datetime import date, datetime

import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageDraw, ImageFont

import database


# Ollama model used in the user's AI Data Analyst project.
OLLAMA_MODEL = "llama3.2"


SCHEMA = """
MySQL database: employee_data

ACTIVE EMPLOYEE TABLE: data
Columns:
- ID VARCHAR(10) PRIMARY KEY
- Name VARCHAR(30)
- Phone VARCHAR(10)
- Role VARCHAR(30)
- Gender VARCHAR(10)
- Salary DECIMAL(10,2)

DELETED EMPLOYEE TABLE: deleted_employees
Columns:
- ID VARCHAR(10) PRIMARY KEY
- Name VARCHAR(30)
- Phone VARCHAR(10)
- Role VARCHAR(30)
- Gender VARCHAR(10)
- Salary DECIMAL(10,2)
- Deleted_At TIMESTAMP

Important:
- Use table `data` for current/active employees.
- Use table `deleted_employees` only when the user asks about deleted, restored, or deleted-history records.
- Salary is numeric.
- ID, Name, Phone, Role and Gender are text fields.
"""


SQL_SYSTEM_PROMPT = f"""
You are the database SQL assistant for an Employee Management System.
Generate ONE read-only MySQL query that answers the user's question.

{SCHEMA}

Rules:
1. Return SQL only. No markdown fences and no explanation.
2. Only SELECT queries are allowed.
3. Never use INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, TRUNCATE, GRANT, REVOKE, SET, CALL, LOAD, OUTFILE or INTO OUTFILE.
4. Never modify the database.
5. Use only the tables and columns listed in the schema.
6. Prefer the active `data` table unless the question explicitly concerns deleted records.
7. Add a sensible LIMIT 100 for list/detail queries unless the user asks for a specific number.
8. For aggregate questions, use appropriate SQL aggregation such as COUNT, SUM, AVG, MIN or MAX.
9. For salary questions, use the Salary column.
"""

ANSWER_SYSTEM_PROMPT = f"""
You are the AI assistant inside an Employee Management System.
Answer the user's question using the SQL result provided below.

{SCHEMA}

Rules:
- Be concise and factual.
- Do not invent employee records or numbers.
- If the result is empty, say that no matching records were found.
- If the question cannot be answered from the database result, say so clearly.
- Format currency/salary values clearly when appropriate.
- Do not provide SQL unless the user asks for the SQL query.
"""


def _clean_sql(text):
    """Remove common markdown/code-fence wrapping from an Ollama response."""
    sql = text.strip()
    sql = re.sub(r"^```(?:sql)?\s*", "", sql, flags=re.IGNORECASE)
    sql = re.sub(r"\s*```$", "", sql)
    sql = sql.strip().rstrip(";")
    return sql


def _validate_sql(sql):
    """Allow only a single read-only SELECT statement."""
    normalized = re.sub(r"\s+", " ", sql.strip()).lower()

    if not normalized.startswith("select ") and not normalized.startswith("select\n"):
        return False, "The AI did not generate a read-only SELECT query."

    if ";" in sql:
        return False, "Multiple SQL statements are not allowed."

    blocked = [
        "insert ", "update ", "delete ", "drop ", "alter ", "create ",
        "truncate ", "grant ", "revoke ", "call ", "load ",
        "outfile", "infile", "into outfile", "into dumpfile",
        "set ", "use ", "replace ", "handler ", "lock tables",
        "unlock tables", "shutdown"
    ]

    for keyword in blocked:
        if keyword in normalized:
            return False, f"Blocked SQL operation detected: {keyword.strip()}"

    return True, ""


def _format_value(value):
    if isinstance(value, Decimal):
        return f"{value:,.2f}"
    if isinstance(value, (datetime, date)):
        return value.strftime("%Y-%m-%d %H:%M:%S") if isinstance(value, datetime) else value.isoformat()
    return str(value) if value is not None else "NULL"


def _result_to_text(columns, rows):
    if not rows:
        return "No matching records found."

    lines = [" | ".join(columns)]
    lines.append(" | ".join("---" for _ in columns))

    for row in rows:
        lines.append(" | ".join(_format_value(value) for value in row))

    return "\n".join(lines)


def _get_llm():
    try:
        from langchain_ollama import ChatOllama
    except ImportError as exc:
        raise RuntimeError(
            "Ollama integration is not installed.\n\n"
            "Install the required packages with:\n"
            "pip install langchain-ollama ollama"
        ) from exc

    return ChatOllama(model=OLLAMA_MODEL, temperature=0)


def ask_database(question):
    """Generate a safe SELECT query, execute it, and turn the result into an answer."""
    question = question.strip()
    if not question:
        return "Please enter a question about the employee database."

    llm = _get_llm()

    # Step 1: Natural language -> SQL
    sql_response = llm.invoke([
        ("system", SQL_SYSTEM_PROMPT),
        ("human", question)
    ])
    sql = _clean_sql(sql_response.content)

    valid, reason = _validate_sql(sql)
    if not valid:
        return f"I couldn't safely execute the AI-generated query.\n\nReason: {reason}"

    # Step 2: Execute the read-only query against MySQL.
    db_connect, db_cursor = database.connect_database()
    if db_connect is None or db_cursor is None:
        return "I could not connect to the employee database. Please check that MySQL is running."

    try:
        db_cursor.execute(sql)
        rows = db_cursor.fetchall()
        columns = [description[0] for description in db_cursor.description] if db_cursor.description else []
        result_text = _result_to_text(columns, rows)
    except Exception as exc:
        return (
            "The database query could not be executed.\n\n"
            f"Database error: {exc}\n\n"
            "You can try asking the question in a simpler way."
        )
    finally:
        db_cursor.close()
        db_connect.close()

    # Step 3: SQL result -> natural language answer.
    answer_response = llm.invoke([
        ("system", ANSWER_SYSTEM_PROMPT),
        (
            "human",
            f"User question:\n{question}\n\n"
            f"SQL used internally:\n{sql}\n\n"
            f"Database result:\n{result_text}"
        )
    ])

    answer = answer_response.content.strip()
    return answer if answer else result_text


def open_ask_ai(parent):
    """Open the Ask AI window from the EMS sidebar."""
    ai_window = ctk.CTkToplevel(parent)
    ai_window.title("Ask AI - Employee Database")
    ai_window.geometry("1000x750")
    ai_window.minsize(800, 600)
    ai_window.transient(parent)

    # ------------------------------------------------------------
    # Colors matching the EMS application
    # ------------------------------------------------------------
    BG = ("#F3F5F8", "#111827")
    CARD = ("#FFFFFF", "#1F2937")
    TEXT = ("#1F2937", "#F9FAFB")
    MUTED = ("#6B7280", "#9CA3AF")
    PRIMARY = ("#2563EB", "#3B82F6")

    ai_window.configure(fg_color=BG)

    header = ctk.CTkFrame(
        ai_window,
        height=92,
        corner_radius=0,
        fg_color=("#FFFFFF", "#1F2937")
    )
    header.pack(fill="x")
    header.pack_propagate(False)

    title = ctk.CTkLabel(
        header,
        text="ASK AI ABOUT YOUR DATABASE",
        font=("Arial", 26, "bold"),
        text_color=("#174A7E", "#4DA6FF")
    )
    title.pack(anchor="w", padx=25, pady=(17, 2))

    subtitle = ctk.CTkLabel(
        header,
        text="Powered by Ollama • llama3.2 • Read-only database analysis",
        font=("Arial", 13),
        text_color=MUTED
    )
    subtitle.pack(anchor="w", padx=25)

    # Chat area
    chat_card = ctk.CTkFrame(
        ai_window,
        corner_radius=12,
        fg_color=CARD
    )
    chat_card.pack(fill="both", expand=True, padx=20, pady=(15, 10))

    # Use a real scrollable frame for chat messages instead of inserting
    # images into CTkTextbox. This avoids CustomTkinter/Tk scaling issues
    # and keeps the input area fully functional.
    chat_box = ctk.CTkScrollableFrame(
        chat_card,
        corner_radius=10,
        fg_color=("#F8FAFC", "#111827")
    )
    chat_box.pack(fill="both", expand=True, padx=12, pady=12)

    # ------------------------------------------------------------
    # Professional chat logos
    # Uses the project's images/ai_logo.jpg and images/cat_logo.jpg.
    # ------------------------------------------------------------
    images_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")

    ai_logo_path = os.path.join(images_dir, "ai_logo.jpg")
    you_logo_path = os.path.join(images_dir, "cat_logo.jpg")

    def load_chat_logo(path):
        try:
            image = Image.open(path).convert("RGB")
            return ctk.CTkImage(
                light_image=image,
                dark_image=image,
                size=(60, 60)
            )
        except Exception:
            # Small fallback icon if an image is temporarily unavailable.
            fallback = Image.new("RGB", (60, 60), "#E5E7EB")
            return ctk.CTkImage(
                light_image=fallback,
                dark_image=fallback,
                size=(60, 60)
            )

    ai_logo = load_chat_logo(ai_logo_path)
    you_logo = load_chat_logo(you_logo_path)

    chat_logos = {
        "AI": ai_logo,
        "You": you_logo
    }

    def append_message(role, message):
        is_user = role == "You"
        logo = chat_logos["You" if is_user else "AI"]
        # Message row
        row = ctk.CTkFrame(
            chat_box,
            fg_color="transparent"
        )
        row.pack(fill="x", padx=8, pady=(8, 4))

        # Logo
        logo_label = ctk.CTkLabel(
            row,
            text="",
            image=logo,
            width=26,
            height=26
        )
        logo_label.pack(side="left", anchor="n", padx=(2, 8))

        # Message content
        content = ctk.CTkFrame(
            row,
            corner_radius=10,
            fg_color=("#FFFFFF", "#1F2937") if not is_user
                       else ("#EFF6FF", "#172554")
        )
        content.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 4)
        )

        # Read-only selectable message box.
        # Users can highlight text and press Ctrl+C to copy it.
        message_box = ctk.CTkTextbox(
            content,
            height=max(42, min(220, 24 + (len(message) // 70 + message.count("\n")) * 18)),
            font=("Arial", 13),
            text_color=TEXT,
            fg_color="transparent",
            border_width=0,
            corner_radius=0,
            wrap="word"
        )
        message_box.pack(
            fill="x",
            expand=True,
            padx=8,
            pady=6
        )

        message_box.insert("1.0", message)
        message_box.configure(state="disabled")

        # Ctrl+C copies the selected text.
        def copy_selected(event=None):
            try:
                selected = message_box.get("sel.first", "sel.last")
            except Exception:
                return "break"

            if selected:
                ai_window.clipboard_clear()
                ai_window.clipboard_append(selected)
                ai_window.update()
            return "break"

        message_box.bind("<Control-c>", copy_selected)

        # Right-click provides a simple Copy action.
        def show_copy_menu(event):
            import tkinter as tk

            menu = tk.Menu(ai_window, tearoff=0)

            try:
                selected = message_box.get("sel.first", "sel.last")
            except Exception:
                selected = ""

            if selected:
                menu.add_command(
                    label="Copy",
                    command=lambda: (
                        ai_window.clipboard_clear(),
                        ai_window.clipboard_append(selected),
                        ai_window.update()
                    )
                )

            menu.tk_popup(event.x_root, event.y_root)
            menu.grab_release()

        message_box.bind("<Button-3>", show_copy_menu)

        # Keep the newest message visible.
        ai_window.after(
            50,
            lambda: chat_box._parent_canvas.yview_moveto(1.0)
        )

    append_message(
        "AI",
        "Hello! Ask me about the employee database.\n\n"
        "Examples:\n"
        "• How many employees are there?\n"
        "• What is the average salary?\n"
        "• Which role has the highest average salary?\n"
        "• Show employees earning more than 50000.\n"
        "• How many male and female employees are there in Gender?"
    )

    # Input area
    input_frame = ctk.CTkFrame(
        ai_window,
        height=92,
        corner_radius=12,
        fg_color=CARD
    )
    input_frame.pack(fill="x", padx=20, pady=(0, 20))
    input_frame.pack_propagate(False)

    question_entry = ctk.CTkEntry(
        input_frame,
        height=44,
        placeholder_text="Ask a question about your employee database...",
        font=("Arial", 13),
        corner_radius=8
    )
    question_entry.pack(side="left", fill="x", expand=True, padx=(12, 8), pady=24)

    send_button = ctk.CTkButton(
        input_frame,
        text="Ask AI",
        width=110,
        height=44,
        corner_radius=8,
        font=("Arial", 13, "bold"),
        fg_color=PRIMARY,
        hover_color=("#1D4ED8", "#2563EB")
    )
    send_button.pack(side="right", padx=(0, 12), pady=24)

    clear_button = ctk.CTkButton(
        input_frame,
        text="Clear",
        width=80,
        height=44,
        corner_radius=8,
        font=("Arial", 13, "bold"),
        fg_color=("#64748B", "#475569"),
        hover_color=("#475569", "#334155")
    )
    clear_button.pack(side="right", padx=(0, 8), pady=24)

    def set_busy(busy):
        if busy:
            send_button.configure(state="disabled", text="Thinking...")
            question_entry.configure(state="disabled")
        else:
            send_button.configure(state="normal", text="Ask AI")
            question_entry.configure(state="normal")
            question_entry.focus_set()

    def finish_answer(question, answer):
        if not ai_window.winfo_exists():
            return
        append_message("You", question)
        append_message("AI", answer)
        set_busy(False)

    def worker(question):
        try:
            answer = ask_database(question)
        except Exception as exc:
            answer = (
                "I couldn't process that request.\n\n"
                f"{exc}\n\n"
                "Make sure Ollama is installed, running, and the "
                f"'{OLLAMA_MODEL}' model is available."
            )

        try:
            ai_window.after(0, lambda: finish_answer(question, answer))
        except Exception:
            pass

    def send_question(event=None):
        question = question_entry.get().strip()
        if not question:
            return "break"

        question_entry.delete(0, "end")
        set_busy(True)
        threading.Thread(target=worker, args=(question,), daemon=True).start()
        return "break"

    def clear_chat():
        for widget in chat_box.winfo_children():
            widget.destroy()

        append_message(
            "AI",
            "Chat cleared. What would you like to know about the database?"
        )

    send_button.configure(command=send_question)
    clear_button.configure(command=clear_chat)
    question_entry.bind("<Return>", send_question)

    question_entry.focus_set()
