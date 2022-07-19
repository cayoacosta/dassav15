# -*- coding: utf-8 -*-
# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class AccountInvoice(models.Model):
    _inherit = 'account.move'

    # Columns Section
    margin = fields.Float(
        'Margin', compute='_compute_margin', store=True,
        digits_compute=dp.get_precision('Product Price'),
        help="It gives profitability by calculating the difference between"
        " the Unit Price and the cost price.")

    margin_percent = fields.Float(
        'Margin (%)', compute='_compute_margin', store=True,
        digits_compute=dp.get_precision('PoS Order Margin Percent'))

    # Compute Section
    
    @api.depends('invoice_line_ids.margin', 'invoice_line_ids.price_subtotal')
    def _compute_margin(self):
        for invoice in self:
            tmp_margin = sum(invoice.mapped('invoice_line_ids.margin'))
            tmp_subtotal = sum(invoice.mapped('invoice_line_ids.price_subtotal'))
            invoice.update({
                'margin': tmp_margin,
                'margin_percent': tmp_margin / tmp_subtotal * 100 if
                tmp_subtotal else 0.0,
            })
