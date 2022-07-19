# -*- coding: utf-8 -*-

"""from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError


class AccountInvoiceRefund(models.TransientModel):
    #Credit Notes

    _inherit = "account.invoice.refund"
    _description = "Credit Note"

    @api.model
    def _get_default_tipo(self):
        ctx = self._context
        if ctx.get('active_model') == 'account.invoice':
            return self.env['account.invoice'].browse(ctx.get('active_ids')[0]).tipo

    @api.model
    def _get_default_journal(self):
        ctx = self._context
        if ctx.get('active_model') == 'account.invoice':
            return self.env['account.invoice'].browse(ctx.get('active_ids')[0]).journal_id.id

    @api.model
    def _get_default_account_id(self):
        ctx = self._context
        if ctx.get('active_model') == 'account.invoice':
            return self.env['account.invoice'].browse(ctx.get('active_ids')[0]).account_id_aux_refund.id



    invoice_id = fields.Many2one('account.invoice', string='Invoice Reference',
        ondelete='cascade', index=True)

    journal_id = fields.Many2one('account.journal', string='Journal',
        required=True, readonly=True, default=_get_default_journal)

    nota_dev = fields.Selection([('facturacion','Facturación'),('devolucion','Devolución'),('bonificacion','Bonificación')],
                            string='Tipo Documento', required=True)

    account_id = fields.Many2one('account.account', string='Account', domain=[('deprecated', '=', False)],
        help="The income or expense account related to the selected product.", required=True, default=_get_default_account_id)

    tipo = fields.Selection([('refacciones','Refacciones'),('maquinaria','Maquinaria'),('taller','Taller'),('gastos','Gastos')],
                            string='Tipo', default=_get_default_tipo, readonly=True)


    def _get_refund(self, inv, mode):
        refund = super(AccountInvoiceRefund, self)._get_refund(inv, mode)
        refund.nota_dev = self.nota_dev
        refund.tipo = self.tipo
        if self.account_id:
            for line in refund.invoice_line_ids:
                line.update({'account_id': self.account_id})
        return refund"""