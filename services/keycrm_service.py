import os
import re
from typing import Any, Dict, List, Optional, Tuple
from dotenv import load_dotenv
import requests
import pytz
from datetime import datetime, timezone

load_dotenv()

# === Конфигурация KeyCRM API ===
KEYCRM_API_KEY = os.getenv("KEYCRM_API_KEY", "your_api_key_here")
API_COMPANIES_ENDPOINT = "/companies"
API_CARDS_ENDPOINT = "/pipelines/cards"

# UUID кастомных полей
SOCIAL_MEDIAS_CUSTOM_FIELDS = "CY_1039"
SENT_CUSTOM_FIELDS = "CY_1071"

TIMEOUT = 30

# Регулярное выражение для поиска ссылок на Instagram (захватывает username)
INSTAGRAM_REGEX = re.compile(
    r"(?:https?:\/\/)?(?:www\.)?instagram\.com\/([A-Za-z0-9_.]+)/?", re.IGNORECASE
)

SERVER_TZ = timezone.utc
KYIV_TZ = pytz.timezone("Europe/Kyiv")
today = datetime.now(KYIV_TZ).strftime("%Y-%m-%d")
end_date = datetime.strptime(today, "%Y-%m-%d").strftime("%Y-%m-%d")
start_date = "2025-10-27"


class ApiClient:
    """Простой клиент KeyCRM, используемый в этом скрипте.

    Класс предоставляет два метода, которые используются в скрипте:
    - fetch_all_companies: собирает компании с пагинацией
    - put_custom_field: обновляет кастомное поле у компании
    """

    def __init__(self, KEYCRM_API_KEY: str, API_BASE_URL: str) -> None:
        self.base_url: str = API_BASE_URL
        self.api_key: str = KEYCRM_API_KEY
        self.headers: Dict[str, str] = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def fetch_all_companies(
        self,
        limit: int = 50,
        date: Optional[Tuple[str, str]] = None,
        include: str = "",
        filters: Optional[Dict[str, Any]] = None,
        max_pages: int = 100,
    ) -> Dict[str, Any]:
        """Получить все компании из KeyCRM, обрабатывая пагинацию."""

        endpoint = "/companies"
        all_companies: List[Dict[str, Any]] = []
        page = 1

        if date:
            start_date, end_date = date[0], date[1]
            local_filters: Dict[str, Any] = dict(filters) if filters else {}
            local_filters["created_between"] = f"{start_date} 00:00:00, {end_date} 23:59:59"
            filters = local_filters

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
        """Обновить (или создать) значение кастомного поля для конкретной компании."""

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

    def fetch_cards(
        self,
        limit: int = 50,
        page: int = 1,
        include: str = "",
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Fetch cards for given pipeline IDs."""

        url: str = f"{self.base_url}{API_CARDS_ENDPOINT}"
        params: Dict[str, Any] = {
            "limit": limit,
            "page": page
        }
        if include:
            params["include"] = include
        if filters:
            for key, value in filters.items():
                params[f"filter[{key}]"] = value

        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=TIMEOUT)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "error": True,
                "message": f"Error fetching calls: {str(e)}",
                "data": []
            }

    def fetch_all_pipeline_cards(
        self,
        pipeline_ids: List[int],
        date: Optional[Tuple[str, str]],
        limit: int = 50,
        include: str = ""
    ) -> Optional[List[Dict[str, Any]]]:
        """Получить все карточки для всех pipeline_id с возможностью фильтрации по дате создания."""

        all_cards: List[Dict[str, Any]] = []

        for pipeline_id in pipeline_ids:
            page = 1
            while True:
                filters: Dict[str, Any] = {"pipeline_id": pipeline_id}
                if date:
                    start_date, end_date = date[0], date[1]
                    filters["created_between"] = f"{start_date} 00:00:00, {end_date} 23:59:59"

                response = self.fetch_cards(
                    limit=limit,
                    page=page,
                    include=include,
                    filters=filters
                )

                if response.get("error"):
                    print(f"Error on page {page}: {response.get('message')}")
                    break

                data = response.get("data", [])

                if not data:
                    break

                all_cards.extend(data)

                if len(data) < limit:
                    break

                page += 1
        return all_cards


def insta_filter(
    all_companies: Dict[str, Any],
    cards: List[Dict[str, Any]],
    pipeline_ids: List[int]
) -> List[Tuple[int, str, Optional[str], List[str], str]]:
    """Возвращает список кортежей (id_компании, name, category, type_professions, instagram_url) для компаний,
    у которых в кастомных полях есть ссылка на Instagram.
    """

    # Формируем маппинг company_id -> pipeline_id и список разрешенных company_ids
    company_id_to_pipeline_id = {}
    allowed_company_ids = []

    for card in cards:
        if card['is_finished']:
            continue
        if card['contact'] and card['contact']['client']:
            company_id = card['contact']['client']['company_id']
            if company_id:
                company_id_to_pipeline_id[company_id] = card['pipeline_id']
                allowed_company_ids.append(company_id)

    results: List[Tuple[int, str, Optional[str], List[str], str]] = []

    for company in all_companies.get("data", []):
        company_id = company.get("id")

        if company_id not in allowed_company_ids:
            continue

        custom_fields = company.get("custom_fields", []) or []
        manager_id = company.get("manager_id", None)

        if manager_id:
            continue

        already_sent = any(f.get("uuid") == SENT_CUSTOM_FIELDS and bool(f.get("value")) for f in custom_fields)
        if already_sent:
            continue

        # Получаем основной вид деятельности
        type_professions: List[str] = [""]
        for f in custom_fields:
            if f.get("uuid") == "CY_1015":
                value = f.get("value")
                if isinstance(value, list) and value:
                    type_professions = [str(value[0])]
                elif value:
                    type_professions = [str(value)]
                break

        # Ищем ссылки на соцсети
        for f in custom_fields:
            if f.get("uuid") != SOCIAL_MEDIAS_CUSTOM_FIELDS:
                continue

            social_link = f.get("value")
            if not social_link:
                continue

            links = social_link if isinstance(social_link, list) else [social_link]

            for link in links:
                if isinstance(link, str) and INSTAGRAM_REGEX.search(link):
                    pipeline_id = company_id_to_pipeline_id.get(company_id)
                    category = define_category(pipeline_id) if pipeline_id else None
                    results.append((company_id, company.get("name"), category, type_professions, link))
                    break

            break

    return results


def define_category(pipeline_id: int) -> Optional[str]:
    """Returns category name based on pipeline ID."""
    categories = {
        1: "Електрики", 2: "Електрики", 22: "Електрики",
        3: "Дизайнери", 4: "Дизайнери", 24: "Дизайнери",
        15: "Будівельники", 16: "Будівельники", 26: "Будівельники",
        19: "Ріелтори", 20: "Ріелтори", 30: "Ріелтори",
        31: "Архітектори", 32: "Архітектори", 33: "Архітектори"
    }
    return categories.get(pipeline_id)
