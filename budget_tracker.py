import customtkinter as ctk
import sqlite3
from datetime import datetime, timedelta
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv
from tkinter import filedialog

# Тъмна тема бе
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

# Емоджита за категориите - изглежда по-яко
CATEGORY_ICONS = {
    "Food": "🍔",
    "Transport": "🚗",
    "Rent": "🏠",
    "Salary": "💰",
    "Entertainment": "🎮",
    "Shopping": "🛍️",
    "Utilities": "💡",
    "Other": "📦"
}

TRANSLATIONS = {
    "EN": {
        "app_title": "Budget Tracker",
        "nav_dashboard": "Dashboard",
        "nav_add": "Add Transaction",
        "nav_analytics": "Analytics",
        "nav_budgets": "Budget Limits",
        "nav_goals": "Goals",
        "footer": "v2.0.0\nMade with ❤️",

        "dashboard_title": "Dashboard Overview",
        "card_balance": "Total Balance",
        "card_income": "Income",
        "card_expense": "Expenses",
        "recent_header": "Recent Transactions",
        "no_data": "No transactions yet.",
        "filter_label": "Filter Period:",
        "filter_all": "All Time",
        "filter_week": "This Week",
        "filter_month": "This Month",
        "filter_year": "This Year",
        "btn_export": "Export CSV",

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
        "trend_title": "Income vs Expenses Trend",
        "no_chart_data": "Not enough data yet.",

        "budgets_title": "Budget Limits",
        "set_limit": "Set Limit",
        "current_spent": "Spent",
        "limit": "Limit",
        "no_limit": "No limit set",

        "goals_title": "Savings Goals",
        "goal_name": "Goal Name",
        "goal_target": "Target Amount",
        "goal_current": "Current Saved",
        "add_goal": "Add Goal",
        "progress": "Progress",

        "msg_missing": "Please enter an amount.",
        "msg_error": "Amount must be a number.",
        "msg_success": "Transaction added successfully!",
        "msg_deleted": "Transaction deleted!",
        "msg_budget_warning": "⚠️ You're over budget!",

        "edit": "Edit",
        "delete": "Delete",
        "cancel": "Cancel",

        "cat_Food": "Food",
        "cat_Transport": "Transport",
        "cat_Rent": "Rent",
        "cat_Salary": "Salary",
        "cat_Entertainment": "Entertainment",
        "cat_Shopping": "Shopping",
        "cat_Utilities": "Utilities",
        "cat_Other": "Other",

        "type_Income": "Income",
        "type_Expense": "Expense"
    },
    "BG": {
        "app_title": "Budget Tracker",
        "nav_dashboard": "Табло",
        "nav_add": "Добави",
        "nav_analytics": "Статистика",
        "nav_budgets": "Бюджети",
        "nav_goals": "Цели",
        "footer": "v2.0.0\nСъздадено с ❤️",

        "dashboard_title": "Общ Преглед",
        "card_balance": "Текущ Баланс",
        "card_income": "Приходи",
        "card_expense": "Разходи",
        "recent_header": "Последни Транзакции",
        "no_data": "Няма записи.",
        "filter_label": "Филтър период:",
        "filter_all": "Всички",
        "filter_week": "Тази седмица",
        "filter_month": "Този месец",
        "filter_year": "Тази година",
        "btn_export": "Експорт CSV",

        "add_title": "Добави Транзакция",
        "lbl_type": "Тип",
        "lbl_amount": "Сума",
        "lbl_category": "Категория",
        "lbl_date": "Дата (ГГГГ-ММ-ДД)",
        "lbl_note": "Бележка",
        "btn_save": "Запази",
        "currency": "лв.",

        "analytics_title": "Анализ",
        "chart_title": "Разходи по Категория",
        "trend_title": "Тренд Приходи/Разходи",
        "no_chart_data": "Няма данни.",

        "budgets_title": "Бюджет Лимити",
        "set_limit": "Задай лимит",
        "current_spent": "Похарчено",
        "limit": "Лимит",
        "no_limit": "Няма лимит",

        "goals_title": "Цели за спестявания",
        "goal_name": "Име на цел",
        "goal_target": "Целева сума",
        "goal_current": "Спестено",
        "add_goal": "Добави цел",
        "progress": "Прогрес",

        "msg_missing": "Въведи сума.",
        "msg_error": "Сумата трябва да е число.",
        "msg_success": "Добавено успешно!",
        "msg_deleted": "Изтрито!",
        "msg_budget_warning": "⚠️ Надхвърли си бюджета!",

        "edit": "Редактирай",
        "delete": "Изтрий",
        "cancel": "Отказ",

        "cat_Food": "Храна",
        "cat_Transport": "Транспорт",
        "cat_Rent": "Наем",
        "cat_Salary": "Заплата",
        "cat_Entertainment": "Забавление",
        "cat_Shopping": "Пазаруване",
        "cat_Utilities": "Сметки",
        "cat_Other": "Други",

        "type_Income": "Приход",
        "type_Expense": "Разход"
    }
}

DB_CATEGORIES = ["Food", "Transport", "Rent", "Salary", "Entertainment", "Shopping", "Utilities", "Other"]


class BudgetApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.current_lang = "EN"
        self.current_filter = "all"  # за филтрите

        self.title("Budget Tracker Pro")
        self.geometry("1100x700")

        self.init_db()

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Sidebar
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(7, weight=1)

        # Logo с градиент ефект (емулиран)
        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="💎",
            font=ctk.CTkFont(size=50, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 5))

        self.brand_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="Budget Tracker Pro",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        self.brand_label.grid(row=1, column=0, padx=20, pady=(0, 20))

        # Navigation бутони
        self.btn_dashboard = ctk.CTkButton(
            self.sidebar_frame,
            command=self.show_dashboard,
            height=40,
            corner_radius=10
        )
        self.btn_dashboard.grid(row=2, column=0, padx=20, pady=8)

        self.btn_add = ctk.CTkButton(
            self.sidebar_frame,
            command=self.show_add_page,
            height=40,
            corner_radius=10
        )
        self.btn_add.grid(row=3, column=0, padx=20, pady=8)

        self.btn_analytics = ctk.CTkButton(
            self.sidebar_frame,
            command=self.show_analytics,
            height=40,
            corner_radius=10
        )
        self.btn_analytics.grid(row=4, column=0, padx=20, pady=8)

        self.btn_budgets = ctk.CTkButton(
            self.sidebar_frame,
            command=self.show_budgets,
            height=40,
            corner_radius=10
        )
        self.btn_budgets.grid(row=5, column=0, padx=20, pady=8)

        self.btn_goals = ctk.CTkButton(
            self.sidebar_frame,
            command=self.show_goals,
            height=40,
            corner_radius=10
        )
        self.btn_goals.grid(row=6, column=0, padx=20, pady=8)

        # Language switcher
        self.lang_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="🌍 Language",
            text_color="gray",
            font=("Arial", 10)
        )
        self.lang_label.grid(row=8, column=0, padx=20, pady=(10, 0))

        self.lang_switch = ctk.CTkSegmentedButton(
            self.sidebar_frame,
            values=["EN", "BG"],
            command=self.change_language
        )
        self.lang_switch.set("EN")
        self.lang_switch.grid(row=9, column=0, padx=20, pady=(5, 15))

        # Footer
        self.label_footer = ctk.CTkLabel(
            self.sidebar_frame,
            text_color="gray",
            font=("Arial", 9)
        )
        self.label_footer.grid(row=10, column=0, padx=20, pady=20)

        # Main Content Area
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.update_sidebar_text()
        self.show_dashboard()

    def init_db(self):
        # Основна таблица за транзакции
        self.conn = sqlite3.connect("my_budget.db")
        self.cursor = self.conn.cursor()

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT,
                category TEXT,
                amount REAL,
                date TEXT,
                note TEXT
            )
        """)

        # Таблица за бюджет лимити
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS budget_limits (
                category TEXT PRIMARY KEY,
                limit_amount REAL
            )
        """)

        # Таблица за цели
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS savings_goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                target_amount REAL,
                current_amount REAL DEFAULT 0
            )
        """)

        self.conn.commit()

    def tr(self, key):
        return TRANSLATIONS[self.current_lang].get(key, key)

    def change_language(self, value):
        self.current_lang = value
        self.update_sidebar_text()
        self.show_dashboard()

    def update_sidebar_text(self):
        self.title(self.tr("app_title"))
        self.brand_label.configure(text=self.tr("app_title"))
        self.btn_dashboard.configure(text="📊 " + self.tr("nav_dashboard"))
        self.btn_add.configure(text="➕ " + self.tr("nav_add"))
        self.btn_analytics.configure(text="📈 " + self.tr("nav_analytics"))
        self.btn_budgets.configure(text="💳 " + self.tr("nav_budgets"))
        self.btn_goals.configure(text="🎯 " + self.tr("nav_goals"))
        self.label_footer.configure(text=self.tr("footer"))

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    # ============ DASHBOARD PAGE ============
    def show_dashboard(self):
        self.clear_main_frame()

        # Header с филтри
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            header_frame,
            text=self.tr("dashboard_title"),
            font=ctk.CTkFont(size=28, weight="bold")
        ).pack(side="left")

        # Филтър меню
        filter_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        filter_frame.pack(side="right")

        ctk.CTkLabel(
            filter_frame,
            text=self.tr("filter_label"),
            font=("Arial", 11)
        ).pack(side="left", padx=(0, 10))

        filter_values = [
            self.tr("filter_all"),
            self.tr("filter_week"),
            self.tr("filter_month"),
            self.tr("filter_year")
        ]

        self.filter_menu = ctk.CTkOptionMenu(
            filter_frame,
            values=filter_values,
            command=self.on_filter_change,
            width=150
        )
        self.filter_menu.set(self.tr("filter_all"))
        self.filter_menu.pack(side="left", padx=5)

        # Export бутон
        ctk.CTkButton(
            filter_frame,
            text=self.tr("btn_export"),
            command=self.export_to_csv,
            width=120,
            height=32
        ).pack(side="left", padx=5)

        # Stats карти
        income, expense, balance = self.get_totals_filtered()
        currency = self.tr("currency")

        cards_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        cards_frame.pack(fill="x", padx=20, pady=10)

        self.create_stat_card(cards_frame, self.tr("card_balance"), balance, "#1f6aa5", "💰")
        self.create_stat_card(cards_frame, self.tr("card_income"), income, "#2cc985", "📈")
        self.create_stat_card(cards_frame, self.tr("card_expense"), expense, "#c92c2c", "📉")

        # Recent транзакции
        ctk.CTkLabel(
            self.main_frame,
            text=self.tr("recent_header"),
            font=("Arial", 20, "bold")
        ).pack(pady=(20, 10), padx=20, anchor="w")

        history_frame = ctk.CTkScrollableFrame(self.main_frame, height=350)
        history_frame.pack(fill="both", padx=20, expand=True)

        # Вземаме транзакциите според филтъра
        query = "SELECT * FROM transactions"
        date_filter = self.get_date_filter()

        if date_filter:
            query += f" WHERE date >= '{date_filter}'"

        query += " ORDER BY date DESC, id DESC LIMIT 20"

        self.cursor.execute(query)
        rows = self.cursor.fetchall()

        if not rows:
            ctk.CTkLabel(
                history_frame,
                text=self.tr("no_data"),
                text_color="gray",
                font=("Arial", 14)
            ).pack(pady=30)
        else:
            for row in rows:
                self.create_transaction_item(history_frame, row)

    def create_stat_card(self, parent, title, value, color, icon):
        """Прави яка картичка със статистика"""
        card = ctk.CTkFrame(parent, fg_color=color, height=120, corner_radius=15)
        card.pack(side="left", expand=True, fill="x", padx=8)

        ctk.CTkLabel(
            card,
            text=icon,
            font=("Arial", 32)
        ).pack(pady=(20, 5))

        ctk.CTkLabel(
            card,
            text=title,
            text_color="white",
            font=("Arial", 13)
        ).pack()

        currency = self.tr("currency")
        ctk.CTkLabel(
            card,
            text=f"{currency} {value:.2f}",
            text_color="white",
            font=("Arial", 26, "bold")
        ).pack(pady=(5, 20))

    def create_transaction_item(self, parent, row):
        """Създава един ред за транзакция с контекст меню за edit/delete"""
        t_id, t_type, cat_key, amt, date, note = row

        cat_display = self.tr(f"cat_{cat_key}")
        icon = CATEGORY_ICONS.get(cat_key, "📦")

        is_income = (t_type == "Income")
        color = "#2cc985" if is_income else "#c92c2c"
        sign = "+" if is_income else "-"

        item_frame = ctk.CTkFrame(parent, corner_radius=10)
        item_frame.pack(fill="x", pady=4, padx=5)

        left_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        left_frame.pack(side="left", padx=15, pady=10, fill="x", expand=True)

        ctk.CTkLabel(
            left_frame,
            text=f"{icon} {cat_display}",
            font=("Arial", 13, "bold"),
            anchor="w"
        ).pack(anchor="w")

        ctk.CTkLabel(
            left_frame,
            text=f"{date} • {note}" if note else date,
            font=("Arial", 10),
            text_color="gray",
            anchor="w"
        ).pack(anchor="w")

        currency = self.tr("currency")
        amount_label = ctk.CTkLabel(
            item_frame,
            text=f"{sign}{currency} {amt:.2f}",
            text_color=color,
            font=("Arial", 16, "bold")
        )
        amount_label.pack(side="right", padx=15)

        item_frame.bind("<Button-3>", lambda e: self.show_context_menu(e, t_id))

    def show_context_menu(self, event, transaction_id):
        """Показва context menu за редакция или изтриване"""
        menu = ctk.CTkToplevel(self)
        menu.overrideredirect(True)
        menu.geometry(f"150x80+{event.x_root}+{event.y_root}")

        ctk.CTkButton(
            menu,
            text=self.tr("delete"),
            command=lambda: self.delete_transaction(transaction_id, menu),
            fg_color="#c92c2c",
            hover_color="#a82424"
        ).pack(padx=10, pady=(10, 5), fill="x")

        ctk.CTkButton(
            menu,
            text=self.tr("cancel"),
            command=menu.destroy,
            fg_color="gray"
        ).pack(padx=10, pady=(5, 10), fill="x")

        menu.bind("<FocusOut>", lambda e: menu.destroy())
        menu.focus()

    def delete_transaction(self, transaction_id, menu):
        """Трие транзакция"""
        self.cursor.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
        self.conn.commit()
        menu.destroy()
        messagebox.showinfo("Success", self.tr("msg_deleted"))
        self.show_dashboard()

    def on_filter_change(self, value):
        """Смяна на филтъра"""
        filters_map = {
            self.tr("filter_all"): "all",
            self.tr("filter_week"): "week",
            self.tr("filter_month"): "month",
            self.tr("filter_year"): "year"
        }
        self.current_filter = filters_map.get(value, "all")
        self.show_dashboard()

    def get_date_filter(self):
        """Връща SQL date filter според избрания период"""
        if self.current_filter == "all":
            return None

        today = datetime.now()

        if self.current_filter == "week":
            date = today - timedelta(days=7)
        elif self.current_filter == "month":
            date = today - timedelta(days=30)
        elif self.current_filter == "year":
            date = today - timedelta(days=365)
        else:
            return None

        return date.strftime("%Y-%m-%d")

    def get_totals_filtered(self):
        """Взима total-ите според филтъра"""
        date_filter = self.get_date_filter()
        where_clause = f" WHERE date >= '{date_filter}'" if date_filter else ""
        where_clause = where_clause.strip() if where_clause else ""

        if not where_clause:
            where_clause = "WHERE 1=1"
        elif not where_clause.upper().startswith("WHERE"):
            where_clause = "WHERE " + where_clause

        query = f"""
            SELECT SUM(amount)
            FROM transactions
            {where_clause}
            AND type IN ('Income', 'Приход')
        """

        # FIX: няма нужда от params тук
        self.cursor.execute(query)
        row = self.cursor.fetchone()
        income = float(row[0]) if row and row[0] is not None else 0.0

        # FIX: добавен интервал след 'transactions '
        self.cursor.execute(
            f"SELECT SUM(amount) FROM transactions {where_clause} AND type IN ('Expense', 'Разход')"
        )
        expense = self.cursor.fetchone()[0] or 0.0

        return income, expense, (income - expense)

    def export_to_csv(self):
        """Експортва транзакциите в CSV"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )

        if not file_path:
            return

        self.cursor.execute("SELECT * FROM transactions ORDER BY date DESC")
        rows = self.cursor.fetchall()

        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'Type', 'Category', 'Amount', 'Date', 'Note'])
            writer.writerows(rows)

        messagebox.showinfo("Success", f"Exported to {file_path}")

    # ============ ADD TRANSACTION PAGE ============
    def show_add_page(self):
        self.clear_main_frame()

        ctk.CTkLabel(
            self.main_frame,
            text=self.tr("add_title"),
            font=ctk.CTkFont(size=28, weight="bold")
        ).pack(pady=20, padx=20, anchor="w")

        form_frame = ctk.CTkFrame(self.main_frame)
        form_frame.pack(padx=20, pady=10, fill="both", expand=True)

        form_frame.grid_columnconfigure(1, weight=1)

        # Type
        ctk.CTkLabel(form_frame, text=self.tr("lbl_type"), font=("Arial", 13)).grid(
            row=0, column=0, padx=20, pady=15, sticky="w"
        )

        type_values = [self.tr("type_Income"), self.tr("type_Expense")]
        self.type_var = ctk.StringVar(value=type_values[1])
        ctk.CTkSegmentedButton(
            form_frame,
            values=type_values,
            variable=self.type_var
        ).grid(row=0, column=1, padx=20, pady=15, sticky="ew")

        # Amount
        ctk.CTkLabel(
            form_frame,
            text=f"{self.tr('lbl_amount')} ({self.tr('currency')}):",
            font=("Arial", 13)
        ).grid(row=1, column=0, padx=20, pady=15, sticky="w")

        self.entry_amount = ctk.CTkEntry(
            form_frame,
            placeholder_text="0.00",
            height=40,
            font=("Arial", 14)
        )
        self.entry_amount.grid(row=1, column=1, padx=20, pady=15, sticky="ew")

        # Category
        ctk.CTkLabel(form_frame, text=self.tr("lbl_category"), font=("Arial", 13)).grid(
            row=2, column=0, padx=20, pady=15, sticky="w"
        )

        display_cats = [f"{CATEGORY_ICONS.get(k, '📦')} {self.tr(f'cat_{k}')}" for k in DB_CATEGORIES]

        self.combo_category = ctk.CTkComboBox(
            form_frame,
            values=display_cats,
            height=40
        )
        self.combo_category.grid(row=2, column=1, padx=20, pady=15, sticky="ew")

        # Date
        ctk.CTkLabel(form_frame, text=self.tr("lbl_date"), font=("Arial", 13)).grid(
            row=3, column=0, padx=20, pady=15, sticky="w"
        )

        self.entry_date = ctk.CTkEntry(form_frame, height=40, font=("Arial", 13))
        self.entry_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.entry_date.grid(row=3, column=1, padx=20, pady=15, sticky="ew")

        # Note
        ctk.CTkLabel(form_frame, text=self.tr("lbl_note"), font=("Arial", 13)).grid(
            row=4, column=0, padx=20, pady=15, sticky="w"
        )

        self.entry_note = ctk.CTkEntry(
            form_frame,
            placeholder_text="...",
            height=40,
            font=("Arial", 13)
        )
        self.entry_note.grid(row=4, column=1, padx=20, pady=15, sticky="ew")

        # Save бутон
        ctk.CTkButton(
            form_frame,
            text=self.tr("btn_save"),
            command=self.save_transaction,
            height=50,
            font=("Arial", 15, "bold"),
            corner_radius=12
        ).grid(row=5, column=1, padx=20, pady=30, sticky="ew")

    def save_transaction(self):
        display_type = self.type_var.get()
        display_cat_with_icon = self.combo_category.get()
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

        display_cat = display_cat_with_icon.split(" ", 1)[-1]

        internal_type = "Expense"
        if display_type == self.tr("type_Income"):
            internal_type = "Income"

        internal_cat = "Other"
        for key in DB_CATEGORIES:
            if self.tr(f"cat_{key}") == display_cat:
                internal_cat = key
                break

        self.cursor.execute(
            "INSERT INTO transactions (type, category, amount, date, note) VALUES (?, ?, ?, ?, ?)",
            (internal_type, internal_cat, amount, date, note)
        )
        self.conn.commit()

        if internal_type == "Expense":
            self.check_budget_limit(internal_cat)

        messagebox.showinfo("Success", self.tr("msg_success"))
        self.show_dashboard()

    def check_budget_limit(self, category):
        """Проверява дали сме надхвърлили бюджета"""
        self.cursor.execute(
            "SELECT limit_amount FROM budget_limits WHERE category = ?",
            (category,)
        )
        result = self.cursor.fetchone()

        if not result:
            return

        limit = result[0]

        date_filter = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        self.cursor.execute(
            """SELECT SUM(amount) FROM transactions 
               WHERE category = ? AND type = 'Expense' AND date >= ?""",
            (category, date_filter)
        )

        spent = self.cursor.fetchone()[0] or 0.0

        if spent > limit:
            messagebox.showwarning(
                self.tr("msg_budget_warning"),
                f"{self.tr(f'cat_{category}')}: {self.tr('current_spent')} {spent:.2f} / {self.tr('limit')} {limit:.2f}"
            )

    # ============ ANALYTICS PAGE ============
    def show_analytics(self):
        self.clear_main_frame()

        ctk.CTkLabel(
            self.main_frame,
            text=self.tr("analytics_title"),
            font=ctk.CTkFont(size=28, weight="bold")
        ).pack(pady=20, padx=20, anchor="w")

        self.show_category_pie_chart()
        self.show_trend_chart()

    def show_category_pie_chart(self):
        """Pie chart за разходи по категории"""
        self.cursor.execute(
            "SELECT category, SUM(amount) FROM transactions WHERE type IN ('Expense', 'Разход') GROUP BY category"
        )
        data = self.cursor.fetchall()

        if not data:
            ctk.CTkLabel(
                self.main_frame,
                text=self.tr("no_chart_data"),
                font=("Arial", 14),
                text_color="gray"
            ).pack(pady=20)
            return

        categories = []
        amounts = []

        for row in data:
            cat_key = row[0]
            amount = row[1]

            icon = CATEGORY_ICONS.get(cat_key, "📦")
            display_label = f"{icon} {self.tr(f'cat_{cat_key}')}"

            categories.append(display_label)
            amounts.append(amount)

        chart_frame = ctk.CTkFrame(self.main_frame)
        chart_frame.pack(fill="both", expand=True, padx=20, pady=10)

        fig = plt.Figure(figsize=(7, 4), dpi=100)
        fig.patch.set_facecolor('#2b2b2b')
        ax = fig.add_subplot(111)
        ax.set_facecolor('#2b2b2b')

        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E2']

        wedges, texts, autotexts = ax.pie(
            amounts,
            labels=categories,
            autopct='%1.1f%%',
            startangle=90,
            colors=colors[:len(amounts)],
            textprops=dict(color="white", size=10)
        )

        circle = plt.Circle((0, 0), 0.70, fc='#2b2b2b')
        ax.add_artist(circle)
        ax.set_title(self.tr("chart_title"), color="white", fontsize=14, pad=20)

        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def show_trend_chart(self):
        """Line chart за тренд на приходи vs разходи по време"""
        self.cursor.execute("""
            SELECT 
                strftime('%Y-%m', date) as month,
                SUM(CASE WHEN type = 'Income' THEN amount ELSE 0 END) as income,
                SUM(CASE WHEN type = 'Expense' THEN amount ELSE 0 END) as expense
            FROM transactions
            WHERE date >= date('now', '-12 months')
            GROUP BY month
            ORDER BY month
        """)

        data = self.cursor.fetchall()

        if len(data) < 2:
            return

        months = [row[0] for row in data]
        incomes = [row[1] for row in data]
        expenses = [row[2] for row in data]

        chart_frame = ctk.CTkFrame(self.main_frame)
        chart_frame.pack(fill="both", expand=True, padx=20, pady=(10, 20))

        fig = plt.Figure(figsize=(10, 3), dpi=100)
        fig.patch.set_facecolor('#2b2b2b')
        ax = fig.add_subplot(111)
        ax.set_facecolor('#2b2b2b')

        ax.plot(months, incomes, marker='o', color='#2cc985', linewidth=2, label=self.tr("card_income"))
        ax.plot(months, expenses, marker='o', color='#c92c2c', linewidth=2, label=self.tr("card_expense"))

        ax.set_title(self.tr("trend_title"), color="white", fontsize=12, pad=15)
        ax.tick_params(colors='white')
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.legend(facecolor='#2b2b2b', edgecolor='white', labelcolor='white')
        ax.grid(True, alpha=0.2)

        plt.xticks(rotation=45)
        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    # ============ BUDGETS PAGE ============
    def show_budgets(self):
        self.clear_main_frame()

        ctk.CTkLabel(
            self.main_frame,
            text=self.tr("budgets_title"),
            font=ctk.CTkFont(size=28, weight="bold")
        ).pack(pady=20, padx=20, anchor="w")

        scroll_frame = ctk.CTkScrollableFrame(self.main_frame, height=500)
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)

        for category in DB_CATEGORIES:
            if category == "Salary":
                continue
            self.create_budget_card(scroll_frame, category)

    def create_budget_card(self, parent, category):
        """Картичка за бюджет лимит на категория"""
        card = ctk.CTkFrame(parent, corner_radius=12)
        card.pack(fill="x", pady=10, padx=10)

        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(15, 10))

        icon = CATEGORY_ICONS.get(category, "📦")
        cat_name = self.tr(f"cat_{category}")

        ctk.CTkLabel(
            header,
            text=f"{icon} {cat_name}",
            font=("Arial", 16, "bold")
        ).pack(side="left")

        self.cursor.execute(
            "SELECT limit_amount FROM budget_limits WHERE category = ?",
            (category,)
        )
        result = self.cursor.fetchone()
        current_limit = result[0] if result else 0.0

        date_filter = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        self.cursor.execute(
            """SELECT SUM(amount) FROM transactions 
               WHERE category = ? AND type = 'Expense' AND date >= ?""",
            (category, date_filter)
        )
        spent = self.cursor.fetchone()[0] or 0.0

        if current_limit > 0:
            percentage = (spent / current_limit) * 100
            color = "#2cc985" if percentage < 80 else ("#FFA07A" if percentage < 100 else "#c92c2c")

            status_label = ctk.CTkLabel(
                header,
                text=f"{percentage:.0f}%",
                text_color=color,
                font=("Arial", 14, "bold")
            )
            status_label.pack(side="right")

        if current_limit > 0:
            progress = min(spent / current_limit, 1.0)
            progress_bar = ctk.CTkProgressBar(card, height=8)
            progress_bar.pack(fill="x", padx=20, pady=(0, 10))
            progress_bar.set(progress)

        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(fill="x", padx=20, pady=(0, 15))

        currency = self.tr("currency")

        ctk.CTkLabel(
            info_frame,
            text=f"{self.tr('current_spent')}: {currency} {spent:.2f}",
            font=("Arial", 12),
            text_color="gray"
        ).pack(side="left")

        if current_limit > 0:
            ctk.CTkLabel(
                info_frame,
                text=f"{self.tr('limit')}: {currency} {current_limit:.2f}",
                font=("Arial", 12),
                text_color="gray"
            ).pack(side="right")
        else:
            ctk.CTkLabel(
                info_frame,
                text=self.tr("no_limit"),
                font=("Arial", 11),
                text_color="gray"
            ).pack(side="right")

        input_frame = ctk.CTkFrame(card, fg_color="transparent")
        input_frame.pack(fill="x", padx=20, pady=(0, 15))

        limit_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text=f"{current_limit:.2f}" if current_limit > 0 else "0.00",
            width=150,
            height=35
        )
        limit_entry.pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            input_frame,
            text=self.tr("set_limit"),
            command=lambda: self.set_budget_limit(category, limit_entry.get()),
            width=120,
            height=35
        ).pack(side="left")

    def set_budget_limit(self, category, limit_str):
        """Задава бюджет лимит за категория"""
        try:
            limit = float(limit_str)
            if limit < 0:
                raise ValueError
        except:
            messagebox.showerror("Error", self.tr("msg_error"))
            return

        self.cursor.execute(
            "INSERT OR REPLACE INTO budget_limits (category, limit_amount) VALUES (?, ?)",
            (category, limit)
        )
        self.conn.commit()

        messagebox.showinfo("Success", f"Limit set: {limit}")
        self.show_budgets()

    # ============ GOALS PAGE ============
    def show_goals(self):
        self.clear_main_frame()

        ctk.CTkLabel(
            self.main_frame,
            text=self.tr("goals_title"),
            font=ctk.CTkFont(size=28, weight="bold")
        ).pack(pady=20, padx=20, anchor="w")

        add_frame = ctk.CTkFrame(self.main_frame)
        add_frame.pack(fill="x", padx=20, pady=(0, 20))

        form = ctk.CTkFrame(add_frame, fg_color="transparent")
        form.pack(fill="x", padx=20, pady=20)

        self.goal_name_entry = ctk.CTkEntry(
            form,
            placeholder_text=self.tr("goal_name"),
            width=200,
            height=40
        )
        self.goal_name_entry.pack(side="left", padx=(0, 10))

        self.goal_target_entry = ctk.CTkEntry(
            form,
            placeholder_text=self.tr("goal_target"),
            width=150,
            height=40
        )
        self.goal_target_entry.pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            form,
            text=self.tr("add_goal"),
            command=self.add_savings_goal,
            height=40,
            width=150
        ).pack(side="left")

        goals_scroll = ctk.CTkScrollableFrame(self.main_frame, height=400)
        goals_scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.cursor.execute("SELECT * FROM savings_goals")
        goals = self.cursor.fetchall()

        if not goals:
            ctk.CTkLabel(
                goals_scroll,
                text="No goals yet. Create one! 🎯",
                font=("Arial", 14),
                text_color="gray"
            ).pack(pady=30)
        else:
            for goal in goals:
                self.create_goal_card(goals_scroll, goal)

    def create_goal_card(self, parent, goal):
        """Картичка за savings goal"""
        goal_id, name, target, current = goal

        card = ctk.CTkFrame(parent, corner_radius=12)
        card.pack(fill="x", pady=10, padx=10)

        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkLabel(
            header,
            text=f"🎯 {name}",
            font=("Arial", 18, "bold")
        ).pack(side="left")

        percentage = (current / target * 100) if target > 0 else 0
        color = "#2cc985" if percentage >= 100 else "#FFA07A"

        ctk.CTkLabel(
            header,
            text=f"{percentage:.0f}%",
            font=("Arial", 16, "bold"),
            text_color=color
        ).pack(side="right")

        progress_bar = ctk.CTkProgressBar(card, height=12)
        progress_bar.pack(fill="x", padx=20, pady=(0, 15))
        progress_bar.set(min(current / target, 1.0) if target > 0 else 0)

        currency = self.tr("currency")

        amounts_frame = ctk.CTkFrame(card, fg_color="transparent")
        amounts_frame.pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkLabel(
            amounts_frame,
            text=f"{self.tr('goal_current')}: {currency} {current:.2f}",
            font=("Arial", 13)
        ).pack(side="left")

        ctk.CTkLabel(
            amounts_frame,
            text=f"{self.tr('goal_target')}: {currency} {target:.2f}",
            font=("Arial", 13)
        ).pack(side="right")

        update_frame = ctk.CTkFrame(card, fg_color="transparent")
        update_frame.pack(fill="x", padx=20, pady=(0, 20))

        amount_entry = ctk.CTkEntry(
            update_frame,
            placeholder_text="Add amount...",
            width=120,
            height=35
        )
        amount_entry.pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            update_frame,
            text="➕ Add",
            command=lambda: self.update_goal_amount(goal_id, amount_entry.get()),
            width=80,
            height=35,
            fg_color="#2cc985"
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            update_frame,
            text="🗑️",
            command=lambda: self.delete_goal(goal_id),
            width=40,
            height=35,
            fg_color="#c92c2c"
        ).pack(side="right")

    def add_savings_goal(self):
        """Добавя нова savings goal"""
        name = self.goal_name_entry.get()
        target_str = self.goal_target_entry.get()

        if not name or not target_str:
            messagebox.showwarning("Info", "Please fill all fields")
            return

        try:
            target = float(target_str)
            if target <= 0:
                raise ValueError
        except:
            messagebox.showerror("Error", self.tr("msg_error"))
            return

        self.cursor.execute(
            "INSERT INTO savings_goals (name, target_amount, current_amount) VALUES (?, ?, 0)",
            (name, target)
        )
        self.conn.commit()

        self.goal_name_entry.delete(0, 'end')
        self.goal_target_entry.delete(0, 'end')

        messagebox.showinfo("Success", f"Goal '{name}' created!")
        self.show_goals()

    def update_goal_amount(self, goal_id, amount_str):
        """Добавя сума към savings goal"""
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except:
            messagebox.showerror("Error", self.tr("msg_error"))
            return

        self.cursor.execute(
            "UPDATE savings_goals SET current_amount = current_amount + ? WHERE id = ?",
            (amount, goal_id)
        )
        self.conn.commit()

        messagebox.showinfo("Success", f"Added {amount} to goal!")
        self.show_goals()

    def delete_goal(self, goal_id):
        """Трие savings goal"""
        self.cursor.execute("DELETE FROM savings_goals WHERE id = ?", (goal_id,))
        self.conn.commit()
        messagebox.showinfo("Success", "Goal deleted!")
        self.show_goals()

    def get_totals(self):
        """Взима общите totals (за backward compatibility)"""
        self.cursor.execute("SELECT SUM(amount) FROM transactions WHERE type IN ('Income', 'Приход')")
        income = self.cursor.fetchone()[0] or 0.0

        self.cursor.execute("SELECT SUM(amount) FROM transactions WHERE type IN ('Expense', 'Разход')")
        expense = self.cursor.fetchone()[0] or 0.0

        return income, expense, (income - expense)


if __name__ == "__main__":
    app = BudgetApp()
    app.mainloop()
