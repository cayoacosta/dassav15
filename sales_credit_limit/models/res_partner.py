# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError
from datetime import datetime


class ResPartner(models.Model):
    _inherit = 'res.partner'

    warning_stage = fields.Float(string='Monto Aviso',
                                 help="Mostrará un mensaje una vez el cliente haya alcanzado este monto."
                                      "Colocar el monto en 0.00 para deshabilitar esta función.")
    blocking_stage = fields.Float(string='Límite de Crédito',
                                  help="Se bloquearán las ventas a este cliente al llegar a este monto."
                                       "Colocar el monto en 0.00 para deshabilitar esta función.")
    due_amount = fields.Float(string="Total a Crédito", compute="compute_due_amount")
    active_limit = fields.Boolean("Habilitar Crédito", default=False)
    allow_limit_credit = fields.Boolean("Permitir Mas Credito", default=False)

    
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