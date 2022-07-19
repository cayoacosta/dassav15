# -*- coding: utf-8 -*-
{
    'name': "account_customization",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Cuentas contables de odoo modificaciones
    """,

    'author': "cayo acosta",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Contabilidad y Finanzas',
    'version': '15.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['account', 'sale_management','taller'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_invoice_view.xml',
        'views/account_journal_view.xml',
        'wizard/account_invoice_refund_view.xml',
    ],

}
