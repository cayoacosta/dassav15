# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'


    ubicaciones_ids = fields.One2many('ubicacion','product_id', 'Ubicaciones', 
        copy=True, 
        auto_join=True)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    ubicaciones_ids = fields.One2many('ubicacion','product_id', 'Ubicaciones', 
        copy=True, 
        auto_join=True)

