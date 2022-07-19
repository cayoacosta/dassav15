from odoo import api, fields, models
from odoo import tools


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    mueble = fields.Char(comodel='product.product', 
    	related='product_id.ubicaciones_ids.mueble')
    fila = fields.Char(comodel='product.product', 
    	related='product_id.ubicaciones_ids.fila')
    columna = fields.Char(comodel='product.product', 
    	related='product_id.ubicaciones_ids.columna')