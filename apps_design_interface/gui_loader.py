import os
from tkinter import PhotoImage

def load_logo(master=None):
    """Загрузка логотипа из папки assets"""
    try:
        logo_path = os.path.join(os.path.dirname(__file__), 'assets', 'Logo_Orange.png')
        if os.path.exists(logo_path):
            return PhotoImage(file=logo_path, master=master)
        else:
            print("⚠️ Логотип не найден:", logo_path)
            return None
    except Exception as e:
        print("Ошибка загрузки логотипа:", e)
        return None
