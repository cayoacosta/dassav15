# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError
from datetime import datetime


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    has_due = fields.Boolean()
    is_warning = fields.Boolean()
    is_defaulter = fields.Boolean()
    partner_has_credit = fields.Boolean(related='partner_id.active_limit')
    due_amount = fields.Float(related='partner_id.due_amount')
    credit_limit = fields.Float(related='partner_id.blocking_stage')
    payment_term_id = fields.Many2one('account.payment.term', required=False, string='Payment Terms', oldname='payment_term')


    @api.onchange('partner_id')
    def update_payment_term_id(self):
        #for rec in self:
        if self.partner_has_credit:
            return {'domain': {'payment_term_id': [(1, '=', 1)]}}
        else:
            return {'domain': {'payment_term_id': [('is_immediate', '=', True)]}}


    @api.onchange('pricelist_id')
    def _condicionar_pricelist_id(self):
        domain = {}

        if self.pricelist_id.conta_credit:
            domain = {'payment_term_id':[('is_immediate','=',True)]}
            return {'domain' : domain}
        else:
            domain = {'payment_term_id':[('is_immediate','=',False)]}
            return {'domain' : domain}

    # 
    # def check_overdue(self):
    #     self.ensure_one()
    #     today = datetime.now().date()
    #     # inv_ids = self.search(['&', '&', '&', ('partner_id', '=', self.partner_id), ('state', '=', 'open'),
    #     #                        ('type', '=', 'out_invoice'), ('date_due', '<', today)])
    #     inv_ids = self.env['account.invoice'].search([('partner_id', '=', self.partner_id.id), ('state', '=', 'open'),
    #                             ('type', '=', 'out_invoice'), ('date_due', '<', today)])
    #     if inv_ids:
    #         if self.env.user.has_group('sales_team.group_sale_manager'):
    #             raise Warning(
    #                 "El Cliente tiene facturas Vencidas. ¿Desea continuar?")
    #         else:
    #             raise UserError(
    #                 "No se puede confirmar el pedido. El cliente tiene facturas venciadas.")

    
    def _action_confirm(self):
        """To check the selected customers due amount is exceed than blocking stage"""
        if self.partner_id.allow_limit_credit:
            self.partner_id.allow_limit_credit = False
            return super(SaleOrder, self)._action_confirm()

        if not self.payment_term_id.is_immediate:
            if self.partner_id.active_limit:
                if self.env.user.has_group('sales_credit_limit.group_ignore_credit_limit'):
                    return super(SaleOrder, self)._action_confirm()
                else:
                    if self.is_defaulter:
                        raise UserError(_("Este cliente Tiene Facturas Vencidas."))
                    new_credit = self.due_amount + self.amount_total  #considera el monto del pedido actual para ver no sobrepase su crédito.
                    if new_credit >= self.partner_id.blocking_stage:
                        if self.partner_id.blocking_stage != 0:
                            raise UserError(_("Este cliente ha alcanzado su límite de Crédito."))
            else:
                raise UserError(_("Este cliente no cuenta con crédito autorizado."))
        return super(SaleOrder, self)._action_confirm()

    @api.onchange('partner_id')
    def check_due(self):
        """To show the due amount and warning stage"""
        if self.partner_id and self.partner_id.due_amount > 0:
            self.has_due = True
        else:
            self.has_due = False
        if self.partner_id and self.partner_id.active_limit:
            if self.due_amount >= self.partner_id.warning_stage:
                if self.partner_id.warning_stage != 0:
                    self.is_warning = True
        else:
            self.is_warning = False
        today = datetime.now().date()
        inv_ids = self.env['account.move'].search([('partner_id', '=', self.partner_id.id), ('state', '=', 'open'),
                                                      ('move_type', '=', 'out_invoice'), ('invoice_date_due', '<', today)])
        if inv_ids:
            self.is_defaulter = True


