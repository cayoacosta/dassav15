# -*- coding: utf-8 -*-

{
    'name': 'Customer Credit Limit',
    'version': '15.0.1.0',
    'summary': 'An advanced way to handle customer credit limit through warning and blocking stage.',
    'description': """This module helps you to handle customer credit limit in an efficient way.
                You can set a warning stage and blocking stage to a particular customer.
                This module also shows the due amount of a customer while creating an order.""",
    'category': 'Sales',
    'author': 'Jonatan',
    'company': '',
    'maintainer': '',
    'depends': ['base', 'sale', 'sale_management', 'account'],
    'website': '',
    'data': [
        'views/sale_order_view.xml',
        'views/res_partner_view.xml',
        'views/account_payment_term_view.xml',
        'views/product_pricelist_views.xml',
        'views/product_category_views.xml',
        'views/sale_order_line_view.xml',
        'security/sales_credit_limit_data.xml',
    ],
    'qweb': [],
    'images': ['static/description/banner.jpg'],
    'license': 'OPL-1',
    'price': 1,
    'currency': 'MXN',
    'installable': True,
    'auto_install': False,
    'application': False,
}
