import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def open_dashboard(parent, tree):

    # Dashboard Window
    dashboard_window = ctk.CTkToplevel(parent)

    dashboard_window.title("Employee Dashboard")
    dashboard_window.geometry("1550x800")
    dashboard_window.resizable(False, False)

    dashboard_window.transient(parent)

    # Get Employee Data
    employees = tree.get_children()

    employee_data = []

    for employee in employees:

        values = tree.item(employee, "values")

        if values:
            employee_data.append(values)

    # Calculate Statistics
    total_employees = len(employee_data)

    male_count = 0
    female_count = 0

    salaries = []
    role_count = {}
    role_salaries = {}

    for employee in employee_data:
        # Salary
        try:
            salary = float(employee[5])
            salaries.append(salary)

        except (ValueError, TypeError):
            pass

        # Gender
        gender = str(employee[4]).lower()

        if gender == "male":
            male_count += 1

        elif gender == "female":
            female_count += 1

        # Role
        role = str(employee[3])

        if role:
            role_count[role] = role_count.get(role, 0) + 1

    # Average Salary By Role
    for employee in employee_data:
        try:
            role = str(employee[3])
            salary = float(employee[5])

            if role:
                role_salaries.setdefault(role, []).append(salary)

        except (ValueError, TypeError, IndexError):
            pass

    role_average_salary = {
        role: sum(values) / len(values)
        for role, values in role_salaries.items()
        if values
    }

    # Salary Statistics
    if salaries:

        total_salary = sum(salaries)

        average_salary = total_salary / len(salaries)

        highest_salary = max(salaries)

        lowest_salary = min(salaries)

    else:

        total_salary = 0
        average_salary = 0
        highest_salary = 0
        lowest_salary = 0

    # Dashboard Title
    title_label = ctk.CTkLabel(
        dashboard_window,
        text="EMPLOYEE DASHBOARD",
        font=("Arial", 28, "bold"),
        text_color=("#174A7E", "#4DA6FF")
    )

    title_label.pack(pady=(20, 3))

    subtitle_label = ctk.CTkLabel(
        dashboard_window,
        text="Employee statistics and salary overview",
        font=("Arial", 13),
        text_color=("#666666", "#AAAAAA")
    )

    subtitle_label.pack(pady=(0, 15))

    # MAIN CONTENT
    main_frame = ctk.CTkFrame(
        dashboard_window,
        fg_color="transparent"
    )

    main_frame.pack(
        fill="both",
        expand=True,
        padx=25,
        pady=5
    )

    # LEFT SIDE
    left_frame = ctk.CTkFrame(
        main_frame,
        width=430,
        fg_color="transparent"
    )

    left_frame.pack(
        side="left",
        fill="y",
        padx=(0, 10)
    )

    left_frame.pack_propagate(False)

    # Statistics Frame
    statistics_frame = ctk.CTkFrame(
        left_frame,
        fg_color="transparent"
    )

    statistics_frame.pack(
        fill="x",
        pady=(5, 10)
    )

    # Make both columns equal
    statistics_frame.grid_columnconfigure(0, weight=1)
    statistics_frame.grid_columnconfigure(1, weight=1)

    # Make rows equal
    for row in range(4):
        statistics_frame.grid_rowconfigure(
            row,
            weight=1
        )

    # Card Function
    def create_card(title, value, row, column):

        card = ctk.CTkFrame(
            statistics_frame,
            height=90,
            corner_radius=12,
            fg_color=("#F5F7FA", "#2B2B2B")
        )

        card.grid(
            row=row,
            column=column,
            padx=7,
            pady=7,
            sticky="nsew"
        )

        card.grid_propagate(False)

        # Title
        card_title = ctk.CTkLabel(
            card,
            text=title,
            font=("Arial", 12),
            text_color=("#555555", "#BBBBBB")
        )

        card_title.pack(
            pady=(15, 3)
        )

        # Number
        card_value = ctk.CTkLabel(
            card,
            text=value,
            font=("Arial", 20, "bold"),
            text_color=("#174A7E", "#4DA6FF")
        )

        card_value.pack(
            pady=(0, 10)
        )

    # Statistics Cards
    create_card(
        "Total Employees",
        str(total_employees),
        0,
        0
    )

    create_card(
        "Total Salary",
        f"{total_salary:,.2f}",
        0,
        1
    )

    create_card(
        "Average Salary",
        f"{average_salary:,.2f}",
        1,
        0
    )

    create_card(
        "Highest Salary",
        f"{highest_salary:,.2f}",
        1,
        1
    )

    create_card(
        "Lowest Salary",
        f"{lowest_salary:,.2f}",
        2,
        0
    )

    create_card(
        "Male Employees",
        str(male_count),
        2,
        1
    )

    create_card(
        "Female Employees",
        str(female_count),
        3,
        0
    )

    create_card(
        "Total Roles",
        str(len(role_count)),
        3,
        1
    )

    # Employees By Role
    role_frame = ctk.CTkFrame(
        left_frame,
        height=135,
        corner_radius=12,
        fg_color=("#F5F7FA", "#2B2B2B")
    )

    role_frame.pack(
        fill="x",
        padx=7,
        pady=(5, 0)
    )

    role_frame.pack_propagate(False)

    role_title = ctk.CTkLabel(
        role_frame,
        text="EMPLOYEES BY ROLE",
        font=("Arial", 17, "bold"),
        text_color=("#174A7E", "#4DA6FF")
    )

    role_title.pack(
        pady=(10, 5)
    )

    # Display up to 12 roles in 3 columns
    role_grid = ctk.CTkFrame(
        role_frame,
        fg_color="transparent"
    )

    role_grid.pack(
        fill="both",
        expand=True,
        padx=10,
        pady=(0, 8)
    )

    for column in range(3):
        role_grid.grid_columnconfigure(column, weight=1)

    for row in range(4):
        role_grid.grid_rowconfigure(row, weight=1)

    if role_count:
        roles = list(role_count.items())[:12]

        for index, (role, count) in enumerate(roles):
            row = index // 3
            column = index % 3

            role_label = ctk.CTkLabel(
                role_grid,
                text=f"{role}: {count}",
                font=("Arial", 12),
                text_color=("#333333", "#DDDDDD"),
                justify="center",
                wraplength=135
            )

            role_label.grid(
                row=row,
                column=column,
                padx=3,
                pady=1,
                sticky="nsew"
            )

    else:
        role_label = ctk.CTkLabel(
            role_grid,
            text="No employee data available",
            font=("Arial", 11),
            text_color=("#333333", "#DDDDDD")
        )

        role_label.grid(
            row=0,
            column=0,
            columnspan=3,
            sticky="nsew"
        )

    # MIDDLE SIDE - SALARY ANALYTICS
    middle_frame = ctk.CTkFrame(
        main_frame,
        width=500,
        fg_color="transparent"
    )

    middle_frame.pack(
        side="left",
        fill="both",
        expand=False,
        padx=10
    )

    middle_frame.pack_propagate(False)

    # AVERAGE SALARY BY ROLE
    average_role_frame = ctk.CTkFrame(
        middle_frame,
        height=285,
        corner_radius=12,
        fg_color=("#F5F7FA", "#2B2B2B")
    )

    average_role_frame.pack(
        fill="x",
        pady=(0, 10)
    )

    average_role_frame.pack_propagate(False)

    average_role_title = ctk.CTkLabel(
        average_role_frame,
        text="AVERAGE SALARY BY ROLE",
        font=("Arial", 17, "bold"),
        text_color=("#174A7E", "#4DA6FF")
    )

    average_role_title.pack(pady=(8, 0))

    figure3 = Figure(figsize=(4.9, 2.45), dpi=100)
    ax3 = figure3.add_subplot(111)

    appearance_mode = ctk.get_appearance_mode()

    if appearance_mode == "Dark":
        figure3.patch.set_facecolor("#2B2B2B")
        ax3.set_facecolor("#2B2B2B")
        text_color3 = "white"
    else:
        figure3.patch.set_facecolor("#F5F7FA")
        ax3.set_facecolor("#F5F7FA")
        text_color3 = "black"

    sorted_role_salary = sorted(
        role_average_salary.items(),
        key=lambda item: item[1],
        reverse=True
    )

    if sorted_role_salary:
        labels = [item[0] for item in sorted_role_salary]
        values = [item[1] for item in sorted_role_salary]
        positions = list(range(len(labels)))

        ax3.barh(positions, values)
        ax3.set_yticks(positions)
        ax3.set_yticklabels(labels, fontsize=7, color=text_color3)
        ax3.invert_yaxis()

        from matplotlib.ticker import MaxNLocator, FuncFormatter

        ax3.xaxis.set_major_locator(
            MaxNLocator(nbins=5)
        )

        ax3.xaxis.set_major_formatter(
            FuncFormatter(lambda x, pos: f"{x:,.0f}")
        )

        ax3.tick_params(
            axis="x",
            colors=text_color3,
            labelsize=7,
            pad=2
        )

        ax3.tick_params(
            axis="y",
            colors=text_color3,
            labelsize=7
        )

        ax3.set_xlabel(
            "Average Salary",
            color=text_color3,
            fontsize=8,
            labelpad=2
        )

        ax3.spines["bottom"].set_color(text_color3)
        ax3.spines["left"].set_color(text_color3)
        ax3.spines["top"].set_visible(False)
        ax3.spines["right"].set_visible(False)

        max_value = max(values)

        for i, value in enumerate(values):
            ax3.text(
                value,
                i,
                f" {value:,.0f}",
                va="center",
                fontsize=7,
                color=text_color3
            )

        ax3.set_xlim(0, max_value * 1.22 if max_value else 1)

    else:
        ax3.text(
            0.5, 0.5, "No Data",
            ha="center", va="center",
            color=text_color3
        )

    figure3.tight_layout(pad=0.8)

    canvas3 = FigureCanvasTkAgg(
        figure3,
        master=average_role_frame
    )
    canvas3.draw()
    canvas3.get_tk_widget().pack(
        fill="both",
        expand=True,
        padx=8,
        pady=2
    )

    # SALARY DISTRIBUTION
    distribution_frame = ctk.CTkFrame(
        middle_frame,
        height=285,
        corner_radius=12,
        fg_color=("#F5F7FA", "#2B2B2B")
    )

    distribution_frame.pack(
        fill="both",
        expand=True
    )

    distribution_frame.pack_propagate(False)

    distribution_title = ctk.CTkLabel(
        distribution_frame,
        text="SALARY DISTRIBUTION",
        font=("Arial", 17, "bold"),
        text_color=("#174A7E", "#4DA6FF")
    )

    distribution_title.pack(pady=(8, 0))

    figure4 = Figure(figsize=(4.6, 2.45), dpi=100)
    ax4 = figure4.add_subplot(111)

    if appearance_mode == "Dark":
        figure4.patch.set_facecolor("#2B2B2B")
        ax4.set_facecolor("#2B2B2B")
        text_color4 = "white"
    else:
        figure4.patch.set_facecolor("#F5F7FA")
        ax4.set_facecolor("#F5F7FA")
        text_color4 = "black"

    distribution_labels = [
        "Below 70K",
        "70K - 89K",
        "90K - 109K",
        "110K - 129K",
        "130K+"
    ]

    distribution_values = [0, 0, 0, 0, 0]

    for salary in salaries:
        if salary < 70000:
            distribution_values[0] += 1
        elif salary < 90000:
            distribution_values[1] += 1
        elif salary < 110000:
            distribution_values[2] += 1
        elif salary < 130000:
            distribution_values[3] += 1
        else:
            distribution_values[4] += 1

    ax4.bar(distribution_labels, distribution_values)

    ax4.set_ylabel("Employees", color=text_color4, fontsize=9)
    ax4.tick_params(axis="x", colors=text_color4, labelsize=7, rotation=20)
    ax4.tick_params(axis="y", colors=text_color4, labelsize=8)

    ax4.spines["bottom"].set_color(text_color4)
    ax4.spines["left"].set_color(text_color4)
    ax4.spines["top"].set_visible(False)
    ax4.spines["right"].set_visible(False)

    for i, value in enumerate(distribution_values):
        if value > 0:
            ax4.text(
                i, value, str(value),
                ha="center", va="bottom",
                fontsize=8, color=text_color4
            )

    figure4.tight_layout()

    canvas4 = FigureCanvasTkAgg(
        figure4,
        master=distribution_frame
    )
    canvas4.draw()
    canvas4.get_tk_widget().pack(
        fill="both",
        expand=True,
        padx=8,
        pady=2
    )

    # RIGHT SIDE - CHARTS
    right_frame = ctk.CTkFrame(
        main_frame,
        width=500,
        fg_color="transparent"
    )

    right_frame.pack(
        side="left",
        fill="both",
        expand=True,
        padx=(10, 0)
    )

    # GENDER PIE CHART
    appearance_mode = ctk.get_appearance_mode()

    gender_frame = ctk.CTkFrame(
        right_frame,
        height=285,
        corner_radius=12,
        fg_color=("#F5F7FA", "#2B2B2B")
    )

    gender_frame.pack(
        fill="x",
        pady=(0, 10)
    )

    gender_frame.pack_propagate(False)

    gender_title = ctk.CTkLabel(
        gender_frame,
        text="GENDER DISTRIBUTION",
        font=("Arial", 17, "bold"),
        text_color=("#174A7E", "#4DA6FF")
    )

    gender_title.pack(
        pady=(8, 0)
    )

    # Create Gender Chart
    figure1 = Figure(
        figsize=(4.5, 2.1),
        dpi=100
    )

    ax1 = figure1.add_subplot(111)

    # Dark mode detection
    if appearance_mode == "Dark":

        figure1.patch.set_facecolor("#2B2B2B")
        ax1.set_facecolor("#2B2B2B")

        text_color = "white"
    else:
        figure1.patch.set_facecolor("#F5F7FA")
        ax1.set_facecolor("#F5F7FA")

        text_color = "black"

    # Pie Data
    gender_values = []
    gender_labels = []

    if male_count > 0:
        gender_values.append(male_count)
        gender_labels.append("Male")
    if female_count > 0:
        gender_values.append(female_count)
        gender_labels.append("Female")
    if gender_values:
        ax1.pie(
            gender_values,
            labels=gender_labels,
            autopct="%1.0f%%",
            startangle=90,
            textprops={
                "color": text_color,
                "fontsize": 10
            }
        )
    else:
        ax1.text(
            0.5,
            0.5,
            "No Data",
            ha="center",
            va="center",
            color=text_color
        )

    ax1.axis("equal")

    figure1.tight_layout()

    canvas1 = FigureCanvasTkAgg(
        figure1,
        master=gender_frame
    )

    canvas1.draw()

    canvas1.get_tk_widget().pack(
        fill="both",
        expand=True,
        padx=10,
        pady=2
    )

    # SALARY GRAPH
    salary_frame = ctk.CTkFrame(
        right_frame,
        height=285,
        corner_radius=12,
        fg_color=("#F5F7FA", "#2B2B2B")
    )

    salary_frame.pack(
        fill="both",
        expand=True
    )

    salary_frame.pack_propagate(False)

    salary_title = ctk.CTkLabel(
        salary_frame,
        text="SALARY COMPARISON",
        font=("Arial", 17, "bold"),
        text_color=("#174A7E", "#4DA6FF")
    )

    salary_title.pack(
        pady=(8, 0)
    )

    # Create Salary Chart
    figure2 = Figure(
        figsize=(4.5, 2.1),
        dpi=100
    )

    ax2 = figure2.add_subplot(111)

    if appearance_mode == "Dark":

        figure2.patch.set_facecolor("#2B2B2B")
        ax2.set_facecolor("#2B2B2B")

        text_color = "white"
    else:
        figure2.patch.set_facecolor("#F5F7FA")
        ax2.set_facecolor("#F5F7FA")

        text_color = "black"

    # Salary Data
    salary_labels = [
        "Lowest",
        "Average",
        "Highest"
    ]

    salary_values = [
        lowest_salary,
        average_salary,
        highest_salary
    ]

    ax2.bar(
        salary_labels,
        salary_values
    )

    ax2.set_ylabel(
        "Salary",
        color=text_color
    )

    ax2.tick_params(
        axis="x",
        colors=text_color
    )

    ax2.tick_params(
        axis="y",
        colors=text_color
    )

    ax2.spines["bottom"].set_color(text_color)
    ax2.spines["left"].set_color(text_color)

    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)

    # Add Values Above Bars
    for i, value in enumerate(salary_values):
        ax2.text(
            i,
            value,
            f"{value:,.0f}",
            ha="center",
            va="bottom",
            color=text_color,
            fontsize=9
        )

    # Give space above highest bar
    if highest_salary > 0:
        ax2.set_ylim(
            0,
            highest_salary * 1.20
        )

    figure2.tight_layout()

    canvas2 = FigureCanvasTkAgg(
        figure2,
        master=salary_frame
    )

    canvas2.draw()

    canvas2.get_tk_widget().pack(
        fill="both",
        expand=True,
        padx=10,
        pady=2
    )

    # Close Button
    close_button = ctk.CTkButton(
        dashboard_window,
        text="Close Dashboard",
        width=170,
        height=38,
        font=("Arial", 13, "bold"),
        command=dashboard_window.destroy
    )

    close_button.pack(
        pady=(5, 15)
    )

    # LIVE DASHBOARD REFRESH
    # The EMS Treeview is refreshed after Add, Update, Delete,
    def get_data_signature():
        current_data = []

        for item in tree.get_children():
            values = tree.item(item, "values")
            current_data.append(tuple(values))

        return tuple(current_data)

    last_signature = get_data_signature()

    def live_refresh():
        nonlocal last_signature

        if not dashboard_window.winfo_exists():
            return

        current_signature = get_data_signature()

        if current_signature != last_signature:
            last_signature = current_signature

            # Rebuild with the latest employee data.
            dashboard_window.destroy()
            open_dashboard(parent, tree)
            return

        # Check again after 500 ms.
        dashboard_window.after(500, live_refresh)

    dashboard_window.after(500, live_refresh)