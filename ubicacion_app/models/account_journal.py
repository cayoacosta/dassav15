"""from odoo import models, fields, api

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    account_id_aux_refund = fields.Many2one('account.account', 
    	string='Cuenta de Devolución',
    	domain=[('deprecated', '=', False)],
    	help="Establecer cuenta contable para aplicación de notas de crédito.")"""