from odoo import api, fields, models
from odoo.exceptions import Warning
from odoo.exceptions import ValidationError


class Ubicacion(models.Model):
    _name = 'ubicacion'
    _description = 'ubicacion'
    _order = 'name'

    # Text fields
    name = fields.Char(
        'Title',
        default=None,
        index=True,
        readonly=False,
        required=False,
        translate=False,
    )

    company_id = fields.Many2one('res.company', 'Company', 
        default=lambda self: self.env['res.company']._company_default_get('ubicacion'))
    category_id = fields.Many2one('ubicacion.category', string='Category')

    #ubicaciones
    active = fields.Boolean(string='Activo?', default=True)
    product_id = fields.Many2one("product.product",'Producto')
    warehouse_id = fields.Many2one('stock.warehouse', string='Almacén')
    location_id = fields.Many2one('stock.location', string='Ubicacion de Inventarios')

    #mueble_many2one =  fields.Many2one('ubicacion',string='Mueble Test')
    mueble = fields.Char(string='Mueble')
    fila = fields.Char(string='Fila')
    columna = fields.Char(string='Columna')
    operating_unit_id = fields.Many2one(
        comodel_name='operating.unit',
        string='Operating Unit',
        required=False,
        default=lambda self: (self.env['res.users'].operating_unit_default_get(self.env.uid)))


