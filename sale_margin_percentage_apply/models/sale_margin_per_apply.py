# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo import tools
import math


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.onchange('margin_delivered_percent')
    def _onchange_markup_per(self):
        for record in self:
            if record.margin_delivered_percent:
                if record.purchase_price:
                    #if record.product_id.taxes_id.amount:
                        if record.margin_delivered_percent > -9999.99 and record.margin_delivered_percent < 9999.99:
                            record.price_unit = round((record.purchase_price / (1 - (record.margin_delivered_percent / 100.00)))*
                            (1+(record.product_id.taxes_id.amount/100.00)),0)
                            record.margin_delivered = record.price_subtotal - (record.purchase_price*record.product_uom_qty)
                        

