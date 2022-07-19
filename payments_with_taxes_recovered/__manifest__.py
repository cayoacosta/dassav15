# -*- coding: utf-8 -*-
{
    'name': "TECNIKA - DASSA Payments with Taxes",

    'summary': """
        Tecnika - Dassa payments with calculated recovered taxes""",

    'description': """
        This module caculates the taxes in Payments. It separates the taxes for cash payments
        and credit payments
    """,

    'author': "TECNIKA GLOBAL",
    'website': "https://tecnika.com.mx/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '15.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_payment.xml',
        #'views/templates.xml',
    ],
    # only loaded in demonstration mode
    #'demo': [
    #    'demo/demo.xml',
    #],
}
