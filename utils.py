import time
import random
import os
from logger import log_message
from selenium.webdriver.common.action_chains import ActionChains

# === Основные функции задержек ===
def random_delay(min_sec=15, max_sec=45):
    """Большая рандомная пауза (между сообщениями)"""
    delay = random.uniform(min_sec, max_sec)
    log_message(f"Затримка {delay:.1f} секунд...")
    time.sleep(delay)
    return delay


def small_random_delay(min_sec=0.3, max_sec=1.5):
    """Маленькая случайная пауза между микродействиями"""
    delay = random.uniform(min_sec, max_sec)
    time.sleep(delay)
    return delay


# === Имитация поведения человека ===
def random_scroll(driver, max_scrolls=2):
    """Случайные прокрутки страницы (имитация просмотра контента)"""
    for _ in range(random.randint(1, max_scrolls)):
        try:
            amount = random.randint(-300, 300)
            driver.execute_script("window.scrollBy(0, arguments[0]);", amount)
            time.sleep(random.uniform(0.4, 1.2))
        except Exception:
            pass


def human_type(element, text, runner=None):
    """Реалистичный ввод текста по символам, с проверкой паузы."""
    import time, random
    from logger import log_message

    for char in text:
        # Проверяем, поставлен ли бот на паузу
        if runner and getattr(runner, "paused", False):
            log_message("⏸️ Бот поставлен на паузу во время ввода текста.")
            # Ждём пока пользователь не нажмёт "Продолжить"
            while runner.paused:
                time.sleep(0.5)
            log_message("▶️ Возобновление ввода после паузы.")

        element.send_keys(char)
        time.sleep(random.uniform(0.08, 0.25))


def safe_click(driver, element):
    """Безопасный клик (с прокруткой и fallback через JS)"""
    try:
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(random.uniform(0.3, 0.6))
        element.click()
    except Exception:
        try:
            ActionChains(driver).move_to_element(element).pause(random.uniform(0.2, 0.4)).click().perform()
        except Exception:
            driver.execute_script("arguments[0].click();", element)
    time.sleep(random.uniform(0.2, 0.6))

def update_env_variable(variable_name, new_value):
    """Функция для обновления переменной в файле keyes_data/password_keys_dates.env"""
    try:
        # Правильный путь к .env файлу
        env_file = os.path.join(
            os.path.dirname(__file__),
            "keyes_data",
            "password_keys_dates.env"
        )

        # Проверяем, существует ли файл
        if not os.path.exists(env_file):
            raise FileNotFoundError(f"Файл не найден: {env_file}")

        # Читаем существующие строки
        with open(env_file, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # Перезаписываем с обновлённым значением
        with open(env_file, 'w', encoding='utf-8') as file:
            found = False
            for line in lines:
                if line.startswith(f"{variable_name}="):
                    file.write(f"{variable_name}={new_value}\n")
                    found = True
                else:
                    file.write(line)

            # Если переменной не было — добавляем в конец
            if not found:
                file.write(f"{variable_name}={new_value}\n")

        print(f"✅ {variable_name} успешно обновлена в {env_file}")

    except Exception as e:
        print(f"⚠️ Ошибка при обновлении {variable_name}: {e}")