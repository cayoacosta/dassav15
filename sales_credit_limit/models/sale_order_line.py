# -*- coding: utf-8 -*-

"""from odoo import models, fields,api,_
from odoo.addons import decimal_precision as dp
from odoo.tools import float_compare
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    markup = fields.Float(compute='_compute_markup', digits=dp.get_precision('.2f%'), store=False, readonly=True)
    markup_per = fields.Float(compute='_compute_markup_per', digits=dp.get_precision('.2f%'), store=False, readonly=False)
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', readonly=True, store=True)
    price_unit = fields.Float('Unit Price', required=True, digits=dp.get_precision('Product Price'), default=0.0)



    @api.depends('price_unit', 'purchase_price')
    def _compute_markup(self):
        for record in self:
            if record.price_unit and record.purchase_price:
                record.markup = record.price_unit - record.purchase_price

    @api.depends('price_unit', 'purchase_price')
    def _compute_markup_per(self):
        for record in self:
            if record.purchase_price > 0:
                record.markup_per = 100.0 * (record.price_unit - record.purchase_price) / record.purchase_price

    @api.onchange('markup_per')
    def _onchange_markup_per(self):
            if self.markup_per:
                if self.markup_per > -9999.99 and self.markup_per < 9999.99:
                    self.price_unit = self.purchase_price * (1 + self.markup_per / 100.0)