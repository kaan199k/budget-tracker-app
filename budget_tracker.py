import customtkinter as ctk
import sqlite3
from datetime import datetime
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Theme Dark Blue
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

# --- LOCALIZATION CONFIGURATION ---
# We keep internal keys (DB_KEYS) separate from Display Text.
# This ensures the database is consistent even if languages change.

TRANSLATIONS = {
    "EN": {
        "app_title": "Budget Tracker",
        "nav_dashboard": "Dashboard",
        "nav_add": "Add Transaction",
        "nav_analytics": "Analytics",
        "footer": "v1.1.0\nMade with Python",

        "dashboard_title": "Dashboard Overview",
        "card_balance": "Total Balance",
        "card_income": "Income",
        "card_expense": "Expenses",
        "recent_header": "Recent Transactions",
        "no_data": "No transactions yet.",

        "add_title": "Add New Transaction",
        "lbl_type": "Type",
        "lbl_amount": "Amount",
        "lbl_category": "Category",
        "lbl_date": "Date (YYYY-MM-DD)",
        "lbl_note": "Note",
        "btn_save": "Save Transaction",
        "currency": "$",

        "analytics_title": "Spending Analysis",
        "chart_title": "Expenses by Category",
        "no_chart_data": "Not enough data to show charts yet.",

        "msg_missing": "Please enter an amount.",
        "msg_error": "Amount must be a number.",
        "msg_success": "Transaction added successfully!",

        # Categories mapping (Display Name)
        "cat_Food": "Food",
        "cat_Transport": "Transport",
        "cat_Rent": "Rent",
        "cat_Salary": "Salary",
        "cat_Entertainment": "Entertainment",
        "cat_Shopping": "Shopping",
        "cat_Utilities": "Utilities",
        "cat_Other": "Other",

        # Transaction Types
        "type_Income": "Income",
        "type_Expense": "Expense"
    },
    "BG": {
        "app_title": "Бюджет Тракер",
        "nav_dashboard": "Табло",
        "nav_add": "Добави",
        "nav_analytics": "Статистика",
        "footer": "v1.1.0\nСъздадено с Python",

        "dashboard_title": "Общ Преглед",
        "card_balance": "Текущ Баланс",
        "card_income": "Приходи",
        "card_expense": "Разходи",
        "recent_header": "Последни Транзакции",
        "no_data": "Няма намерени записи.",

        "add_title": "Добави Нова Транзакция",
        "lbl_type": "Тип",
        "lbl_amount": "Сума",
        "lbl_category": "Категория",
        "lbl_date": "Дата (ГГГГ-ММ-ДД)",
        "lbl_note": "Бележка",
        "btn_save": "Запази Запис",
        "currency": "лв.",

        "analytics_title": "Анализ на Разходите",
        "chart_title": "Разходи по Категория",
        "no_chart_data": "Няма достатъчно данни за графика.",

        "msg_missing": "Моля, въведете сума.",
        "msg_error": "Сумата трябва да е число.",
        "msg_success": "Транзакцията е добавена успешно!",

        # Categories mapping
        "cat_Food": "Храна",
        "cat_Transport": "Транспорт",
        "cat_Rent": "Наем",
        "cat_Salary": "Заплата",
        "cat_Entertainment": "Забавление",
        "cat_Shopping": "Пазаруване",
        "cat_Utilities": "Сметки",
        "cat_Other": "Други",

        # Transaction Types
        "type_Income": "Приход",
        "type_Expense": "Разход"
    }
}

# Standard database keys
DB_CATEGORIES = ["Food", "Transport", "Rent", "Salary", "Entertainment", "Shopping", "Utilities", "Other"]


class BudgetApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Default Language
        self.current_lang = "EN"

        # Window setup
        self.title("Budget Tracker")
        self.geometry("1000x650")

        self.init_db()

        # Layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- Sidebar ---
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)  # Push footer down

        # Logo
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="$", font=ctk.CTkFont(size=40, weight="bold"),
                                       text_color="#2cc985")
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.brand_label = ctk.CTkLabel(self.sidebar_frame, text="Budget Tracker",
                                        font=ctk.CTkFont(size=16, weight="bold"))
        self.brand_label.grid(row=1, column=0, padx=20, pady=(0, 20))

        # Nav Buttons (We keep references to update text later)
        self.btn_dashboard = ctk.CTkButton(self.sidebar_frame, command=self.show_dashboard)
        self.btn_dashboard.grid(row=2, column=0, padx=20, pady=10)

        self.btn_add = ctk.CTkButton(self.sidebar_frame, command=self.show_add_page)
        self.btn_add.grid(row=3, column=0, padx=20, pady=10)

        self.btn_analytics = ctk.CTkButton(self.sidebar_frame, command=self.show_analytics)
        self.btn_analytics.grid(row=4, column=0, padx=20, pady=10)

        # --- Language Switcher
        self.lang_label = ctk.CTkLabel(self.sidebar_frame, text="Language / Език:", text_color="gray",
                                       font=("Arial", 10))
        self.lang_label.grid(row=6, column=0, padx=20, pady=(10, 0))

        self.lang_switch = ctk.CTkSegmentedButton(self.sidebar_frame, values=["EN", "BG"], command=self.change_language)
        self.lang_switch.set("EN")
        self.lang_switch.grid(row=7, column=0, padx=20, pady=(5, 20))

        # Footer
        self.label_footer = ctk.CTkLabel(self.sidebar_frame, text_color="gray")
        self.label_footer.grid(row=8, column=0, padx=20, pady=20)

        # --- Main Content ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew")

        # Initial UI Update
        self.update_sidebar_text()
        self.show_dashboard()

    def init_db(self):
        try:
            self.conn = sqlite3.connect("my_budget.db")
            self.cursor = self.conn.cursor()
            # Internal 'type' and 'category' are always stored in English
            self.cursor.execute("""
                                CREATE TABLE IF NOT EXISTS transactions
                                (
                                    id
                                    INTEGER
                                    PRIMARY
                                    KEY
                                    AUTOINCREMENT,
                                    type
                                    TEXT,
                                    category
                                    TEXT,
                                    amount
                                    REAL,
                                    date
                                    TEXT,
                                    note
                                    TEXT
                                )
                                """)
            self.conn.commit()
        except Exception as e:
            messagebox.showerror("DB Error", str(e))

    def tr(self, key):
        """Helper to get translated string"""
        return TRANSLATIONS[self.current_lang].get(key, key)

    def change_language(self, value):
        self.current_lang = value
        self.update_sidebar_text()
        # Refresh current page to show new language
        # We check which page is currently "active" by checking internal state or just defaulting to dashboard
        # For simplicity in this version, we reload the Dashboard, or we could track `self.current_page`
        self.show_dashboard()

    def update_sidebar_text(self):
        self.title(self.tr("app_title"))
        self.brand_label.configure(text=self.tr("app_title"))
        self.btn_dashboard.configure(text=self.tr("nav_dashboard"))
        self.btn_add.configure(text=self.tr("nav_add"))
        self.btn_analytics.configure(text=self.tr("nav_analytics"))
        self.label_footer.configure(text=self.tr("footer"))

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    # --- PAGES ---

    def show_dashboard(self):
        self.clear_main_frame()
        income, expense, balance = self.get_totals()
        currency = self.tr("currency")

        ctk.CTkLabel(self.main_frame, text=self.tr("dashboard_title"), font=ctk.CTkFont(size=24, weight="bold")).pack(
            pady=20, padx=20, anchor="w")

        cards_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        cards_frame.pack(fill="x", padx=20)

        def create_card(parent, title, value, color):
            card = ctk.CTkFrame(parent, fg_color=color, height=100)
            card.pack(side="left", expand=True, fill="x", padx=5)
            ctk.CTkLabel(card, text=title, text_color="white", font=("Arial", 14)).pack(pady=(15, 0))
            ctk.CTkLabel(card, text=f"{currency} {value:.2f}", text_color="white", font=("Arial", 24, "bold")).pack(
                pady=(5, 15))

        create_card(cards_frame, self.tr("card_balance"), balance, "#1f6aa5")
        create_card(cards_frame, self.tr("card_income"), income, "#2cc985")
        create_card(cards_frame, self.tr("card_expense"), expense, "#c92c2c")

        ctk.CTkLabel(self.main_frame, text=self.tr("recent_header"), font=("Arial", 18)).pack(pady=(30, 10), padx=20,
                                                                                              anchor="w")

        history_frame = ctk.CTkScrollableFrame(self.main_frame, height=300)
        history_frame.pack(fill="x", padx=20, expand=True)

        self.cursor.execute("SELECT * FROM transactions ORDER BY id DESC LIMIT 15")
        rows = self.cursor.fetchall()

        if not rows:
            ctk.CTkLabel(history_frame, text=self.tr("no_data"), text_color="gray").pack(pady=20)
        else:
            for row in rows:
                t_id, t_type, cat_key, amt, date, note = row

                # Translate display data
                # If DB has old data in BG, we might need to handle it, but assuming clean slate or EN keys:

                # Resolve Category Display Name
                cat_display = self.tr(f"cat_{cat_key}")

                # Logic for colors
                # We check against EN key "Income" or "Приход" (legacy support)
                is_income = (t_type == "Income" or t_type == "Приход")

                color = "#2cc985" if is_income else "#c92c2c"
                sign = "+" if is_income else "-"

                item_frame = ctk.CTkFrame(history_frame)
                item_frame.pack(fill="x", pady=2)

                ctk.CTkLabel(item_frame, text=f"{date} | {cat_display}", anchor="w").pack(side="left", padx=10, pady=5)
                ctk.CTkLabel(item_frame, text=f"{sign}{currency} {amt:.2f}", text_color=color,
                             font=("Arial", 12, "bold")).pack(side="right", padx=10)

    def show_add_page(self):
        self.clear_main_frame()
        ctk.CTkLabel(self.main_frame, text=self.tr("add_title"), font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20,
                                                                                                                padx=20,
                                                                                                                anchor="w")

        form_frame = ctk.CTkFrame(self.main_frame)
        form_frame.pack(padx=20, pady=10, fill="both", expand=True)

        # Type Selector
        ctk.CTkLabel(form_frame, text=self.tr("lbl_type")).grid(row=0, column=0, padx=20, pady=10, sticky="w")

        # We use display names for the buttons, but need to map back to EN for logic
        type_values = [self.tr("type_Income"), self.tr("type_Expense")]
        self.type_var = ctk.StringVar(value=type_values[1])  # Default Expense
        ctk.CTkSegmentedButton(form_frame, values=type_values, variable=self.type_var).grid(row=0, column=1, padx=20,
                                                                                            pady=10, sticky="ew")

        # Amount
        ctk.CTkLabel(form_frame, text=f"{self.tr('lbl_amount')} ({self.tr('currency')}):").grid(row=1, column=0,
                                                                                                padx=20, pady=10,
                                                                                                sticky="w")
        self.entry_amount = ctk.CTkEntry(form_frame, placeholder_text="0.00")
        self.entry_amount.grid(row=1, column=1, padx=20, pady=10, sticky="ew")

        # Category
        ctk.CTkLabel(form_frame, text=self.tr("lbl_category")).grid(row=2, column=0, padx=20, pady=10, sticky="w")

        # Generate display list based on current lang
        display_cats = [self.tr(f"cat_{k}") for k in DB_CATEGORIES]

        self.combo_category = ctk.CTkComboBox(form_frame, values=display_cats)
        self.combo_category.grid(row=2, column=1, padx=20, pady=10, sticky="ew")

        # Date
        ctk.CTkLabel(form_frame, text=self.tr("lbl_date")).grid(row=3, column=0, padx=20, pady=10, sticky="w")
        self.entry_date = ctk.CTkEntry(form_frame)
        self.entry_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.entry_date.grid(row=3, column=1, padx=20, pady=10, sticky="ew")

        # Note
        ctk.CTkLabel(form_frame, text=self.tr("lbl_note")).grid(row=4, column=0, padx=20, pady=10, sticky="w")
        self.entry_note = ctk.CTkEntry(form_frame, placeholder_text="...")
        self.entry_note.grid(row=4, column=1, padx=20, pady=10, sticky="ew")

        # Save
        ctk.CTkButton(form_frame, text=self.tr("btn_save"), command=self.save_transaction, height=40).grid(row=5,
                                                                                                           column=1,
                                                                                                           padx=20,
                                                                                                           pady=30,
                                                                                                           sticky="ew")

    def show_analytics(self):
        self.clear_main_frame()
        ctk.CTkLabel(self.main_frame, text=self.tr("analytics_title"), font=ctk.CTkFont(size=24, weight="bold")).pack(
            pady=20, padx=20, anchor="w")

        # Query using Internal English Key 'Expense' (or legacy 'Разход')
        self.cursor.execute(
            "SELECT category, SUM(amount) FROM transactions WHERE type IN ('Expense', 'Разход') GROUP BY category")
        data = self.cursor.fetchall()

        if not data:
            ctk.CTkLabel(self.main_frame, text=self.tr("no_chart_data"), font=("Arial", 16)).pack(pady=50)
            return

        # Prepare data for chart
        # categories need to be translated for the chart label
        categories = []
        amounts = []

        for row in data:
            cat_key = row[0]  # This is likely English "Food" or legacy Bulgarian "Храна"
            amount = row[1]

            # Try to translate if it's an English key
            display_label = self.tr(f"cat_{cat_key}")
            # If key not in dict (e.g. legacy data), it returns f"cat_{cat_key}", so we fallback
            if display_label.startswith("cat_"):
                display_label = cat_key  # Just show the raw key if translation fails

            categories.append(display_label)
            amounts.append(amount)

        # Chart logic
        fig = plt.Figure(figsize=(6, 5), dpi=100)
        fig.patch.set_facecolor('#2b2b2b')
        ax = fig.add_subplot(111)
        ax.set_facecolor('#2b2b2b')

        wedges, texts, autotexts = ax.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=90,
                                          textprops=dict(color="white"))
        circle = plt.Circle((0, 0), 0.70, fc='#2b2b2b')
        ax.add_artist(circle)
        ax.set_title(self.tr("chart_title"), color="white", fontsize=14)

        canvas = FigureCanvasTkAgg(fig, master=self.main_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=10)

    # --- LOGIC ---

    def save_transaction(self):
        # 1. Get Display Values from UI
        display_type = self.type_var.get()
        display_cat = self.combo_category.get()
        amount = self.entry_amount.get()
        date = self.entry_date.get()
        note = self.entry_note.get()

        if not amount:
            messagebox.showwarning("Info", self.tr("msg_missing"))
            return
        try:
            amount = float(amount)
        except ValueError:
            messagebox.showerror("Error", self.tr("msg_error"))
            return

        # 2. Convert Display Values -> Internal English Keys (For DB consistency)

        # Reverse lookup for Type
        internal_type = "Expense"  # Default
        if display_type == self.tr("type_Income"): internal_type = "Income"

        # Reverse lookup for Category
        # Find which English key produces the current display_cat
        internal_cat = "Other"
        for key in DB_CATEGORIES:
            if self.tr(f"cat_{key}") == display_cat:
                internal_cat = key
                break

        # 3. Insert
        self.cursor.execute("INSERT INTO transactions (type, category, amount, date, note) VALUES (?, ?, ?, ?, ?)",
                            (internal_type, internal_cat, amount, date, note))
        self.conn.commit()

        messagebox.showinfo("Success", self.tr("msg_success"))
        self.show_dashboard()

    def get_totals(self):
        # Summing up both English keys and potential Legacy BG keys
        self.cursor.execute("SELECT SUM(amount) FROM transactions WHERE type IN ('Income', 'Приход')")
        income = self.cursor.fetchone()[0] or 0.0

        self.cursor.execute("SELECT SUM(amount) FROM transactions WHERE type IN ('Expense', 'Разход')")
        expense = self.cursor.fetchone()[0] or 0.0

        return income, expense, (income - expense)


if __name__ == "__main__":
    app = BudgetApp()
    app.mainloop()