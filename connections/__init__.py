import config
import os

PACKAGE_NAME = 'API Connections'

from .shoper_connect import ShoperAPIClient
from .gsheets_connect import GSheetsClient
from .easystorage_data import EasyStorageData

print('API Connections loaded.')
print('-----------------------------------')

def init_shoper():
    return ShoperAPIClient(
        site_url=os.getenv(f'SHOPERSITE_{config.SITE}'),
        login=os.getenv(f'LOGIN_{config.SITE}'),
        password=os.getenv(f'PASSWORD_{config.SITE}')
    )

def init_gsheets():
    return GSheetsClient(
        credentials=os.path.join('credentials', 'gsheets_credentials.json'),
        sheet_id=os.getenv(f'SHEET_ID_{config.SHEET}'),
        sheet_name=config.SHEET_NAME
    )
