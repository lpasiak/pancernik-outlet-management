import config
import os

PACKAGE_NAME = 'API Connections'
VERSION = '1.0.0'

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

def init_gsheets_lacking_products():
    return GSheetsClient(
        credentials=os.path.join('credentials', 'gsheets_credentials.json'),
        sheet_id=os.getenv(f'SHEET_ID_{config.SHEET}'),
        sheet_name=config.SHEET_LACKING_PRODUCTS_NAME
    )

def init_gsheets_archived():
    return GSheetsClient(
        credentials=os.path.join('credentials', 'gsheets_credentials.json'),
        sheet_id=os.getenv(f'SHEET_ID_{config.SHEET}'),
        sheet_name=config.SHEET_ARCHIVED_NAME
    )