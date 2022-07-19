# -*- coding: utf-8 -*-
{
    'name': "TECNIKA - DASSA Get Stock Loccation",

    'summary': """
        Tecnika - Dassa gets exactly location for items""",

    'description': """
        This module gets the location definied in x_Ubicaciones for showing it 
        in the picking
    """,

    'author': "TECNIKA GLOBAL",
    'website': "https://tecnika.com.mx/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '15.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['stock'],

    # always loaded
    'data': [
        'views/stock_picking.xml',
    ],
}
