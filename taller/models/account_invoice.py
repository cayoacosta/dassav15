from odoo import models, fields, api


class AccountInvoiceLine(models.Model):
    _inherit = 'account.move.line'

    serie_id = fields.Many2one('stock.production.lot', string="No. Serie")
    tipo_de_venta = fields.Selection(
        [('refacciones', 'Refacciones'), ('maquinaria', 'Maquinaria'), ('taller', 'Taller'), ('gastos', 'Gastos')],
        string='Tipo de venta')

    @api.onchange('product_id')
    def _onchange_product_id(self):
        domain = super(AccountInvoiceLine, self)._onchange_product_id()
        if self.product_id.tipo_de_venta == 'maquinaria':
            self.tipo_de_venta = 'maquinaria'
        return domain


class AccountInvoice(models.Model):
    _inherit = 'account.move'

    tipo = fields.Selection(
        [('refacciones', 'Refacciones'), ('maquinaria', 'Maquinaria'), ('taller', 'Taller'), ('gastos', 'Gastos')],
        string='Tipo')

    default_credit_account_id = fields.Many2one('account.account',
                                                string='Cuenta de Taller',
                                                domain=[('deprecated', '=', False)],
                                                help="The income or expense account related to the selected product.")

    @api.onchange('default_credit_account_id')
    def _onchange_default_credit_account_id(self, group_id=False):
        if self.default_credit_account_id:
            for line in self.invoice_line_ids:
                line.update({'account_id': self.default_credit_account_id})

    # Load all unsold PO lines
    @api.onchange('purchase_id')
    def purchase_order_change(self):
        """
        Override to add diario from Purchase Order to Invoice.
        """

        if self.purchase_id and self.purchase_id.journal_id:
            res = super(AccountInvoice, self).purchase_order_change()
            # Assign Journal from PO to Invoice
            self.journal_id = self.purchase_id.journal_id.id
            self.tipo = self.purchase_id.tipo
            return res

    def action_move_create(self):
        res = super(AccountInvoice, self).action_move_create()
        for rec in self.invoice_line_ids:
            if rec.serie_id:
                move_lines = self.move_id.line_ids.filtered(
                    lambda x: x.product_id.id == rec.product_id.id and not x.serie_id and x.quantity == rec.quantity)
                if move_lines:
                    move_lines[0].write({'serie_id': rec.serie_id.id})
        return res
