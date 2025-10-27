import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from logger import log_message
from config import INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD


def human_type(element, text, runner=None):
    """Реалистичный ввод по символам с проверкой паузы."""
    import random
    for char in text:
        # Проверяем — поставлен ли бот на паузу
        if runner and getattr(runner, "paused", False):
            log_message("⏸️ Бот поставлен на паузу во время ввода тексту.")
            while runner.paused:
                time.sleep(0.5)
            log_message("▶️ Продовжуємо набір тексту після паузи.")

        element.send_keys(char)
        time.sleep(random.uniform(0.08, 0.25))


def login(driver, runner=None):
    """Автоматичний вхід в Instagram з підтримкою паузи та правильним відновленням."""
    log_message("🔐 Початок входу в Instagram...")
    driver.get("https://www.instagram.com/accounts/login/")
    wait = WebDriverWait(driver, 30)
    login_done = False

    def clear_field(element):
        """Посимвольне очищення поля"""
        try:
            element.click()
            current_value = element.get_attribute("value")
            if current_value:
                for _ in range(len(current_value)):
                    element.send_keys("\b")
                    time.sleep(0.05)
        except Exception:
            pass

    def check_pause():
        """Пауза під час авторизації"""
        nonlocal login_done
        if runner and runner.paused:
            log_message("⏸️ Бот поставлений на паузу під час авторизації...")
            while runner.paused:
                time.sleep(1)
            log_message("▶️ Продовжуємо авторизацію...")

            # Якщо ще на сторінці входу — перевводимо поля
            if "login" in driver.current_url and not login_done:
                try:
                    username_input = driver.find_element(By.NAME, "username")
                    password_input = driver.find_element(By.NAME, "password")

                    clear_field(username_input)
                    clear_field(password_input)
                    log_message("🔁 Поля очищено після паузи. Повторюємо введення...")

                    human_type(username_input, INSTAGRAM_USERNAME, runner)
                    time.sleep(0.3)
                    human_type(password_input, INSTAGRAM_PASSWORD, runner)
                    password_input.submit()
                    log_message("✅ Дані повторно введено після паузи.")
                    login_done = True
                except Exception as e:
                    log_message(f"⚠️ Не вдалося повторно заповнити поля після паузи: {e}")
            else:
                log_message("✅ Не на сторінці логіну — авторизація вже виконана.")

    try:
        username_input = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        password_input = wait.until(EC.presence_of_element_located((By.NAME, "password")))

        clear_field(username_input)
        clear_field(password_input)

        human_type(username_input, INSTAGRAM_USERNAME, runner)
        time.sleep(2)
        human_type(password_input, INSTAGRAM_PASSWORD, runner)
        time.sleep(2)
        password_input.submit()
        login_done = True
        log_message("✅ Дані для входу введено, очікуємо завантаження...")

        for _ in range(200):
            check_pause()
            url = driver.current_url

            if "challenge" in url or "checkpoint" in url:
                log_message("📩 Instagram запитує код підтвердження. Очікуємо ручного введення коду...")
                while "challenge" in driver.current_url or "checkpoint" in driver.current_url:
                    check_pause()
                    time.sleep(3)
                log_message("✅ Код підтвердження введено вручну. Продовжуємо.")
                break

            if "instagram.com" in url and "login" not in url:
                log_message("🏠 Вхід виконано успішно.")
                break

            time.sleep(3)

        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "svg[aria-label='Home']")))
            log_message("📱 Головна сторінка Instagram активна.")
            return True
        except TimeoutException:
            log_message("⚠️ Не вдалося знайти головну сторінку — можливо, ще вантажиться.")
            return True

    except Exception as e:
        log_message(f"✗ Помилка входу: {e}")
        return False
