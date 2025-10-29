# main.py
import threading
from services.campaign_manager import CampaignManagerTest
from apps_design_interface.gui_main import DirectBotApp
from logger import log_message

def run_campaign_manager():
    """Функция для получения данных из KeyCRM и добавления контактов в очередь"""
    campaign_manager = CampaignManagerTest()
    campaign_manager.fill_queue_from_keycrm()
    log_message("Контакты из KeyCRM были загружены.")

if __name__ == "__main__":
    campaign_thread = threading.Thread(target=run_campaign_manager)
    campaign_thread.start()

    campaign_thread.join()

    app = DirectBotApp()
    app.mainloop()

    campaign_thread.join()