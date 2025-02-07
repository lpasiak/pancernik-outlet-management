from datetime import datetime
import os
import config

def create_shoper_offers(shoper_client, gsheets_client):
    try:
        all_products = gsheets_client.select_offers_ready_to_publish()
        if all_products.empty:
            print("No products found ready to publish")
            return

        counter_product = all_products.shape[0]
        counter_product_created = 0
        sheet_updates = []

        for index, row in all_products.iterrows():
            try:
                product_code = row['SKU']
                product_ean = row['EAN']
                damage_type = row['Uszkodzenie']

                if not all([product_code, product_ean, damage_type]):
                    print(f"Warning: Missing required fields for row {index}")
                    continue

                date_created = datetime.today().strftime(r"%d-%m-%Y")
                
                product_id, product_url = shoper_client.create_a_product(
                    product_code=product_ean,
                    outlet_code=product_code,
                    damage_type=damage_type
                )
                
                product_url = f'{os.getenv(f"SHOPERSITE_{config.SITE}")}/{product_url}'
                google_sheets_row = all_products.loc[all_products['SKU'] == product_code, 'Row Number'].values

                if not isinstance(product_id, int):
                    print(f"Warning: Invalid product ID received for SKU {product_code}")
                    continue

                counter_product_created += 1
                
                if len(google_sheets_row) > 0:
                    row_number = google_sheets_row[0]
                    sheet_updates.append([row_number, True, date_created, product_url, product_id])
                else:
                    print(f"Warning: SKU {product_code} not found in Google Sheets!")

                print("-----------------------------------")
                print(f"{counter_product_created}/{counter_product} Products created")
                print(f"Product URL: {product_url}")
                print("-----------------------------------")

            except Exception as e:
                print("-----------------------------------")
                print(f'Failed to create product {product_code}. Error: {str(e)}')
                print("-----------------------------------")
                
        if sheet_updates:
            try:
                gsheets_client.update_rows(sheet_updates)
            except Exception as e:
                print(f"Failed to update Google Sheets: {str(e)}")

    except Exception as e:
        print(f"Fatal error in create_shoper_offers: {str(e)}")
        raise

def set_main_product_attributes(shoper_client, gsheets_client):
    try:
        all_products = gsheets_client.get_data(include_row_numbers=True)
        if all_products.empty:
            print("No products found in sheets")
            return

        single_ean_products = all_products.drop_duplicates(subset=['EAN'], keep='first').copy()
        print(f'Created single product table with {len(single_ean_products)} unique EANs')

        products = {}
        for _, row_single in single_ean_products.iterrows():
            product_ean = row_single['EAN']
            product_ids_list = all_products[all_products['EAN'] == product_ean]['ID Shoper'].tolist()
            if product_ids_list:
                products[product_ean] = ', '.join(map(str, product_ids_list))

        # Move these to config
        ATTRIBUTE_IDS = {
            'MAIN': {'id': '1402', 'group': '577'},
            'TEST': {'id': '29', 'group': '9'}
        }
        
        if config.SITE not in ATTRIBUTE_IDS:
            raise ValueError(f"Unknown site configuration: {config.SITE}")
            
        attribute_id = ATTRIBUTE_IDS[config.SITE]['id']
        attribute_group = ATTRIBUTE_IDS[config.SITE]['group']

        for product_ean, attribute_value in products.items():
            try:
                shoper_client.upload_an_attribute_by_code(
                    product_ean,
                    attribute_id,
                    attribute_value,
                    attribute_group
                )
                print(f"Updated attributes for EAN: {product_ean}")
            except Exception as e:
                print(f"Failed to update attributes for EAN {product_ean}: {str(e)}")

    except Exception as e:
        print(f"Fatal error in set_main_product_attributes: {str(e)}")
        raise
