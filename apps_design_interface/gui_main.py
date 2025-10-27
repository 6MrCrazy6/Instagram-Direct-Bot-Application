import os
import tkinter as tk
from tkinter import ttk
from apps_design_interface.gui_runner import BotRunner
from apps_design_interface.gui_loader import load_logo

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

        # 🎨 мягкая нейтральная цветовая палитра
        self.bg_color = "#E9E9E9"
        self.panel_color = "#F3F3F3"
        self.text_color = "#2C2C2C"
        self.accent_color = "#F7931E"
        self.log_bg = "#FFFFFF"
        self.log_fg = "#222222"
        self.configure(bg=self.bg_color)

        self.runner = BotRunner(self.log_message, self.toggle_pause_button)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        self.create_header()
        self.create_controls()
        self.create_log_box()
        self.create_footer()

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

    def create_controls(self):
        controls = tk.Frame(self, bg=self.bg_color)
        controls.grid(row=1, column=0, pady=10)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Gravity.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=6,
            foreground="white",
            background="#F7931E",
            borderwidth=0,
            focusthickness=3,
            focuscolor="none"
        )
        style.map(
            "Gravity.TButton",
            background=[("active", "#ff9e32"), ("disabled", "#d9d9d9")],
            foreground=[("disabled", "#999999")]
        )

        # Красная кнопка для выхода
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

    def create_log_box(self):
        container = tk.Frame(self, bg=self.bg_color)
        container.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
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

    def create_footer(self):
        footer = tk.Label(
            self, text="© 2025 Gravity | v1.0",
            bg=self.bg_color, fg="#666",
            font=("Segoe UI", 9)
        )
        footer.grid(row=3, column=0, pady=5, sticky="s")

    def log_message(self, text):
        self.log_text.insert(tk.END, text + "\n")
        self.log_text.see(tk.END)

    def clear_log(self):
        self.log_text.delete("1.0", tk.END)
        self.log_message("🧹 Логи очищены.")

    def toggle_pause_button(self, paused):
        self.pause_resume_btn.config(
            text="▶ Продолжить" if paused else "⏸ Пауза"
        )

    def exit_app(self):
        """Закрывает приложение, при желании закрывает браузер."""
        from tkinter import messagebox
        try:
            if not messagebox.askyesno("Выход", "Вы действительно хотите выйти из приложения?"):
                return  # пользователь передумал

            self.log_message("🚪 Завершение работы приложения...")

            if hasattr(self.runner, "running") and self.runner.running:
                self.runner.running = False
                self.runner.paused = False
                self.log_message("🧩 Бот остановлен пользователем.")

            driver_ref = getattr(self.runner, "driver", None)
            if driver_ref:
                close_browser = messagebox.askyesno(
                    "Закрыть браузер?",
                    "Хотите также закрыть окно Instagram (браузер)?"
                )
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

            import os, sys
            os._exit(0)

        except Exception as e:
            print(f"Ошибка при завершении: {e}")