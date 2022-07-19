"""# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from lxml import etree

class SaleOrder(models.Model):
    _inherit = 'sale.order'


    account_id_aux_refund = fields.Many2one(related='diario.account_id_aux_refund')

    @api.multi
    def _prepare_invoice(self):
    	self.ensure_one()
    	invoice_vals = super(SaleOrder, self)._prepare_invoice()
    	invoice_vals['tipo'] = self.tipo
    	invoice_vals['account_id_aux_refund'] = self.account_id_aux_refund.id
    	return invoice_vals"""
