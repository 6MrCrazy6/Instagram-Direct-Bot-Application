import os
import tkinter as tk
from tkinter import ttk
from apps_design_interface.gui_runner import BotRunner
from apps_design_interface.gui_loader import load_logo
from utils import update_env_variable
from logger import set_gui_logger

class DirectBotApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gravity — Instagram Direct Bot")
        self.geometry("850x600")
        self.minsize(700, 500)

        # === Установка иконки приложения ===
        try:
            assets_path = os.path.join(os.path.dirname(__file__), "assets")
            icon_ico = os.path.join(assets_path, "gravity.ico")

            if os.path.exists(icon_ico):
                self.iconbitmap(icon_ico)
            else:
                print("[⚠️] Иконка не найдена в папке assets.")
        except Exception as e:
            print(f"[Ошибка загрузки иконки] {e}")

        # 🎨 Цветовая палитра
        self.bg_color = "#E9E9E9"
        self.panel_color = "#F3F3F3"
        self.text_color = "#2C2C2C"
        self.accent_color = "#F7931E"
        self.log_bg = "#FFFFFF"
        self.log_fg = "#222222"
        self.configure(bg=self.bg_color)

        set_gui_logger(self.log_message)

        self.runner = BotRunner(self.log_message, self.toggle_pause_button)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.create_header()
        self.create_tabs()
        self.create_footer()

    # === HEADER ===
    def create_header(self):
        header = tk.Frame(self, bg=self.bg_color)
        header.grid(row=0, column=0, pady=(15, 5), sticky="n")

        logo = load_logo(self)
        if logo:
            logo = logo.subsample(2, 2)
            logo_label = tk.Label(header, image=logo, bg=self.bg_color)
            logo_label.image = logo
            logo_label.pack()

        tk.Label(
            header,
            text="Instagram Direct Bot",
            font=("Segoe UI", 14, "bold"),
            fg=self.accent_color,
            bg=self.bg_color
        ).pack(pady=(5, 10))

    # === ВКЛАДКИ ===
    def create_tabs(self):
        notebook = ttk.Notebook(self)
        notebook.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Главная вкладка
        main_tab = tk.Frame(notebook, bg=self.bg_color)
        notebook.add(main_tab, text="Главная")

        # Вкладка Настройки
        settings_tab = tk.Frame(notebook, bg=self.bg_color)
        notebook.add(settings_tab, text="Настройки")

        self.create_controls(main_tab)
        self.create_log_box(main_tab)
        self.create_settings_tab(settings_tab)

    # === КНОПКИ ===
    def create_controls(self, parent):
        controls = tk.Frame(parent, bg=self.bg_color)
        controls.pack(pady=10)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Gravity.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=6,
            foreground="white",
            background="#F7931E",
            borderwidth=0
        )
        style.map(
            "Gravity.TButton",
            background=[("active", "#ff9e32"), ("disabled", "#d9d9d9")],
            foreground=[("disabled", "#999999")]
        )

        style.configure(
            "Exit.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=6,
            foreground="white",
            background="#c23b22",
            borderwidth=0
        )
        style.map("Exit.TButton", background=[("active", "#e04e39")])

        def make_button(text, cmd, col, style_name="Gravity.TButton"):
            btn = ttk.Button(
                controls, text=text, command=cmd,
                style=style_name, width=20
            )
            btn.grid(row=0, column=col, padx=8)
            return btn

        self.start_btn = make_button("▶ Запустить рассылку", self.runner.start, 0)
        self.pause_resume_btn = make_button("⏸ Пауза", self.runner.toggle_pause, 1)
        make_button("🧹 Очистить лог", self.clear_log, 2)
        make_button("🚪 Выйти", self.exit_app, 3, style_name="Exit.TButton")

    # === ЛОГ ===
    def create_log_box(self, parent):
        container = tk.Frame(parent, bg=self.bg_color)
        container.pack(fill="both", expand=True, padx=20, pady=10)
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

        log_frame = tk.LabelFrame(
            container, text=" Лог работы ",
            bg=self.panel_color, fg=self.accent_color,
            font=("Segoe UI", 10, "bold"), labelanchor="n",
            relief="groove", borderwidth=1
        )
        log_frame.grid(sticky="nsew")

        self.log_text = tk.Text(
            log_frame, wrap="word",
            bg=self.log_bg, fg=self.log_fg,
            font=("Consolas", 10),
            relief="flat",
            highlightbackground="#C0C0C0",
            insertbackground=self.accent_color
        )
        self.log_text.pack(fill="both", expand=True, padx=10, pady=10)

        scrollbar = ttk.Scrollbar(self.log_text, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    # === ВКЛАДКА НАСТРОЕК ===
    def create_settings_tab(self, parent):
        # === Блок авторизации ===
        frame = tk.LabelFrame(
            parent,
            text=" Настройки авторизации ",
            bg=self.panel_color,
            fg=self.accent_color,
            font=("Segoe UI", 10, "bold"),
            labelanchor="n"
        )
        frame.pack(fill="x", padx=20, pady=20)

        # Поля для логина и пароля
        tk.Label(frame, text="Логин:", bg=self.panel_color, font=("Segoe UI", 10)).grid(row=0, column=0, padx=10,
                                                                                        pady=5, sticky="e")
        login_entry = tk.Entry(frame, width=30)
        login_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(frame, text="Пароль:", bg=self.panel_color, font=("Segoe UI", 10)).grid(row=1, column=0, padx=10,
                                                                                         pady=5, sticky="e")
        password_entry = tk.Entry(frame, width=30, show="*")
        password_entry.grid(row=1, column=1, padx=10, pady=5)

        # Кнопка "Сохранить"
        save_button = tk.Button(
            frame,
            text="💾 Сохранить",
            bg=self.accent_color,
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            width=15,
            command=lambda: self.save_auth_settings(login_entry.get(), password_entry.get())
        )
        save_button.grid(row=2, column=0, columnspan=2, pady=(10, 5))

        # === Блок "О программе" ===
        about_frame = tk.LabelFrame(
            parent,
            text=" О программе ",
            bg=self.panel_color,
            fg=self.accent_color,
            font=("Segoe UI", 10, "bold"),
            labelanchor="n"
        )
        about_frame.pack(fill="both", expand=True, padx=20, pady=(10, 20))

        # Текст с прокруткой
        text_container = tk.Frame(about_frame, bg=self.panel_color)
        text_container.pack(fill="both", expand=True, padx=10, pady=10)

        scrollbar = ttk.Scrollbar(text_container, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        about_text_widget = tk.Text(
            text_container,
            wrap="word",
            bg=self.panel_color,
            fg=self.text_color,
            font=("Segoe UI", 9),
            relief="flat",
            height=10,
            yscrollcommand=scrollbar.set
        )
        about_text_widget.pack(fill="both", expand=True)
        scrollbar.config(command=about_text_widget.yview)

        about_text = (
            'Данное приложение создано для компании "Gravity Smart Home".\n\n'
            'Это Instagram-бот, который получает данные из системы KeyCRM,\n'
            'находит соответствующие контакты в Instagram и отправляет им первое сообщение.\n'
            'После этого бот отмечает в KeyCRM, что пользователю уже было отправлено сообщение.\n\n'
            '⚠️Важно:\n'
            'Данное приложение может нарушать правила использования платформы Instagram.\n'
            'Используйте его на свой страх и риск. Разработчики не несут ответственности\n'
            'за возможные ограничения или блокировки аккаунтов.'
        )

        about_text_widget.insert("1.0", about_text)
        about_text_widget.config(state="disabled")  # запрет редактирования

    def save_auth_settings(self, login, password):
        """Сохраняем логин и пароль в .env через utils"""
        login = login.strip()
        password = password.strip()

        if not login or not password:
            self.log_message("⚠️ Введите логин и пароль перед сохранением.")
            return

        try:
            update_env_variable("INSTAGRAM_USERNAME", login)
            update_env_variable("INSTAGRAM_PASSWORD", password)
            self.log_message("✅ Данные успешно обновлены в keyes_data/password_keys_dates.env")
        except Exception as e:
            self.log_message(f"❌ Ошибка при сохранении: {e}")

    # === FOOTER ===
    def create_footer(self):
        footer = tk.Label(
            self, text="© 2025 Gravity | v1.0",
            bg=self.bg_color, fg="#666",
            font=("Segoe UI", 9)
        )
        footer.grid(row=2, column=0, pady=5, sticky="s")

    # === ПРОЧЕЕ ===
    def log_message(self, text):
        self.log_text.insert(tk.END, text + "\n")
        self.log_text.see(tk.END)

    def clear_log(self):
        self.log_text.delete("1.0", tk.END)
        self.log_message("🧹 Логи очищены.")

    def toggle_pause_button(self, paused):
        self.pause_resume_btn.config(text="▶ Продолжить" if paused else "⏸ Пауза")

    def exit_app(self):
        from tkinter import messagebox
        try:
            if not messagebox.askyesno("Выход", "Вы действительно хотите выйти из приложения?"):
                return

            self.log_message("🚪 Завершение работы приложения...")

            if hasattr(self.runner, "running") and self.runner.running:
                self.runner.running = False
                self.runner.paused = False
                self.log_message("🧩 Бот остановлен пользователем.")

            driver_ref = getattr(self.runner, "driver", None)
            if driver_ref:
                close_browser = messagebox.askyesno("Закрыть браузер?", "Хотите также закрыть окно Instagram (браузер)?")
                if close_browser:
                    try:
                        driver_ref.quit()
                        self.log_message("🌐 Браузер закрыт пользователем.")
                    except Exception as e:
                        self.log_message(f"⚠️ Не удалось закрыть браузер: {e}")
                else:
                    self.log_message("🪟 Браузер оставлен открытым по желанию пользователя.")
            else:
                self.log_message("⚠️ Браузер не был запущен или уже закрыт.")

            self.destroy()
            self.quit()

            import sys
            os._exit(0)

        except Exception as e:
            print(f"Ошибка при завершении: {e}")