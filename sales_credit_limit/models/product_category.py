# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError
from datetime import datetime


class ProductCategory(models.Model):
    _inherit = 'product.category'

    porc_cat = fields.Float(string="Porcentaje %")
