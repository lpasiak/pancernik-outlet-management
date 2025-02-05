import operations
from gsheets_connection import GSheetsClient
from shoper_connection import ShoperAPIClient
import os
import config

if __name__ == "__main__":

    shoper_client = ShoperAPIClient(
        site_url=os.environ.get(f'SHOPERSITE_{config.SITE}'),
        login=os.environ.get(f'LOGIN_{config.SITE}'),
        password=os.environ.get(f'PASSWORD_{config.SITE}')
    )

    gsheets_client_main = GSheetsClient(
        credentials=os.path.join('credentials', 'gsheets_credentials.json'),
        sheet_id=os.environ.get(f'SHEET_ID_{config.SHEET}'),
        sheet_name=config.SHEET_NAME
    )

    shoper_client.connect()
    gsheets_client_main.connect()

    # operations.create_shoper_offers(shoper_client, gsheets_client)


# TODO: Attributes uploader

    all_products = gsheets_client_main.get_data(include_row_numbers=True)
    print(all_products)

    # MAIN attribute number 577 - 1402
    # TEST attribute number 9 - 29

# TODO: 
# TODO: Price checker