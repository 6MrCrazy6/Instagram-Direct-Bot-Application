import re
import requests

from typing import Any, Dict, List, Optional, Tuple
from config import KEYCRM_API_KEY, API_BASE_URL

# UUID кастомных полей
SOCIAL_MEDIAS_CUSTOM_FIELDS = "CY_1039"
SENT_CUSTOM_FIELDS = "CY_1071"

TIMEOUT = 30

# Регулярное выражение для поиска ссылок на Instagram (захватывает username)
INSTAGRAM_REGEX = re.compile(
    r"(?:https?:\/\/)?(?:www\.)?instagram\.com\/([A-Za-z0-9_.]+)/?",
    re.IGNORECASE,
)


class ApiClient:
    """Простой клиент KeyCRM, используемый в этом скрипте.

    Класс предоставляет два метода, которые используются в скрипте:
    - fetch_all_companies: собирает компании с пагинацией
    - put_custom_field: обновляет кастомное поле у компании
    """

    def __init__(self) -> None:
        self.base_url: str = API_BASE_URL
        self.api_key: str = KEYCRM_API_KEY
        self.headers: Dict[str, str] = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def fetch_all_companies(
        self,
        limit: int = 50,
        include: str = "",
        filters: Optional[Dict[str, Any]] = None,
        max_pages: int = 100,
    ) -> Dict[str, Any]:
        """Получить все компании из KeyCRM, обрабатывая простую пагинацию.

        Параметры:
            limit: количество элементов на страницу (обычно максимум 50)
            include: через запятую связанные сущности для включения (например, "custom_fields")
            filters: необязательный словарь фильтров, где каждая пара ключ/значение становится filter[key]=value
            max_pages: защитный лимит страниц, чтобы избежать бесконечного цикла

        Возвращает:
            словарь с ключами: error (bool), data (список компаний), message (str)
        """

        endpoint = "/companies"
        all_companies: List[Dict[str, Any]] = []
        page = 1

        while True:
            params: Dict[str, Any] = {"limit": limit, "page": page}

            if include:
                params["include"] = include

            if filters:
                for key, value in filters.items():
                    params[f"filter[{key}]"] = value

            try:
                response = requests.get(
                    f"{self.base_url}{endpoint}",
                    headers=self.headers,
                    params=params,
                    timeout=TIMEOUT,
                )
                response.raise_for_status()
                data = response.json()
            except requests.exceptions.RequestException as e:
                return {
                    "error": True,
                    "message": f"Error fetching companies (page {page}): {e}",
                    "data": all_companies,
                }

            companies = data.get("data", [])
            if not companies:
                break

            all_companies.extend(companies)

            # Если получено меньше чем limit — считаем, что это последняя страница
            if len(companies) < limit:
                break

            page += 1
            if page > max_pages:
                break

        return {
            "error": False,
            "data": all_companies,
            "message": f"Fetched {len(all_companies)} companies",
        }

    def put_custom_field(self, company_id: int, uuid: str, field_value: Any) -> Dict[str, Any]:
        """
        Обновить (или создать) значение кастомного поля для конкретной компании.

        Возвращает словарь с ключами error/message/data, аналогично fetch_all_companies.
        """

        url = f"{self.base_url}/companies/{company_id}"

        payload = {
            "custom_fields": [
                {
                    "uuid": uuid,
                    "value": field_value,
                }
            ]
        }

        try:
            response = requests.put(url, headers=self.headers, json=payload, timeout=TIMEOUT)
            response.raise_for_status()
            return {
                "error": False,
                "message": f"Custom field {uuid} updated for company {company_id}",
                "data": response.json(),
            }

        except requests.exceptions.HTTPError as http_err:
            return {"error": True, "message": f"HTTP error: {http_err}", "data": {}}

        except requests.exceptions.RequestException as e:
            return {"error": True, "message": f"Request failed: {e}", "data": {}}


def insta_filter(all_companies: Dict[str, Any]) -> List[Tuple[int, str]]:
    """Возвращает список кортежей (id_компании, instagram_url) для компаний,
    у которых в кастомных полях есть ссылка на Instagram.

    Примечание: логика полностью сохранена из оригинального скрипта (изменений поведения нет).
    """

    results: List[Tuple[int, str]] = []

    for company in all_companies.get("data", []):
        type_professions = None
        custom_fields = company.get("custom_fields", [])
        for field in custom_fields:
            # Проверка, рассылали мы уже или нет
            if field.get("uuid") == SENT_CUSTOM_FIELDS and bool(field.get("value")):
                continue
            else:
                if field.get("uuid") == SOCIAL_MEDIAS_CUSTOM_FIELDS:
                    social_link = field.get("value")
                    if not social_link:
                        continue

                    if field.get("name") == "Основний вид діяльності":
                        type_professions = field.get("value", None)

                    # Может быть строка или список — обрабатываем оба варианта
                    if isinstance(social_link, list):
                        links = social_link
                    else:
                        links = [social_link]

                    for link in links:
                        if isinstance(link, str) and INSTAGRAM_REGEX.search(link):
                            results.append((company.get("id"), company.get("name"),  type_professions, link))
                            break  # нашли одну инстаграм-ссылку — этого достаточно

    return results