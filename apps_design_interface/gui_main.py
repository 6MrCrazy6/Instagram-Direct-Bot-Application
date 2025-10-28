import os
import tkinter as tk
from tkinter import ttk
from apps_design_interface.gui_runner import BotRunner
from apps_design_interface.gui_loader import load_logo
from utils import update_env_variable  # ✅ импортируем твою функцию


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
        frame = tk.LabelFrame(
            parent, text=" Настройки авторизации ",
            bg=self.panel_color, fg=self.accent_color,
            font=("Segoe UI", 10, "bold"), labelanchor="n"
        )
        frame.pack(fill="x", padx=20, pady=20)

        tk.Label(frame, text="Логин Instagram:", bg=self.panel_color, font=("Segoe UI", 10)).grid(
            row=0, column=0, padx=10, pady=5, sticky="w"
        )
        self.login_entry = tk.Entry(frame, width=30)
        self.login_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(frame, text="Пароль Instagram:", bg=self.panel_color, font=("Segoe UI", 10)).grid(
            row=1, column=0, padx=10, pady=5, sticky="w"
        )
        self.password_entry = tk.Entry(frame, width=30, show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=5)

        save_btn = ttk.Button(
            frame, text="💾 Сохранить изменения",
            style="Gravity.TButton", command=self.save_env_settings
        )
        save_btn.grid(row=2, column=0, columnspan=2, pady=10)

        self.status_label = tk.Label(frame, text="", bg=self.panel_color, fg="#555", font=("Segoe UI", 9))
        self.status_label.grid(row=3, column=0, columnspan=2, pady=(0, 5))

    def save_env_settings(self):
        login = self.login_entry.get().strip()
        password = self.password_entry.get().strip()

        if not login or not password:
            self.status_label.config(text="⚠️ Введите логин и пароль", fg="#c23b22")
            return

        try:
            # ✅ обновляем данные через utils.update_env_variable
            update_env_variable("INSTAGRAM_USERNAME", login)
            update_env_variable("INSTAGRAM_PASSWORD", password)

            self.status_label.config(text="✅ Данные успешно обновлены", fg="green")
            self.log_message("🔑 Логин и пароль успешно обновлены в .env")

        except Exception as e:
            self.status_label.config(text=f"❌ Ошибка: {e}", fg="#c23b22")

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