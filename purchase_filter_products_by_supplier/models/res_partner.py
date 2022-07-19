# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'
            
    filter_products = fields.Boolean("Filtrar Productos")