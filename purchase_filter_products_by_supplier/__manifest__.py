# -*- coding: utf-8 -*-
{
    'name': 'Filter products by supplier in purchase order',
    'version': '15.0.1.0.0',
    'category': 'Purchase',
    'author':  'Jamotion GmbH',
    'website': 'https://jamotion.ch',
    'summary': 'Product list filtered by seller',
    'images': ['static/description/screenshot.png'],
    'depends': [
        'purchase',
    ],
    'data': [
        # 'security/ir.model.access.csv',
         'views/res_partner.xml',
         'views/product_template.xml',
    ],
    'demo': [],
    'test': [],
    'application': False,
    'active': False,
    'installable': True,
}
