# Copyright 2020, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class IncomesReport(models.Model):
    _name = 'tecnika.incomes.report'
    _description = 'This model creates an incomes report for daily operations'
    _order = 'operating_unit_id, operation_type, date desc'

    invoice_id = fields.Many2one('account.move', reandonly=True)
    payment_id = fields.Many2one('account.payment', readonly=True)
    move_id = fields.Many2one('account.move', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Partner', readonly=True)
    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit', readonly=True)
    journal_id = fields.Many2one('account.journal', string='Journal', readonly=True)
    cash_amount = fields.Float(srtring='Cash Amount', readonly=True)
    cash_tax_amount = fields.Float(srtring='Cash Tax Amount', readonly=True)
    credit_amount = fields.Float(string='Credit Amount', readonly=True)
    credit_tax_amount = fields.Float(string='Credit Tax Amount', readonly=True)
    date = fields.Date(readonly=True)
    operation_type = fields.Selection([
        ('out_invoice', 'Invoice'),
        ('out_refund', 'Credit Note'),
        ('cash_payment', 'Cash Payment'),
        ('credit_payment', 'Credit Payment'),
    ])


class IncomesReportByDocType(models.Model):
    _name = 'tecnika.incomes.reportbydoc'
    _description = 'This model creates an incomes report by document type for daily operations'
    _order = 'operating_unit_id, doctype, date desc'

    invoice_id = fields.Many2one('account.move', reandonly=True)
    payment_id = fields.Many2one('account.payment', readonly=True)
    move_id = fields.Many2one('account.move', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Partner', readonly=True)
    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit', readonly=True)
    journal_id = fields.Many2one('account.journal', string='Journal', readonly=True)
    amount_total = fields.Float(srtring='Amount', readonly=True)
    amount_tax = fields.Float(srtring='Tax Amount', readonly=True)
    date = fields.Date(readonly=True)
    operation_type = fields.Selection([
        ('out_invoice', 'Invoice'),
        ('out_refund', 'Credit Note'),
        ('cash_payment', 'Cash Payment'),
        ('credit_payment', 'Credit Payment'),
    ])
    doctype = fields.Char(string='Operational Document Type',
                          help='Indicate where this document is grouped')


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    categ_id = fields.Many2one('product.category', string='Categoria del producto', related='product_id.categ_id',
                               store=True)


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    journal_id = fields.Many2one(related='move_id.journal_id', store=True, index=True, copy=False)

