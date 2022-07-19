# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo import tools
import math


class ModificarRefaccionesWizard(models.TransientModel):
    _inherit = "modificar.refacciones.wizard"

    margin_delivered = fields.Float(
        string='Margin Delivered',
        compute='_compute_margin_delivered',
        store=True,
    )
    margin_delivered_percent = fields.Float(
        string='Margen %',
        compute='_compute_margin_delivered',
        store=True,
        readonly=False,
        oldname='margin_delivered_percent',
    )
    purchase_price_delivery = fields.Float(
        string='Purchase Price Delivered',
        compute='_compute_margin_delivered',
        store=True,
    )


    @api.depends('margin', 'qty_delivered', 'product_uom_qty',
                 'move_ids.price_unit')
    def _compute_margin_delivered(self):
        digits = self.env['decimal.precision'].precision_get('Product Price')
        for line in self.filtered('price_reduce'):
            if not line.qty_delivered and not line.product_uom_qty:
                continue
            qty = line.qty_delivered or line.product_uom_qty
            line.purchase_price_delivery = line.purchase_price
            line.margin_delivered = line.margin
            if line.qty_delivered:
                cost_price = 0.0
                moves = line.move_ids.filtered(
                    lambda x: (
                        x.state == 'done' and (
                            x.picking_code == 'outgoing' or (
                                x.picking_code == 'incoming' and x.to_refund))
                    ))
                for move in moves:
                    cost_price += move.product_qty * move.price_unit
                average_price = (abs(cost_price) /
                                 line.qty_delivered) or line.purchase_price
                line.purchase_price_delivery = tools.float_round(
                    average_price, precision_digits=digits)
                line.margin_delivered = line.qty_delivered * (
                    line.price_reduce - line.purchase_price_delivery
                )
            # compute percent margin based on delivered quantities or ordered
            # quantities
            line.margin_delivered_percent = qty and (
                (line.price_reduce_taxexcl - line.purchase_price_delivery) /
                line.price_reduce_taxexcl * 100.0) or 0.0
            #compute price unit margen based on margin_delivered_percent


    @api.onchange('margin_delivered_percent')
    def _onchange_markup_per(self):
        for record in self:
            if record.margin_delivered_percent:
                if record.purchase_price:
                    if record.product_id.taxes_id.amount:
                        if record.margin_delivered_percent > -9999.99 and record.margin_delivered_percent < 9999.99:
                            record.price_unit = round((record.purchase_price / (1 - (record.margin_delivered_percent / 100.00)))*
                            (1+(record.product_id.taxes_id.amount/100.00)),0)
                            record.margin_delivered =  record.price_subtotal - (record.purchase_price*record.product_uom_qty)
