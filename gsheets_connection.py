import gspread
import pandas as pd

class GSheetsClient:

    def __init__(self, credentials, sheet_id):
        """
        Initialize the GSheetsClient with credentials and sheet ID.
        Args:
            credentials (str): Path to the service account JSON credentials file.
            sheet_id (str): Name of the environment variable storing the sheet ID.
        """

        self.credentials_path = credentials
        self.sheet_id = sheet_id
        self.gc = None
        self.sheet = None

    def connect(self):
        """Authenticate with Google Sheets."""

        self.gc = gspread.service_account(filename=self.credentials_path)
        self.sheet = self.gc.open_by_key(self.sheet_id)
        print("Connected to Google Sheets successfully.")

    def get_data(self, sheet_name):
        """Get data from a Google Sheets worksheet as a pandas DataFrame."""

        worksheet = self.sheet.worksheet(sheet_name)
        data = worksheet.get_all_values()
        df = pd.DataFrame(data[1:], columns=data[0])  # First row as header
        return df

    def update_data(self, sheet_name, dataframe):
        """Update a worksheet with a pandas DataFrame."""
        
        worksheet = self.sheet.worksheet(sheet_name)
        worksheet.clear()
        worksheet.update([dataframe.columns.values.tolist()] + dataframe.values.tolist())
        print(f"Updated {sheet_name} with new data.")