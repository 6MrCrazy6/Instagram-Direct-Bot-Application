import time
import random
import undetected_chromedriver as uc
from logger import log_message
from utils import random_delay, random_scroll, get_message_by_category_or_profession
from login_manager import login
from message_sender import send_message
from services.campaign_manager import CampaignManagerTest


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


def run_bot(runner=None):
    """Основная логика Instagram Direct Bot — працює з будь-якою версією Chrome."""
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
    log_message("✓ Запущено undetected ChromeDriver (підтримує будь-яку версію Chrome).")

    try:
        # Авторизация в Instagram
        if not login(driver, runner):
            log_message("✗ Не вдалося увійти. Завершення роботи.")
            return

        random_delay(5, 10)
        random_scroll(driver)

        # Получаем контакты из KeyCRM
        log_message("🔄 Отримання даних із KeyCRM...")
        campaign_manager = CampaignManagerTest()
        campaign_manager.fill_queue_from_keycrm()
        queue = campaign_manager.queue

        if queue.empty():
            log_message("⚠️ Черга порожня — немає контактів для обробки.")
            return

        log_message(f"✅ Завантажено {queue.qsize()} контактів для обробки.")

        success, fail, sent_total = 0, 0, 0

        # Основной цикл рассылки
        while not queue.empty():
            check_stop(runner)
            contact = queue.get()

            username = contact["username"]
            category = contact["category"]
            type_professions = contact["type_professions"]

            # Получаем сообщение для отправки
            message = get_message_by_category_or_profession(category, type_professions)

            if not message:
                log_message(f"⚠️ Пропущено @{username} — немає відповідного повідомлення.")
                continue

            log_message(f"\n--- Обробка користувача: @{username} ({category}) ---")
            ensure_online(driver)

            try:
                # Отправляем сообщение
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

            # Имитируем прокрутку (человеческое поведение)
            if random.random() < 0.3:
                random_scroll(driver)
                log_message("🌀 Імітація прокрутки (людська поведінка).")

            # Задержка перед следующими сообщениями
            delay = random.uniform(25, 75)
            log_message(f"⌛ Затримка перед наступним повідомленням: {delay:.1f} сек.")
            for _ in range(int(delay * 5)):
                time.sleep(0.2)

        # Печать итогов
        log_message(f"\n✅ Розсилка завершена.\nУспішно: {success}, Помилки: {fail}")

    except InterruptedError as stop_signal:
        log_message(f"{stop_signal}")
        log_message("🛑 Виконання бота зупинено користувачем.")
    except Exception as e:
        log_message(f"💀 Критична помилка: {str(e)}")

    finally:
        log_message("🧩 Браузер залишено відкритим (зупинка без закриття).")