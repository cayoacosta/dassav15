# -*- coding: utf-8 -*-

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = ['product.template']

    active = fields.Boolean(track_visibility='onchange')
