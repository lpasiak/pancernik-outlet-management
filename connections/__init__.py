PACKAGE_NAME = 'API Connections'
VERSION = '1.0.0'

from .shoper_connect import ShoperAPIClient
from .gsheets_connect import GSheetsClient
from .easystorage_data import EasyStorageData

print('API Connections loaded.')
print('-----------------------------------')