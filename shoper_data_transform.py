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
    tags = [6] if config.SITE == 'MAIN' else [1]
    category_list = additional_outlet_category(source_product['attributes'], source_product['categories'])

    final_product = {
        'producer_id': source_product['producer_id'],
        'category_id' : source_product['category_id'],
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

    if product_attribute_dict != []:

        if config.SITE == 'MAIN':
            product_type = product_attribute_dict['550']['1370']
        elif config.SITE == 'TEST':
            product_type = product_attribute_dict['8']['28']

    
    if config.SITE == 'MAIN':
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
            if "uchwyt" in product_type and "telefon" in product_type:
                outlet_category = 7540
            else:
                outlet_category = 7525

        print(f"Selected Category: {outlet_category}")  # ✅ Debugging output

    elif config.SITE == 'TEST':
        outlet_category = 1322
    
    print(categories + [outlet_category])
    return categories + [outlet_category]