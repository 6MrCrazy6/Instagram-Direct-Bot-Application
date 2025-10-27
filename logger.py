import time
from config import LOG_FILE

_gui_log_callback = None

def set_gui_logger(callback):
    """Устанавливает GUI-функцию для вывода логов в реальном времени"""
    global _gui_log_callback
    _gui_log_callback = callback

def log_message(message: str):
    """Запись логов в файл и (если есть) в GUI"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {message}"

    # --- вывод в консоль и файл ---
    print(entry)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(entry + '\n')

    # --- отправка в GUI ---
    if _gui_log_callback:
        _gui_log_callback(entry)

