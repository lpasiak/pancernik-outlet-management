
from datetime import datetime
import os
import config

def create_shoper_offers(shoper_client, gsheets_client):

    try:

        all_products = gsheets_client.select_offers_ready_to_publish()

        # print(all_products)

        counter_product = all_products.shape[0]
        counter_product_created = 0
        
        sheet_updates = []

        for index, row in all_products.iterrows():

            product_code = row['SKU']
            product_ean = row['EAN']
            damage_type = row['Uszkodzenie']
            date_created = datetime.today().strftime(r"%d-%m-%Y")

            try:
                product_id, product_url = shoper_client.create_a_product(
                    product_code = product_ean,
                    outlet_code = product_code,
                    damage_type = damage_type)
            
                product_url = f'{os.environ.get(f"SHOPERSITE_{config.SITE}")}{product_url}'

                google_sheets_row = all_products.loc[all_products['SKU'] == product_code, 'Row Number'].values

                if isinstance(product_id, int):
                    counter_product_created += 1
                    created = True

                    if len(google_sheets_row) > 0:
                        row_number = google_sheets_row[0]
                        sheet_updates.append([row_number, created, date_created, product_url, product_id])
                    else:
                        print(f"X | Warning: SKU {product_code} not found in Google Sheets!")

                print("-----------------------------------")
                print(f"{counter_product_created}/{counter_product} Products created")
                print(f"Product URL: {product_url}")
                print("-----------------------------------")

            except Exception as e:
                print("-----------------------------------")
                print(f'Failed to create a product. Error: {e}')
                print("-----------------------------------")
                
        if sheet_updates:
            gsheets_client.update_rows(sheet_updates)

    except Exception as e:
        print(f"Error: {e}")