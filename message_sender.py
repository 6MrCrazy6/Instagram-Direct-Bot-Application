import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from logger import log_message
from utils import human_type, safe_click, small_random_delay


def send_message(driver, username, message, runner=None):
    """Відправка повідомлення користувачу (з реалістичною поведінкою людини + пауза/відновлення)"""
    log_message(f"Спроба надіслати повідомлення до @{username}")
    wait = WebDriverWait(driver, 45)

    # === Расширенная check_pause, как в login_manager ===
    def check_pause(stage=None):
        """Если бот поставлен на паузу — останавливаем выполнение и ждём возобновления"""
        if runner and runner.paused:
            log_message(f"⏸️ Бот поставлен на паузу{f' (етап: {stage})' if stage else ''}. Очікування 'Продовжити'...")
            while runner.paused:
                time.sleep(0.5)
            log_message("▶️ Продовжуємо роботу після паузи...")

            # Если не на странице Direct — вернуть обратно
            try:
                if "instagram.com/direct" not in driver.current_url:
                    log_message("↩️ Не на сторінці Direct. Повертаємось у Direct...")
                    driver.get("https://www.instagram.com/direct/inbox/")
                    time.sleep(5)
                    log_message("📬 Direct відкрито, продовжуємо роботу.")
                else:
                    log_message("✅ Ми вже на сторінці Direct.")
            except Exception as e:
                log_message(f"⚠️ Помилка при перевірці сторінки після паузи: {e}")

    try:
        driver.get('https://www.instagram.com/direct/inbox/')
        time.sleep(6 + small_random_delay(0.5, 2.5))
        check_pause("відкриття Direct")

        # === 1. Кнопка "New message" ===
        try:
            new_btn = wait.until(EC.element_to_be_clickable((
                By.XPATH,
                "//*[contains(@aria-label, 'New message') or "
                "contains(@aria-label, 'Send message') or "
                "contains(@aria-label, 'Написати повідомлення') or "
                "contains(@aria-label, 'Отправить сообщение') or "
                "contains(text(), 'Отправить сообщение') or "
                "contains(text(), 'Написати повідомлення')]"
            )))
            safe_click(driver, new_btn)
            log_message("✓ Кнопка 'New message' знайдена і натиснута.")
        except Exception:
            log_message("✗ Не знайдено кнопку 'New message'")
            return False

        check_pause("після натискання 'New message'")
        time.sleep(7 + small_random_delay(1, 3))

        # === 2. Пошук користувача ===
        attempt_reload = 0
        found_user = False

        while attempt_reload < 3 and not found_user:
            try:
                search_input = wait.until(EC.presence_of_element_located((By.NAME, 'queryBox')))
                search_input.click()
                check_pause("початок пошуку")

                # Очищення поля посимвольно
                current_value = search_input.get_attribute("value")
                if current_value:
                    for _ in range(len(current_value)):
                        search_input.send_keys(Keys.BACKSPACE)
                        time.sleep(0.1)

                time.sleep(0.5 + small_random_delay(0.3, 0.8))
                check_pause("введення імені")

                human_type(search_input, username, runner)
                log_message(f"→ Введено ім'я користувача: {username}")

                # Чекаємо результати пошуку
                for i in range(12):
                    check_pause("очікування результатів пошуку")
                    try:
                        results = driver.find_elements(By.XPATH, "//div[@role='button']//span")
                        if results:
                            try:
                                user_item = driver.find_element(
                                    By.XPATH, f"//div[@role='button']//span[contains(text(), '{username}')]"
                                )
                                safe_click(driver, user_item)
                                log_message("✓ Користувача вибрано.")
                                found_user = True
                                break
                            except Exception:
                                log_message("⏳ Користувача ще не знайдено, чекаємо...")
                        else:
                            log_message("🕐 Результати ще не завантажились...")
                    except Exception:
                        log_message("⚠️ Очікування списку користувачів...")

                    # Якщо довго — повторний набір
                    if i in [4, 8]:
                        check_pause("повторне введення імені")
                        search_input.click()
                        current_value = search_input.get_attribute("value")
                        if current_value:
                            for _ in range(len(current_value)):
                                search_input.send_keys(Keys.BACKSPACE)
                                time.sleep(0.1)
                        time.sleep(0.5 + small_random_delay(0.3, 0.8))
                        human_type(search_input, username, runner)
                        log_message(f"🔁 Повторне введення імені: {username}")

                    time.sleep(2)

                if found_user:
                    break

                # Якщо не знайдено — оновити сторінку
                attempt_reload += 1
                if not found_user and attempt_reload < 3:
                    log_message(f"🔄 Перезавантаження Direct (спроба {attempt_reload}/3)...")
                    driver.refresh()
                    time.sleep(7 + small_random_delay(1, 2))
                    continue

            except Exception:
                attempt_reload += 1
                log_message(f"⚠️ Помилка при пошуку користувача, спроба {attempt_reload}")
                driver.refresh()
                time.sleep(7)

        # === 3. Якщо не знайдено — fallback ===
        if not found_user:
            log_message("⚠️ Користувача не знайдено після кількох спроб. Пробуємо відкрити чат вручну...")
            try:
                chat_btn = driver.find_element(
                    By.XPATH, "//div[text()='Чат' or text()='Chat' or text()='Next' or text()='Далі']"
                )
                safe_click(driver, chat_btn)
                log_message("⚠️ Користувача не знайдено, але чат відкрито вручну.")
            except Exception:
                log_message("✗ Не знайдено користувача і кнопку 'Чат'.")
                return False

        check_pause("відкриття чату")
        time.sleep(3 + small_random_delay(0.5, 1.5))

        # === 4. Кнопка “Next / Chat” ===
        try:
            chat_btn = wait.until(EC.element_to_be_clickable((
                By.XPATH,
                "//div[text()='Chat' or text()='Next' or text()='Далі' or text()='Чат']"
            )))
            safe_click(driver, chat_btn)
            log_message("✓ Кнопка 'Chat/Next' натиснута.")
        except Exception:
            log_message("⚠️ Кнопка 'Chat/Next' не знайдена — можливо вже відкрито чат.")

        check_pause("перед відправкою повідомлення")
        time.sleep(5 + small_random_delay(1, 2))

        # === 5. Поле для повідомлення ===
        try:
            msg_field = wait.until(EC.presence_of_element_located((
                By.XPATH,
                "//textarea[contains(@placeholder,'Message') or "
                "contains(@placeholder,'повідомлення') or "
                "contains(@placeholder,'сообщение')] | "
                "//*[@contenteditable='true' and (@aria-label or @role='textbox')]"
            )))
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", msg_field)
            msg_field.click()
            check_pause("введення повідомлення")
            small_random_delay(0.5, 1.5)

            human_type(msg_field, message, runner)
            msg_field.send_keys(Keys.RETURN)
            time.sleep(3)
            log_message(f"✓ Повідомлення надіслано до @{username}")
            return True

        except Exception:
            log_message("✗ Не знайдено поле для введення повідомлення (textarea або contenteditable).")
            return False

    except TimeoutException:
        log_message(f"✗ Timeout при відправці до @{username}")
        return False
    except Exception as e:
        log_message(f"✗ Помилка при відправці до @{username}: {e}")
        return False