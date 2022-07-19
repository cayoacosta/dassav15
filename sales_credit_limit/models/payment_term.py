# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError
from datetime import datetime


class PaymentTerm(models.Model):
    _inherit = 'account.payment.term'

    is_cash = fields.Boolean(string= "Es Contado", default=False, required = True)
    is_immediate = fields.Boolean("Es Inmediato", default=False)


    
    def compute_due_amount(self):
        for rec in self:
            if not rec.id:
                continue
            debit_amount = rec.debit
            credit_amount = rec.credit
            rec.due_amount = credit_amount - debit_amount
            

    @api.constrains('warning_stage', 'blocking_stage')
    def constrains_warning_stage(self):
        if self.active_limit:
            if self.warning_stage >= self.blocking_stage:
                if self.blocking_stage > 0:
                    raise UserError(_("El monto del Aviso debe ser menos al Límite de Crédito"))
