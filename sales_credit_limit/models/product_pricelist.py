# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from lxml import etree

class StockPickingType(models.Model):
    _inherit = 'product.pricelist'
    
    conta_credit = fields.Boolean(string="Es contado", default=False)