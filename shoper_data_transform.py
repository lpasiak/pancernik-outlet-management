import os, random
from data import info
import config

def transform_offer_to_product(source_product, outlet_code, damage_type):
    """Transforms a downloaded Shoper offer into a ready-to-upload product."""

    outlet_description = info.damage_types_long[damage_type]
    source_description = source_product["translations"]["pl_PL"]["description"]
    product_description = outlet_description + source_description

    product_description_short = info.damage_types_short[damage_type]

    outlet_price = set_outlet_price(source_product)
    attributes = source_product['attributes']
    # attributes = change_outlet_attributes(source_attributes)

    tags = [6] if config.SITE == 'MAIN' else [1]
    
    final_product = {
        'producer_id': source_product['producer_id'],
        'category_id' : source_product['category_id'],
        'categories': source_product['categories'],
        'code': outlet_code,
        'ean': source_product.get('ean', ''),
        'additional_producer': source_product.get('additional_producer', ''),
        'pkwiu': source_product['pkwiu'],
        'translations': {
            "pl_PL": {
                'name': f'OUTLET: {source_product["translations"]["pl_PL"]["name"]}',
                'short_description': product_description_short,
                'description': product_description,
                'active': '1',
                'order': random.randint(1,5),
                'seo_url': source_product['translations']['pl_PL'].get('seo_url', '') + '-outlet-' + str(random.randint(1, 9999))
            }
        },
        'stock': {
            'price': outlet_price,
            'active': 1,
            'stock': 1,
            'gfx_id': source_product['main_image']['gfx_id'],
            'availability_id': source_product.get('availability_id', ''),
            'delivery_id': 1,
            'weight': 0.2,
            'weight_type': source_product.get('weight_type', ''),
        },
        'tax_id': source_product['tax_id'],
        'unit_id': source_product['unit_id'],
        'related': source_product['related'],
        'vol_weight': source_product['vol_weight'],
        'currency_id': source_product['currency_id'],
        'gauge_id': source_product['gauge_id'],
        'unit_price_calculation': source_product['unit_price_calculation'],
        'newproduct': False,
        'tags': tags,
        'type': source_product['type'],
        'safety_information': source_product['safety_information'],
        'feeds_excludes': source_product['feeds_excludes'],
        # 'attributes': attributes,
    }

    return final_product

def set_outlet_price(source_product):

    if source_product['promo_price']:
        price = source_product['promo_price']
    else:
        price = source_product['stock']['price']

    price = float(price) * 0.8
    return price

def transform_offer_photos(source_product, new_product_id):

    source_images = source_product['img']
    final_images = []

    for index, image in enumerate(source_images, start=1):

        # Creating a url for an image
        site_url = f"{os.environ.get(f'SHOPERSITE_{config.SITE}')}"
        image_id = f"{image['gfx_id']}.{image['extension']}"

        image_item = {
            'product_id': new_product_id,
            'url': f"{site_url}/userdata/public/gfx/{image_id}",
            'is_main': 1 if index == 1 else 0,
            'order': index,
            'name': f'{new_product_id}_{index}'
        }

        final_images.append(image_item)

    return final_images

def translate_attribute_group_ids():
    pass

def translate_attribute_ids():
    pass

# def select_additional_outlet_category(attributes):

#     # Select 'product type' attribute by ID
#     product_type = attributes.get(550, {}).get(1370, None)
    
#     if product_type is None:
#         print("Warning: Product type attribute (550, 1370) not found!")
#         return None

#     category_id = {
#         'Outlet': 7525,
#         'Słuchawki': 7611,
#         'Pasek do smartwatcha': 7612,
#         'Adapter': 7547,
#         'Ładowarka sieciowa': 7537,
#         'Ładowarka samochodowa': 7538,
#         'Ładowarka indukcyjna': 7539,
#         'Uchwyt do telefonu': 7540, #???
#         'Powerbank': 7541,
#         'Kabel': 7542,
#         'Listwa zasilająca': 7543,
#         'Rysik': 7544,
#         'Obiektyw do telefonu': 7545,
#         'Akcesoria rowerowe': 7546,
#         'Selfie-Stick': 7548
#     }

# def change_outlet_attributes(attributes):

#     if 577 in attributes and 1402 in attributes[577]:
#         attributes[577][1402] = ''
#     else:
#         print("Warning: attributes[577][1402] not found!")

#     if 593 in attributes and 1538 in attributes[593]:
#         attributes[593][1538] = 'Tak'
#     else:
#         print("Warning: attributes[593][1538] not found!")

#     return attributes

