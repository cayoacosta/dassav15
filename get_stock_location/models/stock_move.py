# -*- coding: utf-8 -*-

from ast import Store
from odoo import models, fields, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    physical_location = fields.Char(compute="_get_physical_location",
                                    string="Physical Location",
                                    help="Indicates where is physically located this product in format <MUEBLE>:<FILA>:<COLUMNA>")

    @api.depends('physical_location', 'product_id', 'location_id')
    def _get_physical_location(self):
        check_model = self.env.get('x_ubicaciones', None)
        if check_model:
            x_ubicacion = self.env['x_ubicaciones']
            for move in self:
                domain = [('x_producto', '=', move.product_id.id),
                          ('x_studio_ubicacion', '=', move.location_id.id)
                          ]
                physical_location = ''
                x_location = x_ubicacion.search(domain)
                if x_location:
                    x_loc = x_location[0]
                    x_mueble = x_loc['x_studio_mueble'] or ''
                    x_fila = x_loc['x_studio_fila'] or ''
                    x_col = x_loc['x_studio_columna'] or ''
                    physical_location = "{}:{}:{}".format(x_mueble, x_fila, x_col)

                move.physical_location = physical_location
            return
        else:
            self.physical_location = None
