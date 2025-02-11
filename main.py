import operations
from connections import GSheetsClient, ShoperAPIClient 
from dotenv import load_dotenv
import os
import config

def load_environment():
    dotenv_path = os.path.join('credentials', 'env')
    load_dotenv(dotenv_path)

def initialize_shoper_client():
    return ShoperAPIClient(
        site_url=os.getenv(f'SHOPERSITE_{config.SITE}'),
        login=os.getenv(f'LOGIN_{config.SITE}'),
        password=os.getenv(f'PASSWORD_{config.SITE}')
    )

def initialize_gsheets_client():
    return GSheetsClient(
        credentials=os.path.join('credentials', 'gsheets_credentials.json'),
        sheet_id=os.getenv(f'SHEET_ID_{config.SHEET}'),
        sheet_name=config.SHEET_NAME
    )

def get_user_action():
    return str(input('''
Co chcesz zrobić?
1. Wystawić produkty outletowe
2. Dopisać atrybuty outletowe głównym produktom
3. Pobrać wszystkie produkty
q żeby wyjść.
Akcja: '''))

def main():

    load_environment()
    shoper_client = initialize_shoper_client()
    outlet_gsheets_client = initialize_gsheets_client()

    shoper_client.connect()
    outlet_gsheets_client.connect()

    while True:
        action = get_user_action()
        
        if action == '1':
            operations.create_shoper_offers(shoper_client, outlet_gsheets_client)
        elif action == '2':
            operations.update_attribute_group_categories(shoper_client, outlet_gsheets_client)
            operations.set_main_product_attributes(shoper_client, outlet_gsheets_client)
        elif action == '3':
            shoper_client.get_all_products()
        elif action == 'q':
            print('Do zobaczenia!')
        else:
            print('Nie ma takiego wyboru :/')

if __name__ == "__main__":
    main()
