import operations
from connections import EasyStorageData
from connections import init_gsheets, init_shoper
from dotenv import load_dotenv
import os
import config

def load_environment():
    dotenv_path = os.path.join('credentials', 'env')
    load_dotenv(dotenv_path)

def get_user_action():
    return str(input(f'''
Co chcesz zrobić?
1. Wystawić produkty outletowe
2. Dopisać atrybuty outletowe głównym produktom
3. Pobrać wszystkie produkty
4. Obniżyć ceny starsze niż {config.DISCOUNT_DAYS} dni
5. Przenieść produkty do archiwum
q żeby wyjść.
Akcja: '''))

def main():

    load_environment()
    shoper_client = init_shoper()
    outlet_gsheets_client = init_gsheets()
    
    shoper_client.connect()
    outlet_gsheets_client.connect()

    while True:
        action = get_user_action()
        
        if action == '1':
            operations.create_shoper_offers(shoper_client, outlet_gsheets_client)
            outlet_gsheets_client.batch_move_products_to_lacking(shoper_client)
        elif action == '2':
            operations.set_main_product_attributes(shoper_client, outlet_gsheets_client)
            operations.update_attribute_group_categories(shoper_client, outlet_gsheets_client)
        elif action == '3':
            shoper_client.get_all_products()
        elif action == '4':
            operations.discount_offers(shoper_client, outlet_gsheets_client)
        elif action == '5':
            x = '''Czy pobrałeś wszystkie najnowsze produkty z EasyStorage? (t/n)\nAkcja: '''
            if input(x) == 't':

                try:
                    easystorage_data = EasyStorageData(config.EASYSTORAGE_PATH).outlet_products
                except FileNotFoundError:
                    print('No file easystorage.xlsx in data directory')
                    
                sold_products = outlet_gsheets_client.batch_move_sold_products_to_archived(shoper_client, easystorage_data)
                shoper_client.connect()
                
                if isinstance(sold_products, list):
                    shoper_client.remove_products_from_a_list(sold_products)
                else:
                    print('Nie ma sprzedanych produktów do usunięcia.')
                
                # Manage unsold products
                unsold_products = outlet_gsheets_client.batch_move_unsold_products_to_archived(shoper_client)
                shoper_client.connect()
                
                if isinstance(unsold_products, list):
                    shoper_client.remove_products_from_a_list(unsold_products)
                else:
                    print('Nie ma niesprzedanych produktów do usunięcia.')

            elif input(x) == 'n':
                print('Pobierz najnowsze produkty z EasyStorage i wrzuć je do "data/easystorage.xlsx".')
                continue
            else:
                print('Nie ma takiego wyboru :/')
        elif action == 'q':
            print('Do zobaczenia!')
            break
        else:
            print('Nie ma takiego wyboru :/')

if __name__ == "__main__":
    main()
