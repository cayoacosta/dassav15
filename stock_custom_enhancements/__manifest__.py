# -*- coding: utf-8 -*-
{
    'name': "Stock Custom Enhancements",

    'summary': """
       Stock Enhancements
       """,

    'description': """
        Se agrego el seguimiento de cambios en el boton Active del modelo product.template.
    """,

    'author': "Jorge Orante",
    'website': "http://www.grupocadena.com/dassa/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Stock',
    'version': '15.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
