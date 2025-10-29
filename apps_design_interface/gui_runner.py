import threading

import bot_core
from logger import set_gui_logger

class BotRunner:
    def __init__(self, log_callback, toggle_button_callback=None):
        self.log_callback = log_callback
        self.toggle_button_callback = toggle_button_callback
        self.thread = None
        self.running = False
        self.paused = False

    def start(self):
        if self.running:
            self.log_callback("⚠️ Бот уже запущен.")
            return

        self.log_callback("🚀 Запуск бота...")
        self.running = True
        self.paused = False

        set_gui_logger(self.log_callback)

        self.thread = threading.Thread(target=self.run_bot, daemon=True)
        self.thread.start()

    def run_bot(self):
        try:
            # Запуск основной логики бота
            bot_core.run_bot(self)  # Запускаем основную логику бота (рассылка)
        except Exception as e:
            self.log_callback(f"❌ Ошибка: {e}")
        finally:
            self.running = False
            if self.toggle_button_callback:
                self.toggle_button_callback(False)
            self.log_callback("✅ Завершено.")

    def toggle_pause(self):
        """Меняет состояние паузы"""
        if not self.running:
            self.log_callback("⚠️ Бот не запущен.")
            return

        self.paused = not self.paused

        if self.paused:
            self.log_callback("⏸️ Бот поставлен на паузу. Ожидание команды 'Продолжить'...")
        else:
            self.log_callback("▶️ Бот возобновил работу.")

        if self.toggle_button_callback:
            self.toggle_button_callback(self.paused)