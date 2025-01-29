import pandas as pd
import requests
import time
from pathlib import Path
import os

class ShoperAPIClient:

    def __init__(self, site_url, login, password):
        """
        Initialize the ShoperAPIClient with store ID and login/password credentials.
        Args:
            site_url (str)
            login (str)
            password (str)
        """
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

        while True:
            params = {'limit': 50, 'page': page}
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

        products.to_excel(os.path.join(self.sheets_dir, 'shoper_all_products.xlsx'), index=False)
        return products
    
    import os

    def get_limited_products(self, max_pages):
        products = []
        self.max_pages = max_pages
        url = f'{self.site_url}/webapi/rest/products'

        for page in range(1, max_pages + 1):
            params = {'limit': 50, 'page': page}
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
    
    def get_all_categories(self):
        categories = []
        page = 1
        url = f'{self.site_url}/webapi/rest/categories'

        while True:
            params = {'limit': 50, 'page': page}
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
        
        categories.to_excel(os.path.join(self.sheets_dir, 'shoper_all_categories.xlsx'), index=False)
        return categories

    def get_all_special_offers(self):
        special_offers = []
        page = 1
        url = f'{self.site_url}/webapi/rest/specialoffers'

        while True:
            params = {'limit': 50, 'page': page}
            response = self._handle_request('GET', url, params=params)

            if response.status_code != 200:
                raise Exception(f"Failed to fetch data: {response.status_code}, {response.text}")

            page_data = response.json().get('list', [])

            if not page_data:  # If no data is returned
                break

            print(f'Page: {page}')
            special_offers.extend(page_data)
            page += 1

        special_offers.to_excel(os.path.join(self.sheets_dir, 'shoper_all_special_offers.xlsx'), index=False)
        return special_offers

    def get_all_special_offers_with_ean(self):
        products = self.get_all_products()
        special_offers = self.get_all_special_offers()

        df_products = pd.DataFrame(products)
        df_special_offers = pd.DataFrame(special_offers)

        df = pd.merge(df_special_offers, df_products, on="product_id")
        code_column = df.pop('code')
        df.insert(0, 'code', code_column)
        id_column = df.pop('product_id')
        df.insert(0, 'product_id', id_column)

        df.to_excel(os.path.join(self.sheets_dir, 'shoper_special_offers_with_ean.xlsx'), index=False)
        return df

    def create_special_offers(self, special_offer):
        url = f'{self.site_url}/webapi/rest/specialoffers'
        response = self._handle_request('POST', url, json=special_offer)

        if response.status_code != 200:
            raise Exception(f"Failed to create special offer: {response.status_code}, {response.text}")

        return response