PACKAGE_NAME = 'API Connections'
VERSION = '1.0.0'

from .shoper_connect import ShoperAPIClient
from .gsheets_connect import GSheetsClient

print('API Connections loaded.')
print('-----------------------------------')