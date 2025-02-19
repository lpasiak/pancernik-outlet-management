import os

# SITE can be either TEST (development) or MAIN (deployment)
SITE = 'TEST' 

# LIMIT for API requests
SHOPER_LIMIT = 50

# Google Sheet name
SHEET = 'TEST'
SHEET_NAME = 'Outlety'
SHEET_LACKING_PRODUCTS_NAME = 'Brak produktów'
SHEET_ARCHIVED_NAME = 'Archiwum'

# Time after which the offer should be discounted
DISCOUNT_DAYS = 14

EASYSTORAGE_PATH = os.path.join('data', 'easystorage.xlsx')
