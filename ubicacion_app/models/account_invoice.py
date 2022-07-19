# -*- coding: utf-8 -*-

"""from collections import OrderedDict
import json
import re
import uuid
from functools import partial

# -*- coding: utf-8 -*-
from odoo import api, exceptions, fields, models, _



class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    nota_dev = fields.Selection([('facturacion','Facturación'),('devolucion','Devolución'),('bonificacion','Bonificación')],
                            string='Tipo Documento', default='facturacion')

    account_id_aux_refund = fields.Many2one('account.account',
        string='Cuenta de Devolución',
        domain=[('deprecated', '=', False)],
        help="The income or expense account related to the selected product.")


    @api.onchange('account_id_aux_refund')
    def _onchange_account_id_aux_refund(self, group_id=False):
    	if self.account_id_aux_refund:
    		for line in self.invoice_line_ids:
    			line.update({'account_id': self.account_id_aux_refund})"""
