# -*- coding: utf-8 -*-
{
    'name': "Sales Custom Validations",

    'summary': """
            Validations for sales ...mainly
        """,

    'description': """
        Si es de contado, la forma de pago  no puede ser 99 (Por definir).
        Si el cliente no trae RFC no se debe facturar.
        Si el RFC es XXXXX (Publico general), no se puede facturar de credito.
        No se puede facturar sin termino de pago.
        Cuando se genere una nota de credito, el termino de pago debe de ser Contado,
        la forma de pago debe de ser Condonacion, y el uso debe de ser Devolciones,
        descuentos y bonificaciones, tambien esos campos tienen que ser solo lectura.
        Cuando la factura sea de maquinaria, y el producto deba llevar numero de serie.
        Si es una venta de maquinaria, se puede facturar a credito a Publico en general.
        Se agregaron Comercial (vendedor) y Equipo de ventas al modelo de Apuntes contables.
        Se agrego CFDI de origen a notas de credito de ventas.        
        Se agrego validacion para que el Comercial en facturas solo enliste usuarios internos.
        Se hizo requerido el campo "Referencia" de las facturas de proveedor.
    """,

    'author': "Jorge Orante",
    'website': "http://www.grupocadena.com/dassa/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Invoicing',
    'version': '15.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'l10n_mx_edi','sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_invoice_inherit_form_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
