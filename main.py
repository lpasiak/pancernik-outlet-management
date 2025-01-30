from shoper_connection import ShoperAPIClient
from gsheets_connection import GSheetsClient
import os
from config import config

if __name__ == "__main__":

    shoper_client = ShoperAPIClient(
        site_url=os.environ.get(f'SHOPERSITE_{config['site']}'),
        login=os.environ.get(f'LOGIN_{config['site']}'),
        password=os.environ.get(f'PASSWORD_{config['site']}')
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
        shoper_client.create_a_product(81675, 'OUTLECIK', 'USZ')
        # x = shoper_client.get_a_single_product(10744)

    except Exception as e:
        print(f"Error: {e}")
