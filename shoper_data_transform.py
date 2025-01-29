import os

def transform_offer_to_product(source_product):
    """Transforms a downloaded Shoper offer into a ready-to-upload product."""
    
    final_product = {
        'producer_id': source_product['producer_id'],
        'category_id' : source_product['category_id'],
        'code': f'OUT_{source_product["code"]}',
        'pkwiu': source_product['pkwiu'],
        'categories': source_product['categories'],
        'translations': {
            "pl_PL": {
                'name': f'OUTLET: {source_product["translations"]["pl_PL"]["name"]}',
                'description': source_product["translations"]["pl_PL"]["description"],
                'active': True
            }
        },
        'stock': {
            'price': source_product['stock']['price'],
            'active': 1,
            'stock': 1,
            'gfx_id': source_product['main_image']['gfx_id']
        },
        'tax_id': source_product['tax_id'],
        'unit_id': source_product['unit_id'],
        'related': source_product['related']
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
