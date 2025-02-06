import operations
from gsheets_connection import GSheetsClient
from shoper_connection import ShoperAPIClient
from dotenv import load_dotenv
import os
import config

dotenv_path = os.path.join('credentials', 'env')
load_dotenv(dotenv_path)

if __name__ == "__main__":

    shoper_client = ShoperAPIClient(
        site_url=os.getenv(f'SHOPERSITE_{config.SITE}'),
        login=os.getenv(f'LOGIN_{config.SITE}'),
        password=os.getenv(f'PASSWORD_{config.SITE}')
    )

    gsheets_client = GSheetsClient(
        credentials=os.path.join('credentials', 'gsheets_credentials.json'),
        sheet_id=os.getenv(f'SHEET_ID_{config.SHEET}'),
        sheet_name=config.SHEET_NAME
    )

    shoper_client.connect()
    gsheets_client.connect()


    action = str(input('''
Co chcesz zrobić?
1. Wystawić produkty outletowe
2. Dopisać atrybuty głównym produktom
Akcja: '''))
    
    if action == '1':
        operations.create_shoper_offers(shoper_client, gsheets_client)
    elif action == '2':
        operations.set_main_product_attributes(shoper_client, gsheets_client)
    else:
        print('Nie ma takiego wyboru :/')

# TODO: Price checker