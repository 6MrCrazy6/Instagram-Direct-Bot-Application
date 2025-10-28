import os
import sys

# Добавляем путь к папке services (чтобы можно было импортировать)
sys.path.append(os.path.join(os.path.dirname(__file__), "services"))

from services.keycrm_service import ApiClient, insta_filter, start_date, end_date
from services.campaign_manager import CampaignManagerTest

print("🚀 Тест KeyCRM API и CampaignManager\n")

# Проверим, что .env подгрузился
print("KEYCRM_API_KEY =", os.getenv("KEYCRM_API_KEY"))
print("API_BASE_URL =", os.getenv("API_BASE_URL"))
print("-" * 50)

API_BASE_URL: str = os.getenv("API_BASE_URL") or ""
KEYCRM_API_KEY: str = os.getenv("KEYCRM_API_KEY") or ""

# 1️⃣ Проверяем подключение к KeyCRM напрямую
client = ApiClient(KEYCRM_API_KEY, API_BASE_URL)
pipeline_ids = [1, 3, 16, 20, 31, 2, 4, 15, 19, 32, 22, 24, 26, 30, 33, 46, 18]
cards = client.fetch_all_pipeline_cards(pipeline_ids, date=(start_date, end_date), include="contact.client")

if not cards:
    cards = []

companies = client.fetch_all_companies(date=(start_date, end_date), include="custom_fields")


# if data.get("error"):
#     print("❌ Ошибка подключения к KeyCRM:", data["message"])
# else:
#     print(f"✅ Успешно получено компаний: {len(data.get('data', []))}")


# 2️⃣ Фильтруем контакты с Instagram
contacts = insta_filter(companies, cards, pipeline_ids)
print(f"📸 Найдено {len(contacts)} компаний с Instagram-ссылками")

for company_id, name, category, type_professions, link in contacts:
    print(f"ID: {company_id}, Имя: {name}, Категория: {category}, Вид діяльності: {type_professions}, Instagram: {link}")

print("-" * 50)

# 3️⃣ Тест CampaignManagerTest
print("🧩 Запуск теста очереди CampaignManagerTest\n")
manager = CampaignManagerTest()
manager.fill_queue_from_keycrm()
manager.show_queue()

print("\n🏁 Тест завершён успешно.")


# 4️⃣ Обновляем кастомне поле в Компании, что мы сделали рассылку на Instagram
# for company_id, instagram_url in companies_with_insta:
#     _ = client.put_custom_field(company_id=company_id, uuid=SENT_CUSTOM_FIELDS, field_value=True)