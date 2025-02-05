from shoper_connection import ShoperAPIClient
from gsheets_connection import GSheetsClient
from datetime import datetime
import os
import config

if __name__ == "__main__":

    shoper_client = ShoperAPIClient(
        site_url=os.environ.get(f'SHOPERSITE_{config.SITE}'),
        login=os.environ.get(f'LOGIN_{config.SITE}'),
        password=os.environ.get(f'PASSWORD_{config.SITE}')
    )

    gsheets_client = GSheetsClient(
        credentials=os.path.join('credentials', 'gsheets_credentials.json'),
        sheet_id=os.environ.get(f'SHEET_ID_{config.SHEET}'),
        sheet_name=config.SHEET_NAME
    )

    try:

        # Authenticate with the Shoper API
        shoper_client.connect()
        gsheets_client.connect()

        all_products = gsheets_client.select_offers_ready_to_publish()
        all_products = all_products.head(5)

        # print(all_products)

        counter_product = all_products.shape[0]
        counter_product_created = 0
        
        for index, row in all_products.iterrows():

            product_code = row['SKU']
            product_ean = row['EAN']
            damage_type = row['Uszkodzenie']
            date_created = datetime.today().strftime(r"%d-%m-%Y")

            product_id, product_url = shoper_client.create_a_product(
                product_code = product_ean,
                outlet_code = product_code,
                damage_type = damage_type)
            
            product_url = f'{os.environ.get(f"SHOPERSITE_{config.SITE}")}{product_url}'

            if isinstance(product_id, int):
                counter_product_created += 1

            print("-----------------------------------")
            print(f"{counter_product_created}/{counter_product} Products created")
            print(f"Product URL: {product_url}")
            print("-----------------------------------")

        # TODO: Update dataframe

        # Paste the entire dataframe

    except Exception as e:
        print(f"Error: {e}")
