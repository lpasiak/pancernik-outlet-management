import gspread
import pandas as pd
from pathlib import Path
import os

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

        print("Connected to Google Sheets successfully.")

    def get_data(self):
        """Get data from a Google Sheets worksheet as a pandas DataFrame."""

        worksheet = self.sheet.worksheet(self.sheet_name)
        data = worksheet.get_all_values()
        all_offers = pd.DataFrame(data[1:], columns=data[0])  # First row as header
        all_offers.to_excel(os.path.join(self.sheets_dir, 'google_sheets_all.xlsx'), index=False)
        
        print('Downloaded all the data from Google Sheets.')
        return all_offers
    
    def select_offers_ready_to_publish(self):
        """Get data of all the items ready to publish based on 'Wystawione' column"""
        all_offers = self.get_data()

        selected_offers = all_offers[all_offers["Wystawione"] == 'FALSE']
        selected_offers.to_excel(os.path.join(self.sheets_dir, 'google_sheets_to_publish.xlsx'), index=False)
        
        print('Selected offers ready to publish.')
        return selected_offers

    def update_data(self, dataframe):
        """Update a worksheet with a pandas DataFrame."""
        
        worksheet = self.sheet.worksheet(self.sheet_name)
        worksheet.clear()
        worksheet.update([dataframe.columns.values.tolist()] + dataframe.values.tolist())
        
        print(f"Updated {self.sheet_name} with new data.")
