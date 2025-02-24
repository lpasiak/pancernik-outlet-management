import os

# SITE can be either TEST (development) or MAIN (deployment)
SITE = 'MAIN' 

# LIMIT for API requests
SHOPER_LIMIT = 50

# Google Sheet name
SHEET = 'MAIN'
SHEET_NAME = 'Outlety'
SHEET_LACKING_PRODUCTS_NAME = 'Brak produktów'
SHEET_ARCHIVED_NAME = 'Archiwum'

# Time after which the offer should be discounted
DISCOUNT_DAYS = 14

try:
    EASYSTORAGE_PATH = os.path.join('data', 'easystorage.xlsx')
except FileNotFoundError:
    print('No file easystorage.xlsx in data directory')
