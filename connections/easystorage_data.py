import pandas as pd

class EasyStorageData:

    def __init__(self, file_path):
        self.file_path = file_path
        self.data = pd.read_excel(file_path)

        print("Easystorage Data downloaded.")
        print("-----------------------------------")
    
    @property
    def outlet_products(self):
        outlet_filter = (self.data['Strefa'] == 'KMP-OUTLET') & (self.data['Magazyn'] == 'MAG')
        return self.data[outlet_filter]
