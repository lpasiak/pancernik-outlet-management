from shoper_connection import ShoperAPIClient
from gsheets_connection import GSheetsClient
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
        products_to_create = gsheets_client.get_data()
        print(all_products)

        for index, row in all_products.iterrows():

            product_code = row['SKU']
            product_ean = row['EAN']
            damage_type = row['Uszkodzenie']

            x = shoper_client.create_a_product(
                product_code = product_ean,
                outlet_code = product_code,
                damage_type = damage_type)
            
            print(x)

        # TODO: Update dataframe

        # Paste the entire dataframe

    except Exception as e:
        print(f"Error: {e}")
