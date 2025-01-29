from shoper_connection import ShoperAPIClient
from gsheets_connection import GSheetsClient
import pandas as pd
import os


if __name__ == "__main__":

    shoper_client = ShoperAPIClient(
        site_url=os.environ.get('SHOPERSITE_TEST'),
        login=os.environ.get('LOGIN_TEST'),
        password=os.environ.get('PASSWORD_TEST')
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
        shoper_client.create_a_product()
        # shoper_client.get_a_single_product(9976)

    except Exception as e:
        print(f"Error: {e}")
