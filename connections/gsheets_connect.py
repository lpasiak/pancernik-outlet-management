import gspread
import pandas as pd
from datetime import datetime
from pathlib import Path
from datetime import timedelta
import os
import config

class GSheetsClient:

    def __init__(self, credentials, sheet_id, sheet_name):
        """
        Initialize the GSheetsClient with credentials and sheet ID.
        Args:
            credentials (str): Path to the service account JSON credentials file.
            sheet_id (str): Name of the environment variable storing the sheet ID.
            sheet_name (str): Name of the specific sheet.
        """

        self.credentials_path = credentials
        self.sheet_id = sheet_id
        self.gc = None
        self.sheet = None
        self.sheet_name = sheet_name

        # We will save downloaded data in Excel in 'sheets' directory.
        # It needs to be created if it doesn't exist in our local files.
        self.sheets_dir = Path('sheets')
        self.sheets_dir.mkdir(exist_ok=True)


    def connect(self):
        """Authenticate with Google Sheets."""

        self.gc = gspread.service_account(filename=self.credentials_path)
        self.sheet = self.gc.open_by_key(self.sheet_id)

        print("Google Authentication successful.")
        print("-----------------------------------")

    def get_data(self, include_row_numbers=False):
        """Get data from a Google Sheets worksheet as a pandas DataFrame."""

        self.worksheet = self.sheet.worksheet(self.sheet_name)
        data = self.worksheet.get_all_values()
        
        df = pd.DataFrame(data[1:], columns=data[0])  # First row as header
        df.to_excel(os.path.join(self.sheets_dir, 'google_sheets_all.xlsx'), index=False)
        
        if include_row_numbers:
            df.insert(0, 'Row Number', range(2, len(df) + 2)) # GSheets rows start at 2

        print('Downloaded all the data from Google Sheets.')
        print("-----------------------------------")
        return df
    
    def select_offers_ready_to_publish(self):
        """Get data of all the items ready to publish based on 'Wystawione' column"""
        all_offers = self.get_data(include_row_numbers=True)
        
        # Use datetime object and convert to string in the same format as stored in sheets
        today = datetime.today().strftime('%d-%m-%Y')

        # Select offers that are not published, have a SKU, and have a date that is not today
        mask = (
            (all_offers["Wystawione"] != 'TRUE') & 
            (all_offers["SKU"].notna() & all_offers["SKU"].ne('')) & 
            (all_offers['Data'].fillna('') != today)
        )
        selected_offers = all_offers[mask]

        selected_offers.to_excel(os.path.join(self.sheets_dir, 'google_sheets_to_publish.xlsx'), index=False)
        
        print('Selected offers ready to publish.')
        print("-----------------------------------")
        return selected_offers

    def get_all_category_ids(self):
        """Get all category IDs from the Google Sheets."""
        all_categories = self.get_data(include_row_numbers=True)
        
        # Filter out empty values and convert to integers
        category_ids = all_categories['ID Kategorii'].dropna()  # Remove empty/NaN values
        category_ids = category_ids[category_ids != '']  # Remove empty strings
        category_ids = category_ids.astype(int).unique()  # Convert to integers and get unique values
        
        return category_ids

    def select_offers_for_discount(self):
        """Get data of all the items ready for discount based on publication date"""
        all_offers = self.get_data(include_row_numbers=True)
        
        # Convert publication dates to datetime
        all_offers['Data wystawienia'] = pd.to_datetime(all_offers['Data wystawienia'], format='%d-%m-%Y')
        today = pd.Timestamp.today()

        # Create mask for filtering
        mask = (
            (all_offers["Wystawione"] == 'TRUE') & 
            (all_offers["SKU"].notna() & all_offers["SKU"].ne('')) &
            (all_offers["Druga Obniżka"] == 'FALSE') &
            ((today - all_offers['Data wystawienia']).dt.days > config.DISCOUNT_DAYS)
        )
        selected_offers = all_offers[mask]

        if len(selected_offers) > 0:
            selected_offers.to_excel(os.path.join(self.sheets_dir, 'google_sheets_to_discount.xlsx'), index=False)
            print('Selected offers ready to be discounted.')
            print("-----------------------------------")
        else:
            print('No offers ready to be discounted.')
            print("-----------------------------------")

        return selected_offers
    
    def update_rows_of_created_offers(self, updates):

        batch_data = []
        self.worksheet = self.sheet.worksheet(self.sheet_name)
    
        for row_number, created, date_created, product_url, product_id, product_category_id in updates:
            batch_data.append({
                'range': f"F{row_number}:J{row_number}",
                'values': [[created, date_created, product_url, product_id, product_category_id]]
            })

        self.worksheet.batch_update(batch_data)

        print(f"✓ | Successfully updated {len(updates)} rows in Google Sheets.")

    def update_rows_of_discounted_offers(self, updates):

        batch_data = []
        self.worksheet = self.sheet.worksheet(self.sheet_name)
    
        for row_number, discounted in updates:
            batch_data.append({
                'range': f"K{row_number}",
                'values': [[discounted]]
            })

        self.worksheet.batch_update(batch_data)

        print(f"✓ | Successfully updated {len(updates)} rows in Google Sheets.")