import os
import re
import queue
import time
from services.keycrm_service import ApiClient, insta_filter, start_date, end_date

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
        self.client = ApiClient(str(os.getenv("KEYCRM_API_KEY")), str(os.getenv("API_BASE_URL")))
        self.queue = queue.Queue()
        pipeline_ids = [1, 3, 16, 20, 31, 2, 4, 15, 19, 32, 22, 24, 26, 30, 33, 46, 18]
        self.pipeline_ids = pipeline_ids

    def fill_queue_from_keycrm(self):
        """Получает все компании с Instagram и кладёт их в очередь"""
        log_message("🔄 Получаю данные из KeyCRM...")
        cards = self.client.fetch_all_pipeline_cards(self.pipeline_ids, date=(start_date, end_date), include="contact.client")
        companies = self.client.fetch_all_companies(date=(start_date, end_date), include="custom_fields")

        if companies.get("error"):
            log_message(f"❌ Ошибка: {companies['message']}")
            return

        # Защититься от None или ошибочных ответов при получении карточек — приводим к списку
        if not isinstance(cards, list):
            if isinstance(cards, dict) and cards.get("error"):
                log_message(f"❌ Ошибка при получении карточек: {cards.get('message')}")
            else:
                log_message("⚠️ Карточки не получены — используем пустой список карточек.")
            cards = []

        contacts = insta_filter(companies, cards, self.pipeline_ids)
        for company_id, name, category, type_professions, link in contacts:
            username_match = re.search(r"instagram\.com/([A-Za-z0-9_.]+)", link)
            if username_match:
                username = username_match.group(1)
                self.queue.put({
                    "company_id": company_id,
                    "company_name": name,
                    "category": category,
                    "type_professions": type_professions,
                    "username": username,
                    "link": link
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
                f"{item['category']} | "
                f"{item['type_professions']} | "
                f"Instagram: @{item['username']} ({item['link']})"
            )
            time.sleep(0.3)

