from dotenv import load_dotenv
import os

load_dotenv('keyes_data/password_keys_dates.env')

# Authorization data from .env file
INSTAGRAM_USERNAME = os.getenv('INSTAGRAM_USERNAME')
INSTAGRAM_PASSWORD = os.getenv('INSTAGRAM_PASSWORD')

# KeyCRM Dates
KEYCRM_API_KEY = os.getenv('KEYCRM_API_KEY')
API_BASE_URL = os.getenv('API_BASE_URL')
API_COMPANIES_ENDPOINT = os.getenv('API_COMPANIES_ENDPOINT')

# Files for test from .env files
LOG_FILE = os.getenv('LOG_FILE')
EXCEL_FILE = os.getenv('EXCEL_FILE')
