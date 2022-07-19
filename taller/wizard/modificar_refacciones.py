# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons import decimal_precision as dp
from odoo.tools import float_compare

class ModificarRefacciones(models.TransientModel):
    _name = 'modificar.refacciones'
    _description = 'modificar refacciones'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    
    line_ids = fields.One2many("modificar.refacciones.wizard",'wizard_id', 'Modificar Refacciones')
    reparacion_id = fields.Many2one("ordenes.de.reparacion",'Orden de reparación')

    partner_id = fields.Many2one(related='reparacion_id.partner_id', string='Cliente', required=False)
    fecha = fields.Date("Fecha")
    currency_id = fields.Many2one("res.currency", string="Currency", readonly=True, default=lambda self: self.env.user.company_id.currency_id)
    refacciones_ids = fields.One2many('modificar.refacciones.wizard','reparacion_id', 'Refacciones', copy=True, auto_join=True)
    pricelist_id = fields.Many2one(related='reparacion_id.pricelist_id', string="Lista de precio",help="Pricelist for current order.", required=False)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env['res.company']._company_default_get('modificar.refacciones'))
    #margin = fields.Monetary(compute='_product_margin', currency_field='currency_id', digits=dp.get_precision('Product Price'), store=True)
    payment_term_id = fields.Many2one(related='reparacion_id.payment_term_id', string='Payment Terms', oldname='payment_term')
    partner_invoice_id = fields.Many2one('res.partner', string='Invoice Address', readonly=True, required=False, states={'draft': [('readonly', False)], 'sent': [('readonly', False)], 'sale': [('readonly', False)]}, help="Invoice address for current sales order.")
    partner_shipping_id = fields.Many2one('res.partner', string='Delivery Address', readonly=True, required=False, states={'draft': [('readonly', False)], 'sent': [('readonly', False)], 'sale': [('readonly', False)]}, help="Delivery address for current sales order.")
    fiscal_position_id = fields.Many2one('account.fiscal.position', oldname='fiscal_position', string='Fiscal Position')
    user_id = fields.Many2one('res.users', string='Salesperson', index=True, track_visibility='onchange', track_sequence=2, default=lambda self: self.env.user)


    
    def action_modify(self):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        refacciones_lines = self.line_ids.mapped('refacciones_line_id')
        deleted_lines = self.reparacion_id.refacciones_ids - refacciones_lines    
        for line in self.line_ids:
            if line.refacciones_line_id and float_compare(line.product_uom_qty, line.product_uom_qty_new, precision_digits=precision) == -1:
                
                line.refacciones_line_id.write({'product_uom_qty' : line.product_uom_qty_new})
                line.refacciones_line_id._action_launch_stock_rule()
                if line.product_uom_qty_new==0.0:
                    line.refacciones_line_id.unlink()
                    
            elif line.refacciones_line_id and float_compare(line.product_uom_qty, line.product_uom_qty_new, precision_digits=precision) == 1:
                product_qty = line.product_uom_qty - line.product_uom_qty_new
                line.refacciones_line_id.with_context(force_product_qty=product_qty)._create_or_update_picking()
                line.refacciones_line_id.write({'product_uom_qty' : line.product_uom_qty_new})
                if line.product_uom_qty_new==0.0:
                    line.refacciones_line_id.unlink()
            # Currently value is  updated        
            elif line.refacciones_line_id:
                line.write({'price_unit':line.price_unit})
                line.refacciones_line_id.write({'price_unit':line.price_unit})
            elif not line.refacciones_line_id:
                product = line.product_id
                refacciones_line = line.refacciones_line_id.new({
                    'product_id': product.id,
                    'name': line.name or product.name,
                    'reparacion_id': self.reparacion_id.id,
                    'product_uom_qty' : line.product_uom_qty_new,
                    'product_uom' : product.uom_id.id,
                    'purchase_price': product.standard_price,
                    'tax_id': [(6,0,line.tax_id.ids)],
                    'price_unit':line.price_unit
                    })
                #refacciones_line.product_id_change()
                vals = refacciones_line._convert_to_write({name: refacciones_line[name] for name in refacciones_line._cache})
                refacciones_line = line.refacciones_line_id.create(vals)
                refacciones_line._action_launch_stock_rule()
#         if len(self.reparacion_id.refacciones_ids) == len(refacciones_lines):
#             deleted_lines = self.reparacion_id.refacciones_ids
        if deleted_lines:
            for line in deleted_lines:
                line.with_context(force_product_qty=line.product_uom_qty)._create_or_update_picking()
                #line.write({'product_uom_qty' : line.product_uom_qty_new})
                
            #deleted_lines.write({'product_uom_qty' : 0})
            #deleted_lines._action_launch_stock_rule()
            deleted_lines.unlink() 
        body ="Refacciones <br/> Subtotal: -> %d" %self.reparacion_id.amount_untaxed_refacciones,  "<br/>" "Total: -> %d" %self.reparacion_id.amount_total_refacciones
        self.reparacion_id.message_post(body=body)
        return




class ModificarRefaccionesWizard(models.TransientModel):
    _name = 'modificar.refacciones.wizard'
    _description = 'modificar refacciones wizard'

    @api.depends('product_uom_qty', 'price_unit', 'tax_id')
    def _compute_amount(self):
        """
        Compute the amounts of line.
        """
        for line in self:
            price = line.price_unit
            taxes = line.tax_id.compute_all(price, line.wizard_id.currency_id, line.product_uom_qty, product=line.product_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })
    
    wizard_id = fields.Many2one("modificar.refacciones",'Wizard')
    reparacion_id = fields.Many2one("modificar.refacciones",'modificar refacciones')
    product_id = fields.Many2one("product.product",'Producto')
    name = fields.Text(string='Descripción')
    product_uom_qty = fields.Float(string='Cantidad', digits=dp.get_precision('Product Unit of Measure'), readonly=False)
    product_uom_qty_new = fields.Float(string='Nueva Cantidad', digits=dp.get_precision('Product Unit of Measure'), default=1.0)
    refacciones_line_id = fields.Many2one("refacciones.ordenes.de.reparacion",'Líneas de refacción')
    price_unit = fields.Float('Precio unitario', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    tax_id = fields.Many2many('account.tax', string='Impuestos', domain=['|', ('active', '=', False), ('active', '=', True)])
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure')
    event_ticket_id = fields.Many2one('event.event.ticket', string='Event Ticket', help="Choose "
        "an event ticket and it will automatically create a registration for this event ticket.")
    company_id = fields.Many2one(related='wizard_id.company_id', string='Company', store=True, readonly=True)


    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', readonly=True, store=True)
    price_tax = fields.Float(compute='_compute_amount', string='Total Tax', readonly=True, store=True)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', readonly=True, store=True)
    currency_id = fields.Many2one(related='wizard_id.currency_id', depends=['wizard_id'], store=True, string='Currency', readonly=True)
    move_ids = fields.One2many('stock.move', 'refacciones_line_id', string='Stock Moves')
    in_move_ids = fields.One2many('stock.move', 'in_refacciones_line_id', string='Incoming Stock Moves')
    route_id = fields.Many2one('stock.location.route', string='Route', domain=[('sale_selectable', '=', True)], ondelete='restrict')
    date_order = fields.Date(related='wizard_id.fecha', string='Order Date', readonly=True)
    move_dest_ids = fields.One2many('stock.move', 'created_ordernes_de_line_id', 'Downstream Moves')
    margin = fields.Float(compute='_product_margin', digits=dp.get_precision('Product Price'), store=True)
    purchase_price = fields.Float(related='refacciones_line_id.purchase_price', string='Cost', digits=dp.get_precision('Product Price'))


    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        if not self.event_ticket_id:
            super(ModificarRefaccionesWizard, self).product_uom_change()


    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        if not self.product_uom or not self.product_id:
            self.price_unit = 0.0
            return
        if self.wizard_id.pricelist_id and self.wizard_id.partner_id:
            product = self.product_id.with_context(
                lang=self.wizard_id.partner_id.lang,
                partner=self.wizard_id.partner_id,
                quantity=self.product_uom_qty,
                pricelist=self.wizard_id.pricelist_id.id,
                uom=self.product_uom.id,
                fiscal_position=self.env.context.get('fiscal_position')
            )
            self.price_unit = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)

    
    
    def _get_display_price(self, product):
        pricelist = self.wizard_id.pricelist_id
        if pricelist.discount_policy == 'with_discount':
            return product.with_context(pricelist=pricelist.id).price
        product_context = dict(self.env.context, partner_id=self.wizard_id.partner_id.id, date=self.wizard_id.fecha, uom=self.product_uom.id)

        final_price, rule_id = pricelist.with_context(product_context).get_product_price_rule(self.product_id, self.product_uom_qty or 1.0, self.wizard_id.partner_id)
        base_price, currency = self.with_context(product_context)._get_real_price_currency(product, rule_id, self.product_uom_qty, self.product_uom, pricelist.id)
        if currency != pricelist.currency_id:
            base_price = currency._convert(
                base_price, pricelist.currency_id,
                self.wizard_id.company_id, self.wizard_id.fecha or fields.Date.today())
        # negative discounts (= surcharge) are included in the display price
        return max(base_price, final_price)


    @api.depends('product_id', 'purchase_price', 'product_uom_qty', 'price_unit', 'price_subtotal')
    def _product_margin(self):
        for line in self:
            currency = line.wizard_id.pricelist_id.currency_id
            price = line.purchase_price
            line.margin = currency.round(line.price_subtotal - (price * line.product_uom_qty))
    
   
    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return {'domain': {'product_uom': []}}

        vals = {}
        domain = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
        if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
            vals['product_uom'] = self.product_id.uom_id
            vals['product_uom_qty'] = self.product_uom_qty or 1.0
        
        pricelist = self.wizard_id.pricelist_id
        product = self.product_id.with_context(
            lang=self.wizard_id.partner_id.lang,
            partner=self.wizard_id.partner_id,
            quantity=vals.get('product_uom_qty') or self.product_uom_qty,
            date=self.wizard_id.fecha,
            pricelist = pricelist.id,
            uom=self.product_uom.id
        )

        result = {'domain': domain}

        name = product.get_product_multiline_description_sale() 

        vals.update(name=name)

        fpos = self.wizard_id.partner_id.property_account_position_id
        # If company_id is set, always filter taxes by the company
        taxes = self.product_id.taxes_id.filtered(lambda r: not self.company_id or r.company_id == self.company_id)
        self.tax_id = fpos.map_tax(taxes, self.product_id, self.wizard_id.partner_id) if fpos else taxes
            
        if self.wizard_id.pricelist_id and self.wizard_id.partner_id:
            vals['price_unit'] = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)
        self.update(vals)
        return result


    def _compute_margin(self, wizard_id, product_id, product_uom_id):
        frm_cur = self.env.user.company_id.currency_id
        to_cur = wizard_id.pricelist_id.currency_id
        purchase_price = product_id.standard_price
        if product_uom_id != product_id.uom_id:
            purchase_price = product_id.uom_id._compute_price(purchase_price, product_uom_id)
        price = frm_cur._convert(
            purchase_price, to_cur, wizard_id.company_id or self.env.user.company_id,
            wizard_id.fecha or fields.Date.today(), round=False)
        return price


    @api.onchange('product_id', 'product_uom')
    def product_id_change_margin(self):
        if not self.wizard_id.pricelist_id or not self.product_id or not self.product_uom:
            return
        self.purchase_price = self._compute_margin(self.wizard_id, self.product_id, self.product_uom)