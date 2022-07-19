# -*- coding: utf-8 -*-
{
    'name': "ctt_dassa_reports",
    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '15.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['base','taller'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/external_layout_saldo_dassa.xml',
        'data/external_layout_standard_saldo_dassa.xml',
        'data/external_layout_modubic_dassa.xml',
        'data/external_layout_standard_modubic_dassa.xml',
        'data/external_layout_existvent_dassa.xml',
        'data/external_layout_standard_existvent_dassa.xml',
        'data/external_layout_ventdep_dassa.xml',
        'data/external_layout_standard_ventdep_dassa.xml',
        'data/paper_format_custom.xml',
        'views/wizard_reports.xml',
        'views/wizard_reports_menu_inherits.xml',
        'reports/existencia_modalidad_ubicacion_report.xml',
        'reports/saldos_report.xml',
        'reports/ventas_departamento.xml',
        'reports/exist_ventas_report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
