import re
import queue
import time
from services.keycrm_service import ApiClient, insta_filter

# 🔹 Безопасный импорт логгера
try:
    import logger
    if getattr(logger, "LOG_FILE", None):
        log_message = logger.log_message
    else:
        print("⚠️ LOG_FILE не задан — используем print вместо логгера.")
        def log_message(message: str):
            print(message)
except Exception:
    print("⚠️ logger.py не найден — используем print вместо логгера.")
    def log_message(message: str):
        print(message)


class CampaignManagerTest:
    def __init__(self):
        self.client = ApiClient()
        self.queue = queue.Queue()

    def fill_queue_from_keycrm(self):
        """Получает все компании с Instagram и кладёт их в очередь"""
        log_message("🔄 Получаю данные из KeyCRM...")
        result = self.client.fetch_all_companies(include="custom_fields")

        if result.get("error"):
            log_message(f"❌ Ошибка: {result['message']}")
            return

        contacts = insta_filter(result)

        for company_id, company_name, type_professions, insta_link in contacts:
            username_match = re.search(r"instagram\.com/([A-Za-z0-9_.]+)", insta_link)
            if username_match:
                username = username_match.group(1)
                self.queue.put({
                    "company_id": company_id,
                    "company_name": company_name,
                    "type_professions": type_professions,
                    "username": username,
                    "link": insta_link
                })

        log_message(f"✅ В очередь добавлено {self.queue.qsize()} контактов")

    def show_queue(self):
        """Выводит содержимое очереди"""
        if self.queue.empty():
            log_message("⚠️ Очередь пуста — возможно, нет контактов с Instagram.")
            return

        log_message("📋 Содержимое очереди:")
        while not self.queue.empty():
            item = self.queue.get()
            print(
                f" → ID: {item['company_id']} | "
                f"{item['company_name']} | "
                f"{item['type_professions']} | "
                f"Instagram: @{item['username']} ({item['link']})"
            )
            time.sleep(0.3)


if __name__ == "__main__":
    log_message("🚀 Тестовый запуск CampaignManager")
    manager = CampaignManagerTest()
    manager.fill_queue_from_keycrm()
    manager.show_queue()
    log_message("🏁 Тест завершён.")
