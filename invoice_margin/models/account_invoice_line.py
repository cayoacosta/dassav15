# -*- coding: utf-8 -*-
# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class AccountInvoiceLine(models.Model):
    _inherit = 'account.move.line'

    # Columns Section
    margin = fields.Float(
        'Margin', compute='_compute_multi_margin', store=True,
        digits_compute=dp.get_precision('Product Price'))

    margin_percent = fields.Float(
        'Margin (%)', compute='_compute_multi_margin', store=True,
        readonly=False,
        digits_compute=dp.get_precision('Product Price'))

    purchase_price = fields.Float(
        string='Cost Price', copy=False,
        digits_compute=dp.get_precision('Product Price'))

    # Onchange Section

    def product_id_change(
            self, product, uom_id, qty=0, name='', type='out_invoice',
            partner_id=False, fposition_id=False, price_unit=False,
            currency_id=False, company_id=None):
        product_obj = self.env['product.product']
        res = super(AccountInvoiceLine, self).product_id_change(
            product, uom_id, qty=qty, name=name, type=type,
            partner_id=partner_id, fposition_id=fposition_id,
            price_unit=price_unit, currency_id=currency_id,
            company_id=company_id)
        if product:
            prod = product_obj.browse(product)
            res['value']['purchase_price'] = prod.standard_price
        return res

    # Compute Section

    @api.depends('purchase_price', 'price_subtotal')
    def _compute_multi_margin(self):
        for line in self:
            if line.move_id and line.move_id.move_type[:2] == "in":
                line.update(
                    {"margin": 0.0, "margin_percent": 0.0}
                )
                continue
            tmp_margin = line.price_subtotal - (line.purchase_price * line.quantity)
            line.update(
                {
                    "margin": tmp_margin,
                    "margin_percent": (
                        tmp_margin / line.price_subtotal * 100.0
                        if line.price_subtotal
                        else 0.0
                    ),
                }
            )

    # Overload Section. Necessary for lines created by other way than UI
    # Could be remove in the version of Odoo that removed product_id_change
    # function
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('purchase_price', False):
                product_obj = self.env['product.product']
                product = product_obj.browse(vals.get('product_id'))
                vals['purchase_price'] = product.standard_price
        return super(AccountInvoiceLine, self).create(vals_list)

    @api.onchange('margin_percent')
    def _onchange_markup_per(self):
        for record in self:
            if record.margin_percent:
                if record.purchase_price:
                    if record.product_id.taxes_id.amount:
                        if -9999.99 < record.margin_percent < 9999.99:
                            record.price_unit = round((record.purchase_price / (1 - (record.margin_percent / 100.00))) *
                                                      (1 + (record.product_id.taxes_id.amount / 100.00)), 0)
                            record.margin = record.price_subtotal - (record.purchase_price * record.quantity)
