# -*- coding: utf-8 -*-

from ast import Store
from odoo import models, fields, api

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    cash_payment = fields.Float(compute="_calculate_payment", store=True,
        string="Cash Amount",
        help="Cash Invoices Paid Amount")
    credit_payment = fields.Float(compute="_calculate_payment", store=True,
        string="Credit Amount",
        help="Credit Invoices Paid Amount")
    cash_tax_paid = fields.Float(compute="_calculate_payment", store=True,
        string="Cash Tax Amount",
        help="Taxes for Cash Invoices")
    credit_tax_paid = fields.Float(compute="_calculate_payment", store=True,
        string="Credit Tax Amount",
        help="Taxes for Credit Invoices" 
        )

    # @api.depends('reconciled_invoice_ids')
    # def _calculate_payment(self):
    #
    #     for pay in self:
    #         rinvids = pay.reconciled_invoice_ids
    #         cash_amt = 0.00
    #         cash_tax = 0.00
    #         credit_amt = 0.00
    #         credit_tax = 0.00
    #         for inv in rinvids:
    #             cash_payment = inv.invoice_payment_term_id.is_immediate or False
    #             paid_amt = pay._get_invoice_payment_amount(inv)
    #             taxes_paid = self._get_payment_taxes(inv, paid_amt)
    #
    #             if cash_payment:
    #                 cash_amt += paid_amt
    #                 cash_tax += taxes_paid
    #             else:
    #                 credit_amt += paid_amt
    #                 credit_tax += taxes_paid
    #
    #         pay.cash_payment = cash_amt
    #         pay.cash_tax_paid = cash_tax
    #         pay.credit_payment = credit_amt
    #         pay.credit_tax_paid = credit_tax
    #
    #     return

    def _get_payment_taxes(self, inv, paid_amt):
        sql = """
            select sum(ait2.amount * (ait2.base / ai.amount_untaxed)) taxes
            from account_invoice ai 
	                join account_invoice_tax ait2 on (ait2.invoice_id  = ai.id)
            where ai.id = %s and ai.amount_untaxed > 0;
        """ % inv.id
        self.env.cr.execute(sql)
        paid_taxes = self.env.cr.dictfetchall()
        percent_paid = paid_amt / inv.amount_total
        taxes_paid = 0
        for pt in paid_taxes:
            if pt['taxes']:
                taxes_paid += pt['taxes'] * percent_paid

        return taxes_paid