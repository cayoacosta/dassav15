# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from lxml import etree

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    ordenes_id = fields.Many2one('ordenes.de.reparacion','Ordenes de reparacion')
    journal_id = fields.Many2one('account.journal','Diario')
    tipo = fields.Selection([('refacciones','Refacciones'),('maquinaria','Maquinaria'),('taller','Taller'),('gastos','Gastos')],
                            string='Tipo',default='refacciones')
    journal_id = fields.Many2one('account.journal','Diario')

    @api.onchange('tipo', 'operating_unit_id')
    def onchange_tipo(self):
        if self.tipo:
            journal = self.env['account.journal'].search([('type','=','purchase'),('tipo','=',self.tipo),('operating_unit_id','=',self.operating_unit_id.id)],limit=1)
            if journal:
                self.journal_id = journal.id

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            seq_code = 'purchase.order'
            if vals.get('tipo','')=='refacciones':
                seq_code = 'purchase.order.refacciones'
            elif vals.get('tipo','')=='maquinaria':
                seq_code = 'purchase.order.maquinaria'
            elif vals.get('tipo','') =='gastos':
                seq_code = 'purchase.order.gastos'
            elif vals.get('tipo','')=='taller':
                seq_code = 'purchase.order.taller'
                
            if 'company_id' in vals:
                vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code(seq_code) or _('New')
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code(seq_code) or _('New')
        result = super(PurchaseOrder, self).create(vals)
        return result

    
    def _prepare_invoice(self):
        invoice_vals = super(PurchaseOrder, self)._prepare_invoice()
        if self.journal_id: 
            invoice_vals['journal_id'] = self.journal_id.id
        return invoice_vals

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(PurchaseOrder, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            tipo = self._context.get('default_tipo','')
            if not tipo:
                tipo = 'refacciones' 
            
            doc = etree.XML(res['fields']['order_line']['views']['tree']['arch'])
            for node in doc.xpath("//field[@name='product_id']"):
                node.set('domain', "[('tipo_de_venta', '=', '%s')]"%(tipo))
            res['fields']['order_line']['views']['tree']['arch'] = etree.tostring(doc)
            
            doc = etree.XML(res['fields']['order_line']['views']['form']['arch'])
            for node in doc.xpath("//field[@name='product_id']"):
                node.set('domain', "[('tipo_de_venta', '=', '%s')]"%(tipo))
            res['fields']['order_line']['views']['form']['arch'] = etree.tostring(doc)
            
        return res



class PurchaseOrderLine(models.Model):
    # Private attributes
    _inherit = 'purchase.order.line'


    @api.onchange('product_id')
    def _condicionar_product_id(self):
        if self.order_id.tipo == 'refacciones':
            res = {}
            if self.partner_id.filter_products:
                res['domain'] = {'product_id': [('planta', '=', True), ('tipo_de_venta', '=', 'refacciones')]}
            else:
                res['domain'] = {'product_id': [('planta', '=', False),('tipo_de_venta', '=', 'refacciones')]}
                return res
            return res
