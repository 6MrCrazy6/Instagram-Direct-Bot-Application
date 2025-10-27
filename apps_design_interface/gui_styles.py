from tkinter import ttk

def apply_style():
    """Применяет общий стиль интерфейса Tkinter"""
    style = ttk.Style()
    style.theme_use("clam")

    # --- Общие настройки ---
    style.configure("TFrame", background="#F8F8F8")
    style.configure("TLabel", background="#F8F8F8", font=("Segoe UI", 10))
    style.configure("TButton",
                    font=("Segoe UI", 10, "bold"),
                    padding=6,
                    relief="flat",
                    background="#F7931E",
                    foreground="white")
    style.map("TButton",
              background=[("active", "#ffa94d"), ("disabled", "#ccc")])

    # --- Настройки вкладок ---
    style.configure("TNotebook", background="#F8F8F8", borderwidth=0)
    style.configure("TNotebook.Tab",
                    font=("Segoe UI", 10, "bold"),
                    padding=[10, 6],
                    background="#EDEDED",
                    foreground="#555",
                    borderwidth=0)
    style.map("TNotebook.Tab",
              background=[("selected", "#F7931E")],
              foreground=[("selected", "white")])

    # --- Поля ввода / текст ---
    style.configure("TEntry", padding=5)
