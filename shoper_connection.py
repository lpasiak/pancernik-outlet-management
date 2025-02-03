import pandas as pd
import requests, time, os, json
from pathlib import Path
import shoper_data_transform
import config

class ShoperAPIClient:

    def __init__(self, site_url, login, password):

        self.site_url = site_url
        self.login = login
        self.password = password
        self.session = requests.Session()  # Maintain a session
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
            print("Authentication successful.")
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
    
    def create_a_product(self, product_id, outlet_code, damage_type):
        """Creates a product in Shoper API, then updates barcode, related products, and images separately."""
        
        # ✅ Step 1: Fetch source product data
        try:
            product = self.get_a_single_product(product_id)
        except Exception as e:
            print(f"❌ Error fetching product {product_id}: {e}")
            return None
        
        # ✅ Step 2: Extract barcode and related products
        barcode = {'ean': str(product['code'])}
        related_products = {'related': product.get('related', [])}

        # ✅ Step 3: Transform product for API upload
        final_product = shoper_data_transform.transform_offer_to_product(product, outlet_code, damage_type)

        # ✅ Step 4: Send POST request to create the product
        url = f'{self.site_url}/webapi/rest/products'
        try:
            response = self._handle_request('POST', url, json=final_product)
            response_data = response.json()

            if response.status_code != 200:
                print(f"❌ Failed to create product. API response: {response.text}")
                return None
            
            final_product_id = response_data # Ensure we get the ID
            if not final_product_id:
                print("❌ Product creation response missing product ID.")
                return None
            
            print(f"✅ Product {barcode['ean']} created with ID: {final_product_id}")

        except Exception as e:
            print(f"❌ Error creating product {product_id}: {e}")
            return None

        # ✅ Step 5: Update barcode
        update_product_url = f'{self.site_url}/webapi/rest/products/{final_product_id}'
        try:
            response = self._handle_request('PUT', update_product_url, json=barcode)
            if response.status_code == 200:
                print(f"✅ Barcode {barcode['ean']} added to product {final_product_id}")
            else:
                print(f"❌ Failed to upload barcode. API Response: {response.text}")
        except Exception as e:
            print(f"❌ Error updating barcode for product {final_product_id}: {e}")

        # ✅ Step 6: Update related products
        if related_products['related']:
            try:
                response = self._handle_request('PUT', update_product_url, json=related_products)
                if response.status_code == 200:
                    print(f"✅ Related products updated for {final_product_id}: {related_products['related']}")
                else:
                    print(f"❌ Failed to update related products. API Response: {response.text}")
            except Exception as e:
                print(f"❌ Error updating related products for {final_product_id}: {e}")

        # ✅ Step 7: Upload images
        final_product_photos = shoper_data_transform.transform_offer_photos(product, final_product_id)
        photo_url = f"{self.site_url}/webapi/rest/product-images"

        for photo in final_product_photos:
            try:
                response = self._handle_request('POST', photo_url, json=photo)
                if response.status_code == 200:
                    print(f"✅ Uploaded image {photo['order']} successfully!")
                else:
                    print(f"❌ Failed to upload image {photo['order']}. API Response: {response.text}")
            except Exception as e:
                print(f"❌ Error uploading image {photo['order']} for product {final_product_id}: {e}")

        return final_product_id
