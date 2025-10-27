import os
import sys

# Добавляем путь к папке services (чтобы можно было импортировать)
sys.path.append(os.path.join(os.path.dirname(__file__), "services"))

from services.keycrm_service import ApiClient, insta_filter
from services.campaign_manager import CampaignManagerTest

print("🚀 Тест KeyCRM API и CampaignManager\n")

# Проверим, что .env подгрузился
print("KEYCRM_API_KEY =", os.getenv("KEYCRM_API_KEY"))
print("API_BASE_URL =", os.getenv("API_BASE_URL"))
print("-" * 50)

# 1️⃣ Проверяем подключение к KeyCRM напрямую
client = ApiClient()
data = client.fetch_all_companies(include="custom_fields")

if data.get("error"):
    print("❌ Ошибка подключения к KeyCRM:", data["message"])
else:
    print(f"✅ Успешно получено компаний: {len(data.get('data', []))}")

# 2️⃣ Фильтруем контакты с Instagram
contacts = insta_filter(data)
print(f"📸 Найдено {len(contacts)} компаний с Instagram-ссылками")

for company_id, company_name, type_professions, insta in contacts[:5]:
    print(f" → ID: {company_id} | {company_name} | {type_professions} | {insta} ")

print("-" * 50)

# 3️⃣ Тест CampaignManagerTest
print("🧩 Запуск теста очереди CampaignManagerTest\n")
manager = CampaignManagerTest()
manager.fill_queue_from_keycrm()
manager.show_queue()

print("\n🏁 Тест завершён успешно.")
