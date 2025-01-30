import os, random
from data import info

def transform_offer_to_product(source_product, outlet_code, damage_type):
    """Transforms a downloaded Shoper offer into a ready-to-upload product."""

    outlet_description = info.damage_types_long[damage_type]
    source_description = source_product["translations"]["pl_PL"]["description"]
    product_description = outlet_description + source_description

    product_description_short = info.damage_types_short[damage_type]

    attributes = source_product['attributes']
    
    final_product = {
        'producer_id': source_product['producer_id'],
        'category_id' : source_product['category_id'],
        'categories': source_product['categories'],
        'code': outlet_code,
        'ean': source_product['code'],
        'pkwiu': source_product['pkwiu'],
        'translations': {
            "pl_PL": {
                'name': f'OUTLET: {source_product["translations"]["pl_PL"]["name"]}',
                'short_description': product_description_short,
                'description': product_description,
                'active': True,
                'order': random.randint(1,5)
            }
        },
        'stock': {
            'price': float(source_product['stock']['price']) * 0.8,
            'active': 1,
            'stock': 1,
            'gfx_id': source_product['main_image']['gfx_id']
        },
        'tax_id': source_product['tax_id'],
        'unit_id': source_product['unit_id'],
        'related': source_product['related'],
        'vol_weight': source_product['vol_weight'],
        'currency_id': source_product['currency_id'],
        'gauge_id': source_product['gauge_id'],
        'unit_price_calculation': source_product['unit_price_calculation'],
        'newproduct': False,
        'type': source_product['type'],
        'safety_information': source_product['safety_information'],
        'feeds_excludes': source_product['feeds_excludes'],
        'tags': [6], # outlet
        'attributes': attributes,
        'options': source_product['options']
    }

    return final_product

def transform_offer_photos(source_product, new_product_id):

    source_images = source_product['img']
    final_images = []

    for index, image in enumerate(source_images, start=1):

        image_item = {
            'product_id': new_product_id,
            'url': f"{os.environ.get('SHOPERSITE_TEST')}/userdata/public/gfx/{image['gfx_id']}.{image['extension']}",
            'is_main': 1 if index == 1 else 0,
            'order': index,
            'name': f'{new_product_id}_{index}'
        }

        final_images.append(image_item)

    return final_images
