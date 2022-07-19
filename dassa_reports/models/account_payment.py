# -*- coding: utf-8 -*-
from odoo import api, fields, models, _



class AccountPayment(models.Model):
    _inherit = "account.payment"
    
    amount_total_words = fields.Char("amount")
   
    @api.model
    def convert_amount_to_word(self, payment, amount):
        return payment.currency_id.amount_to_text(amount)
    