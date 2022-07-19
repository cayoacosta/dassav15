# -*- coding: utf-8 -*-

from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    user_id = fields.Many2one(string='Comercial', relation='res.user', related='move_id.user_id', store=True)
    team_id = fields.Many2one(string='Equipo de ventas', related='move_id.team_id', store=True)
