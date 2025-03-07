import os, random
from data import info
import config

def transform_offer_to_product(source_product, outlet_code, damage_type):
    """Transforms a downloaded Shoper offer into a ready-to-upload product."""

    outlet_description = info.damage_types_long[damage_type]
    outlet_description = outlet_description.replace('[SKU_OUTLET_CODE]', outlet_code)
    source_description = source_product["translations"]["pl_PL"]["description"]
    product_description = outlet_description + source_description
    product_description_short = info.damage_types_short[damage_type]
    outlet_price = set_outlet_price(source_product)
    tags = [6] if config.SITE == 'MAIN' else [1]
    product_type = None

    # Safely get gfx_id
    try:
        gfx_id = source_product['img'][0]['gfx_id']
    except (KeyError, IndexError, TypeError):
        gfx_id = None
        print(f"Warning: No valid image found for product {outlet_code}")

    # Fix the product type handling
    if source_product['attributes'] != []:
        try:
            if config.SITE == 'MAIN':
                product_type = source_product['attributes']['550']['1370']
            elif config.SITE == 'TEST':
                product_type = source_product['attributes']['8']['28']
            else:
                raise ValueError(f"Unknown site configuration: {config.SITE}")
        except (KeyError, TypeError):
            print(f"Warning: Could not determine product type for {outlet_code}")
            product_type = None

    # Get category list with safe product_type
    category_list = additional_outlet_category(source_product['attributes'], source_product['categories'])

    product_url = source_product['translations']['pl_PL'].get('seo_url', '')
    product_category_id = source_product['category_id']

    final_product = {
        'producer_id': source_product['producer_id'],
        'category_id': source_product['category_id'],
        'categories': category_list,
        'code': outlet_code,
        'additional_producer': source_product.get('additional_producer', ''),
        'pkwiu': source_product['pkwiu'],
        'translations': {
            "pl_PL": {
                'name': f'OUTLET: {source_product["translations"]["pl_PL"]["name"]}',
                'short_description': product_description_short,
                'description': product_description,
                'active': '1',
                'order': random.randint(1,5)
            }
        },
        'stock': {
            'price': outlet_price,
            'active': 1,
            'stock': 1,
            'gfx_id': gfx_id,
            'availability_id': None,
            'delivery_id': 1,
            'weight': 0.2,
            'weight_type': source_product.get('weight_type', ''),
        },
        'tax_id': source_product['tax_id'],
        'unit_id': source_product['unit_id'],
        'vol_weight': source_product['vol_weight'],
        'currency_id': source_product['currency_id'],
        'gauge_id': source_product['gauge_id'],
        'unit_price_calculation': source_product['unit_price_calculation'],
        'newproduct': False,
        'tags': tags,
        'type': source_product['type'],
        'safety_information': source_product['safety_information'],
        'feeds_excludes': source_product['feeds_excludes'],
    }

    if source_product['attributes'] != []:
        final_product['attributes'] = transform_attributes(source_product['attributes'])

    # print("Final product JSON:", json.dumps(final_product, indent=4, ensure_ascii=False))

    return final_product, product_url, product_category_id

def set_outlet_price(source_product):

    if source_product['promo_price']:
        price = source_product['promo_price']
    else:
        price = source_product['stock']['price']

    price = float(price) * 0.8
    return price


def transform_offer_photos(source_product, new_product_id):
    if not source_product.get('img'):
        return []
    
    source_images = source_product['img']
    final_images = []

    for image in source_images:

        # Creating a url for an image
        site_url = f"{os.getenv(f'SHOPERSITE_{config.SITE}')}"
        image_id = f"{image['gfx_id']}.{image['extension']}"

        image_item = {
            'product_id': new_product_id,
            'url': f"{site_url}/userdata/public/gfx/{image_id}",
            'main': str(image['main']),
            'order': image['order'],
            'name': image['translations']['pl_PL']['name']
        }

        final_images.append(image_item)
        final_images.sort(key=lambda x: x['order'])

    return final_images

def transform_attributes(product_attribute_dict):

    attribute_dict = {}

    for group, attributes in product_attribute_dict.items():
        if isinstance(attributes, dict):
            for key, value in attributes.items():
                attribute_dict[key] = value

    if config.SITE == 'MAIN':
        attribute_dict['1402'] = ''     # _outlet
        attribute_dict['1538'] = 'Tak'  # Outlet
    
    return attribute_dict

def additional_outlet_category(product_attribute_dict, categories):
    if not isinstance(categories, list):
        raise ValueError("Categories must be a list")
    
    product_type = None
    
    if product_attribute_dict != []:
        try:
            if config.SITE == 'MAIN':
                product_type = product_attribute_dict['550']['1370']
            elif config.SITE == 'TEST':
                product_type = product_attribute_dict['8']['28']
            else:
                raise ValueError(f"Unknown site configuration: {config.SITE}")
        except (KeyError, TypeError):
            print("Warning: Could not determine product type from attributes")
            product_type = None

    if config.SITE == 'MAIN':
        
        if product_type:
            product_type = product_type.lower()

            category_mapping = {
                'słuchawki': 7611,
                'pasek do smartwatcha': 7612,
                'adapter': 7547,
                'ładowarka sieciowa': 7537,
                'ładowarka samochodowa': 7538,
                'ładowarka indukcyjna': 7539,
                'powerbank': 7541,
                'kabel': 7542,
                'listwa zasilająca': 7543,
                'rysik': 7544,
                'obiektyw do telefonu': 7545,
                'akcesoria rowerowe': 7546,
                'selfie-stick': 7548
            }

            outlet_category = category_mapping.get(product_type)

            if outlet_category is None:
                if product_type and "uchwyt" in product_type and "telefon" in product_type:
                    outlet_category = 7540
                else:
                    outlet_category = 7525
        else:
            outlet_category = 7525  # Default category when product_type is None

    elif config.SITE == 'TEST':
        outlet_category = 1322
    
    return categories + [outlet_category]