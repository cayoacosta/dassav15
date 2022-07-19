# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError


class PurchaseOrderLine(models.Model):
    # Private attributes
    _inherit = 'purchase.order.line'

    @api.onchange('product_id')
    def _condicionar_product_id(self):
        res = {}
        if self.partner_id.filter_products:
            res['domain'] = {'product_id': [('planta', '=', True)]}
        else:
        	res['domain'] = {'product_id': [('planta', '=', False)]}
        	return res
        return res

