# -*- coding: utf-8 -*-

from odoo import models, api, fields,_
from odoo.addons import decimal_precision as dp

class ManoDeObraWizard(models.TransientModel):
    _name = 'mano.de.obra.wizard'
    _description = 'mano de obra wizard'
    
    line_ids = fields.One2many("mano.de.obra.wizard.line",'wizard_id', 'Mano de obra')
    reparacion_id = fields.Many2one("ordenes.de.reparacion",'Orden de reparación')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env['res.company']._company_default_get('ordenes.de.reparacion'))
    
    
    def action_modify(self):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        reparacion = self.reparacion_id
        mano_de_obras = reparacion.mano_de_obra_ids
        mano_de_obra_exist = self.line_ids.mapped('mano_de_obra_line_id')
        mano_de_obra_remove = mano_de_obras - mano_de_obra_exist
        for line in self.line_ids:
            if line.mano_de_obra_line_id and line.product_uom_qty==0.0:
                line.mano_de_obra_line_id.unlink()
                continue 
            vals = {'product_id': line.product_id.id,'name':line.name, 
             'mecanico_id': line.mecanico_id.id, 'detalle': line.detalle,
             'product_uom_qty' : line.product_uom_qty, 'price_unit': line.price_unit, 
             'tax_id': [(6,0,line.tax_id.ids)],
            # 'reparacion_id' : self.reparacion_id.id,
             'comision': line.comision,
             'monto': line.monto,
             'product_uom' : line.product_id.uom_id.id,
            }

            if line.mano_de_obra_line_id:
                line.mano_de_obra_line_id.write(vals)
            else:
                vals.update({'reparacion_id': reparacion.id,})
                line.mano_de_obra_line_id.create(vals)
#         if len(mano_de_obras) == len(mano_de_obra_exist):
#             mano_de_obra_remove = mano_de_obras
        if mano_de_obra_remove:
            mano_de_obra_remove.unlink()
        body ="Mano de obra <br/> Subtotal: -> %d" %self.reparacion_id.amount_untaxed_mano,  "<br/>" "Total: -> %d" %self.reparacion_id.amount_total_mano
        self.reparacion_id.message_post(body=body)
        return
    
class ManoDeObraWizardLine(models.TransientModel):
    _name = 'mano.de.obra.wizard.line'
    _description = 'mano de obra wizard line'
    
    wizard_id = fields.Many2one("mano.de.obra.wizard",'Wizard')
    
    product_id = fields.Many2one("product.product",'Producto',domain=[('mano_de_obra','=',True)])
    name = fields.Text(string='Descripción', required=True)
    mecanico_id = fields.Many2one("res.partner",'Mecánico',domain=[('mecanico','=',True)], required=True)
    product_uom_qty = fields.Float(string='Cantidad', digits=dp.get_precision('Product Unit of Measure'), required=True, default=1.0)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure')
    price_unit = fields.Float('Precio unitario', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    tax_id = fields.Many2many('account.tax', string='Impuestos', domain=['|', ('active', '=', False), ('active', '=', True)])
    mano_de_obra_line_id = fields.Many2one("mano.deobra.ordenes.de.reparacion",'Mano de obra Line')
    detalle = fields.Char(string='Detalles')
    comision = fields.Float(string="Comisión %", computed="_recio_unitario_monto", help="Ingrese el Porcentaje de la comsion")
    monto = fields.Float(string="Monto $",computed="_recio_unitario_comision", readonly=False, help="El monto es el cálculo de la comsión")

    
    @api.onchange('price_unit', 'product_uom_qty', 'comision')
    def _recio_unitario_comision(self):
        if self.comision:
            #self.monto = (self.comision / 100) * ((self.price_unit / 1.16) * self.product_uom_qty)
            self.monto = (self.comision / 100) * (self.price_unit / (1+(self.product_id.taxes_id.amount/100)) * self.product_uom_qty)

    @api.onchange('monto')
    def _recio_unitario_monto(self):
        if self.monto and self.price_unit:
            #self.comision = (self.monto / ((self.price_unit / 1.16) * self.product_uom_qty))*(100)
            self.comision = (self.monto / ((self.price_unit / (1+(self.product_id.taxes_id.amount/100))) * self.product_uom_qty))*(100)

    @api.onchange('mecanico_id')
    def get_comision_par_user(self):
        if self.mecanico_id:
                vals={'comision':self.mecanico_id.comision}
                self.update(vals)

    
    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return
        vals = {}
        name = self.product_id.get_product_multiline_description_sale() 
        vals.update(name=name)
        
        fpos = self.mecanico_id.property_account_position_id
        # If company_id is set, always filter taxes by the company
        taxes = self.product_id.taxes_id.filtered(lambda r: not self.wizard_id.company_id or r.company_id == self.wizard_id.company_id)
        self.tax_id = fpos.map_tax(taxes, self.product_id, self.wizard_id.reparacion_id.partner_id) if fpos else taxes
        
        self.update(vals)
