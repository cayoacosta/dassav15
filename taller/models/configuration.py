# -*- coding: utf-8 -*-

from odoo import models, fields


class TallerConfiguracion(models.Model):
    _name = 'taller.configuracion'
    _description = 'taller configuracion'
    
    
    pct_percent = fields.Float('PCT(%)')
    name = fields.Char("Nombre", required=1)

