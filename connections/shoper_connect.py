import pandas as pd
import requests, time, os, json
from pathlib import Path
from . import shoper_data_transform
import config

class ShoperAPIClient:

    def __init__(self, site_url, login, password):

        self.site_url = site_url
        self.login = login
        self.password = password
        self.session = requests.Session()
        self.token = None

        self.sheets_dir = Path('sheets')
        self.sheets_dir.mkdir(exist_ok=True)

    def connect(self):
        """Authenticate with the API"""
        response = self.session.post(
            f'{self.site_url}/webapi/rest/auth',
            auth=(self.login, self.password)
        )

        if response.status_code == 200:
            self.token = response.json().get('access_token')
            self.session.headers.update({'Authorization': f'Bearer {self.token}'})
            print("Shoper Authentication successful.")
            print("-----------------------------------")
        else:
            raise Exception(f"Authentication failed: {response.status_code}, {response.text}")

    def _handle_request(self, method, url, **kwargs):
        """Handle API requests with automatic retry on 429 errors."""
        while True:
            response = self.session.request(method, url, **kwargs)

            if response.status_code == 429:  # Too Many Requests
                retry_after = int(response.headers.get('Retry-After', 1))
                print(f"Rate limit exceeded. Retrying after {retry_after} seconds...")
                time.sleep(retry_after)
            else:
                return response

    def get_all_products(self):
        products = []
        page = 1
        url = f'{self.site_url}/webapi/rest/products'

        print("Downloading all products.")
        while True: 
            params = {'limit': config.SHOPER_LIMIT, 'page': page}
            response = self._handle_request('GET', url, params=params)
            data = response.json()
            number_of_pages = data['pages']

            if response.status_code != 200:
                raise Exception(f"Failed to fetch data: {response.status_code}, {response.text}")

            page_data = response.json().get('list', [])

            if not page_data:  # If no data is returned
                break

            print(f'Page: {page}/{number_of_pages}')
            products.extend(page_data)
            page += 1

        df = pd.DataFrame(products)
        df.to_excel(os.path.join(self.sheets_dir, 'shoper_all_products.xlsx'), index=False)
        return df

    def get_limited_products(self, max_pages):
        products = []
        self.max_pages = max_pages
        url = f'{self.site_url}/webapi/rest/products'

        for page in range(1, max_pages + 1):
            params = {'limit': config.SHOPER_LIMIT, 'page': page}
            response = self._handle_request('GET', url, params=params)
            
            if response.status_code != 200:
                raise Exception(f"Failed to fetch data: {response.status_code}, {response.text}")

            data = response.json()
            page_data = data.get('list', [])

            if not page_data:  # Stop if there are no products
                break

            print(f'Page: {page}/{self.max_pages}')
            products.extend(page_data)

        df = pd.DataFrame(products)
        df.to_excel(os.path.join(self.sheets_dir, 'shoper_limited_products.xlsx'), index=False)

        return products
    
    def get_a_single_product(self, product_id):
        url = f'{self.site_url}/webapi/rest/products/{product_id}'
        photo_url = f'{self.site_url}/webapi/rest/product-images'
        
        photo_filter = {
            "filters": json.dumps({"product_id": product_id}),
            "limit": 50
        }

        response = self._handle_request('GET', url)
        photo_response = self._handle_request('GET', photo_url, params=photo_filter)

        product = response.json()
        product_photos = photo_response.json()['list']
        product['img'] = product_photos

        return product
    
    def get_a_single_product_by_code(self, product_code):
        url = f'{self.site_url}/webapi/rest/products'
        photo_url = f'{self.site_url}/webapi/rest/product-images'

        product_filter = {
            "filters": json.dumps({"stock.code": product_code})
        }

        try:
            response = self._handle_request('GET', url, params=product_filter)
            product_list = response.json().get('list', [])
            
            if not product_list:
                print(f'Product {product_code} doesn\'t exist')
                return None
            
            product = product_list[0]
            product_id = product['product_id']

            photo_filter = {
                "filters": json.dumps({"product_id": product_id}),
                "limit": 50
            }

            photo_response = self._handle_request('GET', photo_url, params=photo_filter)
            product_photos = photo_response.json()['list']
            product['img'] = product_photos

            return product
        
        except Exception as e:
            print(f'Error fetching product {product_code}: {str(e)}')
            return None

    def get_all_attribute_groups(self):
        attribute_groups = []
        page = 1
        url = f'{self.site_url}/webapi/rest/attribute-groups'

        print("Downloading all attribute groups.")
        while True:
            params = {'limit': config.SHOPER_LIMIT, 'page': page}
            response = self._handle_request('GET', url, params=params)
            data = response.json()
            number_of_pages = data['pages']

            if response.status_code != 200:
                raise Exception(f"Failed to fetch data: {response.status_code}, {response.text}")

            page_data = response.json().get('list', [])

            if not page_data:  # If no data is returned
                break

            print(f'Page: {page}/{number_of_pages}')
            attribute_groups.extend(page_data)
            page += 1

        df = pd.DataFrame(attribute_groups)
        df.to_excel(os.path.join(self.sheets_dir, 'shoper_all_attribute_groups.xlsx'), index=False)
        return attribute_groups

    def get_all_attributes(self):
        attributes = []
        page = 1
        url = f'{self.site_url}/webapi/rest/attributes'

        print("Downloading all attributes.")
        while True:
            params = {'limit': config.SHOPER_LIMIT, 'page': page}
            response = self._handle_request('GET', url, params=params)
            data = response.json()
            number_of_pages = data['pages']

            if response.status_code != 200:
                raise Exception(f"Failed to fetch data: {response.status_code}, {response.text}")

            page_data = response.json().get('list', [])

            if not page_data:  # If no data is returned
                break

            print(f'Page: {page}/{number_of_pages}')
            attributes.extend(page_data)
            page += 1

        df = pd.DataFrame(attributes)
        df.to_excel(os.path.join(self.sheets_dir, 'shoper_all_attributes.xlsx'), index=False)
        return df

    def get_all_categories(self):
        categories = []
        page = 1
        url = f'{self.site_url}/webapi/rest/categories'

        print("Downloading all categories.")
        while True:
            params = {'limit': config.SHOPER_LIMIT, 'page': page}
            response = self._handle_request('GET', url, params=params)
            data = response.json()
            number_of_pages = data['pages']

            if response.status_code != 200:
                raise Exception(f"Failed to fetch data: {response.status_code}, {response.text}")

            page_data = response.json().get('list', [])

            if not page_data:
                break
        
            print(f'Page: {page}/{number_of_pages}')
            categories.extend(page_data)
            page += 1
        
        df = pd.DataFrame(categories)
        df.to_excel(os.path.join(self.sheets_dir, 'shoper_all_categories.xlsx'), index=False)
        return df
    
    def create_a_product(self, product_code, outlet_code, damage_type):
        """Creates a product in Shoper API, then updates barcode, related products, and images separately."""
        
        # Step 1: Fetch source product data
        product = self.get_a_single_product_by_code(product_code)
        if not product:
            print(f"X | Error: Could not fetch source product with code {product_code}")
            return None
        
        product_id = product['product_id']
        
        # Step 2: Extract barcode and related products
        barcode = {'ean': str(product['code'])}
        related_products = {'related': product.get('related', [])}

        # Step 3: Transform product for API upload
        final_product, product_seo, product_category_id = shoper_data_transform.transform_offer_to_product(product, outlet_code, damage_type)

        # Step 4: Send POST request to create the product
        url = f'{self.site_url}/webapi/rest/products'
        try:
            response = self._handle_request('POST', url, json=final_product)
            response_data = response.json()

            if response.status_code != 200:
                try:
                    error_data = response.json()
                    error_message = error_data.get('error_description', 'Brak opisu błędu.')
                    print(f"X | Failed to create product. API response: {error_message}")
                except json.JSONDecodeError:
                    print(f"X | Failed to create product. Raw API Response: {response.text}")  
                return None
            
            final_product_id = response_data # Ensure we get the ID
            if not final_product_id:
                print("X | Product creation response missing product ID.")
                return None
            
            print(f"✓ | Product {barcode['ean']} created with ID: {final_product_id}")

        except Exception as e:
            print(f"X | Error creating product {product_id}: {e}")
            return None

        # Step 5: Update barcode
        update_product_url = f'{self.site_url}/webapi/rest/products/{final_product_id}'
        try:
            response = self._handle_request('PUT', update_product_url, json=barcode)
            if response.status_code == 200:
                print(f"✓ | Barcode {barcode['ean']} added to product {final_product_id}")
            else:
                print(f"X | Failed to upload barcode. API Response: {response.text}")
        except Exception as e:
            print(f"X | Error updating barcode for product {final_product_id}: {e}")

        # Step 6: Update related products
        if related_products['related']:
            try:
                response = self._handle_request('PUT', update_product_url, json=related_products)
                if response.status_code == 200:
                    print(f"✓ | Related products updated for {final_product_id}: {related_products['related']}")
                else:
                    print(f"X | Failed to update related products. API Response: {response.text}")
            except Exception as e:
                print(f"X | Error updating related products for {final_product_id}: {e}")

        # Step 7: Upload images
        final_product_photos = shoper_data_transform.transform_offer_photos(product, final_product_id)
        photo_url = f"{self.site_url}/webapi/rest/product-images"

        for photo in final_product_photos:
            try:
                response = self._handle_request('POST', photo_url, json=photo)
                if response.status_code == 200:
                    print(f"✓ | Uploaded image {photo['order']} successfully!")
                else:
                    print(f"X | Failed to upload image {photo['order']}. API Response: {response.text}")
            except Exception as e:
                print(f"X | Error uploading image {photo['order']} for product {final_product_id}: {e}")

        # Step 8: Upload a url

        if product_seo != None and product_seo != '':
            product_seo = f'{product_seo}-outlet-{final_product_id}'
        else:
            product_seo = f'outlet-{final_product_id}'

        product_seo_json = { 'translations': { 'pl_PL': { 'seo_url': product_seo }}}

        try:
            response = self._handle_request('PUT', update_product_url, json=product_seo_json)

            if response.status_code == 200:
                print(f"✓ | Uploaded url successfully!")

            else:
                print(f"X | Failed to upload a url. API Response: {response.text}")
                    
        except Exception as e:
            print(f"X | Error uploading a url for product {final_product_id}: {e}")

        return final_product_id, product_seo, product_category_id

    def upload_an_attribute_by_code(self, product_code, attribute_id, attribute_value):
        try:
            product = self.get_a_single_product_by_code(product_code)
            if not product:
                return

            product_id = product.get('product_id', '')
            attributes_to_upload = {'attributes': {attribute_id: attribute_value}}

            url = f'{self.site_url}/webapi/rest/products/{product_id}'

            try:
                response = self._handle_request('PUT', url, json=attributes_to_upload)
                if response.status_code == 200:
                    print(f"✓ | Attributes added to the product {product_code} | {product_id}")
                else:
                    print(f"X | Failed to upload attributes. API Response: {response.text}")
            except Exception as e:
                print(f"X | Error updating attributes to the product {product_code} | {product_id}: {e}")

        except Exception as e:
            print(f'Error: {e}')

    def get_attribute_group_info(self, group_id):
        """Get information about a specific attribute group."""
        url = f"{self.site_url}/webapi/rest/attribute-groups/{group_id}"
        try:
            response = self._handle_request('GET', url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting attribute group info: {str(e)}")
            raise
        
    def merge_attribute_group_categories(self, group_id, attribute_categories, category_id_list):
        """Update attribute group categories by merging existing and new categories."""
        
        # Convert to lists if they're numpy arrays
        attribute_categories = attribute_categories.tolist() if hasattr(attribute_categories, 'tolist') else list(attribute_categories)
        category_id_list = category_id_list.tolist() if hasattr(category_id_list, 'tolist') else list(category_id_list)
        
        # Merge lists and remove duplicates using set
        merged_categories = list(set(attribute_categories + category_id_list))
        print(f'Updating {len(merged_categories)} categories to a group {group_id}')

        # Update the attribute group with merged categories
        url = f"{self.site_url}/webapi/rest/attribute-groups/{group_id}"
        try:
            response = self._handle_request('PUT', url, json={'categories': merged_categories})
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error updating attribute group categories: {str(e)}")
            raise
        
    def discount_product(self, product_id):
        url = f"{self.site_url}/webapi/rest/products/{product_id}"
        
        try:
            get_product_response = self._handle_request('GET', url)
            product_price = float(get_product_response.json()['stock']['price'])
            discount_price = round(product_price * 0.8, 2)
            print(discount_price)

            update_product_response = self._handle_request('PUT', url, json={'stock': {'price': discount_price}})

            if update_product_response.status_code == 200:
                print(f"✓ | Product {product_id} discounted successfully!")

            else:
                print(f"X | Failed to discount product {product_id}. API Response: {update_product_response.text}")

        except Exception as e:  
            print(f"Error getting product price: {str(e)}")
            raise

        return update_product_response