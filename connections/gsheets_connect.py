import gspread
import pandas as pd
from datetime import datetime
from pathlib import Path
import os, time, sys
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

        print(f"Google Authentication {self.sheet_name} successful.")
        print("-----------------------------------")

    def get_data(self, include_row_numbers=False):
        """Get data from a Google Sheets worksheet as a pandas DataFrame."""

        self.worksheet = self.sheet.worksheet(self.sheet_name)
        data = self.worksheet.get_all_values()
        
        df = pd.DataFrame(data[1:], columns=data[0])  # First row as header
        df.to_excel(os.path.join(self.sheets_dir, 'google_sheets_all.xlsx'), index=False)
        
        # Making sure the necessary data is properly formatted in gsheets
        df['SKU'] = df['SKU'].str.upper()
        df['Uszkodzenie'] = df['Uszkodzenie'].str.upper()

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
            ((today - all_offers['Data wystawienia']).dt.days >= config.DISCOUNT_DAYS)
        )
        selected_offers = all_offers[mask]

        if len(selected_offers) > 0:
            selected_offers.to_excel(os.path.join(self.sheets_dir, 'google_sheets_to_discount.xlsx'), index=False)
            print('Selected offers ready to be discounted.')
            print(selected_offers[['EAN', 'SKU']])
            print("-----------------------------------")
            while True:
                x = str(input('Should I proceed? (y/n): '))
                if x == 'y':
                    print('Continuing...')
                    break
                elif x == 'n':
                    print('Exiting...')
                    sys.exit()
                else:
                    print('Invalid input. Please enter y or n.')

        else:
            print('No offers ready to be discounted.')
            print("-----------------------------------")

        return selected_offers
    
    def select_offers_for_lacking(self, shoper_client):
        """Get data of all the items ready to be moved to lacking products (because they have no main product on Shoper)"""
        all_offers = self.get_data(include_row_numbers=True)

        columns_to_keep = ['Row Number', 'EAN', 'SKU', 'Nazwa', 'Uszkodzenie', 'Data']


        today = datetime.today().strftime('%d-%m-%Y')

        # Select offers that are not published, have a SKU, and have a date that is not today
        mask = (
            (all_offers["Wystawione"] != 'TRUE') & 
            (all_offers["SKU"].notna() & all_offers["SKU"].ne('') &
            (all_offers['Data'].fillna('') != today))
        )
        selected_offers = all_offers[mask].copy()
        selected_offers['Row Number'] = all_offers.loc[mask, 'Row Number']
        
        print('Checking if all the products exist on Shoper...')
        # If the product EAN exists in Shoper, drop the offer from the selected_offers df
        try:
            for index, row in selected_offers.iterrows():
                response = shoper_client.get_a_single_product_by_code(row['EAN'])
                
                if response is not None:
                    selected_offers = selected_offers.drop(index)
                    print(f'Product {row["EAN"]} exists on Shoper.')

            if selected_offers.empty:
                print('No products to move to lacking products.')
                print("-----------------------------------")
            else:
                print('The offers above will be moved to lacking products.')
                print("-----------------------------------")

        except Exception as e:
            print(f'Fatal Error in select_offers_for_lacking: {e}')
                
        return selected_offers[columns_to_keep]

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

    def batch_move_products_to_lacking(self, shoper_client):
        """Move products to lacking products sheet in batch."""
        
        try:
            self.df_to_move = self.select_offers_for_lacking(shoper_client)
            self.source_worksheet = self.sheet.worksheet(self.sheet_name)
            self.target_worksheet = self.sheet.worksheet(config.SHEET_LACKING_PRODUCTS_NAME)

            if self.df_to_move.empty:
                print("No products to move.")
                print("-----------------------------------")
                return

            # Convert DataFrame to list of lists for Google Sheets, dropping Row Number column
            df_without_rows = self.df_to_move.drop('Row Number', axis=1)
            values_to_append = df_without_rows.values.tolist()

            # Get current sheet dimensions and calculate needed rows
            current_rows = len(self.target_worksheet.get_all_values())
            needed_rows = current_rows + len(values_to_append)
            
            # Resize the sheet if necessary by adding empty rows
            if needed_rows > current_rows:
                self.target_worksheet.resize(rows=needed_rows)
            
            # Find the first empty row in target worksheet
            next_row = current_rows + 1  # Add 1 to start after the last row
            
            batch_data = [{
                'range': f'A{next_row}',
                'values': values_to_append
            }]

            # Perform the batch update
            try:
                self.target_worksheet.batch_update(batch_data)
                print(f"✓ | Successfully moved {len(values_to_append)} products to lacking products sheet.")
                print("-----------------------------------")
            except Exception as e:
                print(f"Failed to move products to lacking products sheet: {str(e)}")
                print("-----------------------------------")

            try:
                # Get row numbers to delete in reverse order to maintain correct indices
                row_numbers = sorted(self.df_to_move['Row Number'].tolist(), reverse=True)
                
                # Delete rows one by one from bottom to top
                for row_num in row_numbers:
                    time.sleep(1)  # Delay between deletions
                    self.source_worksheet.delete_rows(row_num)
                
                print(f"✓ | Successfully removed {len(row_numbers)} rows from outlet sheet.")
                print("-----------------------------------")
            except Exception as e:
                print(f"Failed to remove products from outlet sheet: {str(e)}")

        except Exception as e:
            print(f"Failed to move products to lacking products sheet: {str(e)}")
            raise

    def select_offers_sold(self, shoper_client, easystorage_data):

        try:
            start_time = time.time()

            self.easy_storage_data = easystorage_data
            self.easy_storage_data['SKU'] = self.easy_storage_data['SKU'].str.upper()
            self.easy_storage_sku_list = self.easy_storage_data['SKU'].tolist()

            gsheets_data = self.get_data(include_row_numbers=True)
            gsheets_data = gsheets_data[
                (gsheets_data['Wystawione'] == 'TRUE') & 
                (gsheets_data['ID Shoper'].notna()) & 
                (gsheets_data['ID Shoper'] != '') & 
                (gsheets_data['ID Shoper'] != 0)
            ]

            columns_to_keep = ['Row Number', 'EAN', 'SKU', 'Nazwa', 'Uszkodzenie', 'Data', 'Wystawione', 'Data wystawienia', 'Druga Obniżka', 'ID Shoper']
            gsheets_data = gsheets_data[columns_to_keep]
            gsheets_data['Status'] = 'Sprzedane'
            gsheets_data['Zutylizowane'] = 'TRUE'


            if gsheets_data.empty:
                return

            gsheets_data_length = len(gsheets_data)

            for index, row in gsheets_data.iterrows():

                product_sku = str(row['SKU'])
                product_data = shoper_client.get_a_single_product(row['ID Shoper'])
                product_stock = int(product_data['stock']['stock'])

                print(f'Analyzing product {product_sku} | {index + 1}/{gsheets_data_length}')
                # If product has 0 items on Shoper and it is not in easy storage warehouse
                if product_stock != 0 or product_sku in self.easy_storage_sku_list:
                    gsheets_data = gsheets_data.drop(index)

            print('-----------------------------------')
            print('Products to be removed from Shoper and moved to archived:')
            print(gsheets_data[['EAN', 'SKU']])
            print('-----------------------------------')

            while True:
                x = str(input('Should I proceed? (y/n): '))
                if x == 'y':
                    print('Continuing...')
                    break
                elif x == 'n':
                    print('Exiting...')
                    sys.exit()
                else:
                    print('Invalid input. Please enter y or n.')

            print('-----------------------------------')

            end_time = time.time()
            print(f"Total runtime of select_sold_products: {round(end_time - start_time, 2)} seconds")

            return gsheets_data
        except Exception as e:
            print(f"Fatal error in select_sold_products: {str(e)}")
            raise

    def batch_move_products_to_archived(self, shoper_client, easystorage_data):
        """Move products to sold products sheet in batch."""
        
        try:
            self.df_to_move = self.select_offers_sold(shoper_client, easystorage_data)
            self.source_worksheet = self.sheet.worksheet(self.sheet_name)
            self.target_worksheet = self.sheet.worksheet(config.SHEET_ARCHIVED_NAME)

            if self.df_to_move.empty:
                print("No products to move.")
                print("-----------------------------------")
                return

            # Convert DataFrame to list of lists for Google Sheets, dropping Row Number column
            df_without_rows = self.df_to_move.drop(['Row Number', 'ID Shoper'], axis=1)
            values_to_append = df_without_rows.values.tolist()

            # Get current sheet dimensions
            current_rows = len(self.target_worksheet.get_all_values())
            needed_rows = current_rows + len(values_to_append)
            
            # Resize the sheet if necessary by adding empty rows
            if needed_rows > current_rows:
                self.target_worksheet.resize(rows=needed_rows)
            
            # Find the first empty row in target worksheet
            next_row = current_rows + 1  # Add 1 to start after the last row
            
            batch_data = [{
                'range': f'A{next_row}',
                'values': values_to_append
            }]

            # Perform the batch update
            try:
                self.target_worksheet.batch_update(batch_data)
                print(f"✓ | Successfully moved {len(values_to_append)} products to archived products sheet.")
                print("-----------------------------------")
            except Exception as e:
                print(f"Failed to move products to archived products sheet: {str(e)}")
                print("-----------------------------------")

            # Get row numbers to delete in reverse order to maintain correct indices
            try:
                row_numbers = sorted(self.df_to_move['Row Number'].tolist(), reverse=True)
                
                # Delete rows with delay to avoid API rate limits
                print(f'Removing products from outlet sheet...')
                for row_num in row_numbers:
                    time.sleep(1)  # Delay between deletions
                    self.source_worksheet.delete_rows(row_num)

                print(f"✓ | Successfully removed {len(row_numbers)} rows from outlet sheet.")
                print("-----------------------------------")
            except Exception as e:
                print(f"Failed to remove products from outlet sheet: {str(e)}")

            return self.df_to_move
        
        except Exception as e:
            print(f"Failed to remove products sheet: {str(e)}")
            raise

    def _handle_worksheet_operation(self, operation, *args, **kwargs):
        """Handle worksheet operations with automatic retry on rate limit errors."""
        while True:
            try:
                if operation == 'delete_rows':
                    return self.source_worksheet.delete_rows(*args, **kwargs)
                # Add other worksheet operations as needed
                else:
                    raise ValueError(f"Unknown operation: {operation}")
            except gspread.exceptions.APIError as e:
                if "RESOURCE_EXHAUSTED" in str(e) or "RATE_LIMIT_EXCEEDED" in str(e):
                    # Default backoff of 1 second on rate limit
                    time.sleep(1)
                    continue
                else:
                    raise

    def delete_rows(self, row_num):
        return self._handle_worksheet_operation('delete_rows', row_num)
