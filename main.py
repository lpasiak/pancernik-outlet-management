from api_connection import ShoperAPIClient
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
        sheet_id=os.environ.get('SHEET_ID')    
    )

    try:

        # Authenticate with the Shoper API
        # shoper_client.connect()
        gsheets_client.connect()

        data = gsheets_client.get_data('Test')
        print(data)

    except Exception as e:
        print(f"Error: {e}")
