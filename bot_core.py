import os
import time
import random
import pandas as pd
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from logger import log_message
from utils import random_delay, small_random_delay, random_scroll
from login_manager import login
from message_sender import send_message
from config import EXCEL_FILE


def check_stop(runner):
    """Перевіряє, чи бот не поставлено на паузу / зупинку."""
    if not runner:
        return
    if not runner.running:
        raise InterruptedError("⛔ Бот зупинено користувачем.")
    if runner.paused:
        log_message("⏸️ Бот поставлений на паузу. Очікування 'Продовжити'...")
        while runner.paused and runner.running:
            time.sleep(0.3)
        log_message("▶️ Бот відновив роботу.")


def ensure_online(driver):
    """Перевіряє, чи Instagram не показує 'Немає підключення' або 'Something went wrong'."""
    try:
        page = driver.page_source
        if (
            "Нет подключения к Интернету" in page
            or "No Internet" in page
            or "Sorry, something went wrong" in page
            or ("edge-chat.instagram.com" in page and "error" in page)
        ):
            log_message("⚠️ Instagram втратив підключення або WebSocket. Оновлюємо сторінку...")
            driver.refresh()
            time.sleep(8)
            return False
    except Exception as e:
        log_message(f"⚠️ Помилка при перевірці підключення: {e}")
    return True


def resume_context(driver):
    """Перевіряє, що бот у правильному контексті після паузи."""
    try:
        current_url = driver.current_url

        # Авторизація
        if "login" in current_url:
            log_message("⚠️ На сторінці входу. Очікуємо ручного входу...")
            while "login" in driver.current_url:
                time.sleep(3)
            log_message("✅ Авторизацію виконано вручну.")

        # Challenge
        elif "challenge" in current_url or "checkpoint" in current_url:
            log_message("📩 Instagram запитує код підтвердження. Очікуємо ручного підтвердження...")
            while "challenge" in driver.current_url or "checkpoint" in driver.current_url:
                time.sleep(3)
            log_message("✅ Підтвердження виконано вручну.")

        # Якщо не Direct
        elif "direct" not in current_url:
            log_message("↩️ Не на сторінці Direct. Повертаємось...")
            driver.get("https://www.instagram.com/direct/inbox/")
            time.sleep(5)

        # Перевіряємо наявність кнопки "New message"
        for _ in range(10):
            try:
                driver.find_element(By.XPATH, "//*[contains(@aria-label, 'New message')]")
                log_message("📬 Сторінка Direct активна, можна продовжувати.")
                return True
            except Exception:
                time.sleep(2)

        log_message("⚠️ Кнопку 'New message' не знайдено, можливо сторінка ще вантажиться.")
        return True

    except Exception as e:
        log_message(f"❌ Помилка при відновленні контексту: {e}")
        return False


def run_bot(runner=None):
    """Основна логіка Instagram Direct Bot (з людською поведінкою + антидетект + реактивна пауза)."""
    log_message("=" * 60)
    log_message("🚀 Запуск Instagram Auto-Messenger")
    log_message("=" * 60)

    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-infobars")

    driver = uc.Chrome(options=options)
    runner.driver = driver
    if runner:
        runner.driver = driver
    log_message("✓ Запущено undetected ChromeDriver (антидетект).")

    try:
        if not login(driver, runner):
            log_message("✗ Не вдалося увійти. Завершення роботи.")
            return

        random_delay(5, 10)
        random_scroll(driver)

        df = pd.read_excel(EXCEL_FILE)
        log_message(f"📄 Знайдено {len(df)} контактів у файлі {EXCEL_FILE}")

        success, fail, sent_total = 0, 0, 0

        for index, row in df.iterrows():
            check_stop(runner)

            username = str(row['username']).strip().replace('@', '')
            link = str(row['link']).strip()
            message = MESSAGE_TEMPLATE.format(link=link)

            log_message(f"\n--- [{index + 1}/{len(df)}] Обробка користувача: @{username} ---")
            ensure_online(driver)

            try:
                if send_message(driver, username, message, runner):
                    success += 1
                    sent_total += 1
                else:
                    fail += 1
            except InterruptedError:
                log_message("⏸️ Бот поставлено на паузу. Очікування 'Продовжити'...")
                continue
            except Exception as e:
                log_message(f"⚠️ Помилка при відправці до @{username}: {e}")
                fail += 1

            small_random_delay(1.0, 3.5)
            check_stop(runner)

            if random.random() < 0.3:
                random_scroll(driver)
                log_message("🌀 Імітація прокрутки (людська поведінка).")

            if random.random() < 0.15:
                t = random.uniform(5, 10)
                log_message(f"🤔 Користувач робить паузу {t:.1f} сек.")
                for _ in range(int(t * 5)):
                    check_stop(runner)
                    time.sleep(0.2)

            if index < len(df) - 1:
                delay = random.uniform(25, 75)
                log_message(f"⌛ Затримка перед наступним повідомленням: {delay:.1f} сек.")
                for _ in range(int(delay * 5)):
                    check_stop(runner)
                    time.sleep(0.2)

            if sent_total % 10 == 0 and sent_total != 0:
                pause = random.uniform(180, 300)
                log_message(f"😴 Відпочинок після 10 повідомлень ({pause:.0f} сек.)")
                for _ in range(int(pause * 5)):
                    check_stop(runner)
                    time.sleep(0.2)

            ensure_online(driver)

        log_message(f"\n✅ Розсилка завершена.\nУспішно: {success}, Помилки: {fail}")

    except InterruptedError as stop_signal:
        log_message(f"{stop_signal}")
        log_message("🛑 Виконання бота зупинено користувачем.")
    except Exception as e:
        log_message(f"💀 Критична помилка: {str(e)}")

    finally:
        log_message("🧩 Браузер залишено відкритим (зупинка без закриття).")