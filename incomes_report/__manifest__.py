# Copyright 2020, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).

{
    'name': 'TECNIKA - DASSA Incomes Report',
    'summary': 'Generate Incomes Report',
    'version': '15.0.1.0.0',
    'category': 'Reports',
    'author': "TECNIKA GLOBAL",
    'website': "https://tecnika.com.mx/",
    'license': 'LGPL-3',
    'depends': [
        'account',
    ],
    'data': [
        'views/incomes_report_view.xml',
        'wizard/incomes_report_wizard_view.xml',
        'security/ir.model.access.csv',
    ],
}
