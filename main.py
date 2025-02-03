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
        sheet_id=os.environ.get('SHEET_ID'),
        sheet_name='Test'
    )

    try:

        # Authenticate with the Shoper API
        shoper_client.connect()
        # gsheets_client.connect()

        # data = gsheets_client.select_offers_ready_to_publish()
        # shoper_client.get_limited_products(3)
        shoper_client.create_a_product(33, 'OUTLET_213722', 'USZ')
        # x = shoper_client.get_a_single_product(81740)
        # print(x)
        # shoper_client.get_all_products()
        # x = shoper_client.get_all_attribute_groups()
        # print(x)


    except Exception as e:
        print(f"Error: {e}")
