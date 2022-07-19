# -*- coding: utf-8 -*-

from odoo import models, fields
from odoo.exceptions import ValidationError, AccessError, UserError, RedirectWarning, Warning
import logging

_logger = logging.getLogger(__name__)
from datetime import date
from datetime import datetime
import pytz


# --CRITERIOS DE SELECCION
class report_comun_data_product_selection(models.TransientModel):
    _name = 'report.comun_data_product_selection'
    _description = 'Criterio de seleccion de productos para los reportes'

    category_ids = fields.Many2many(
        'product.category',
        string="Categoria"
    )
    mueble = fields.Char(
        string="Mueble"
    )
    fila = fields.Char(
        string="Fila"
    )
    columna = fields.Char(
        string="Columna"
    )


class report_comun_data_almacen_selection(models.TransientModel):
    _name = 'report.comun_data_almacen_selection'
    _description = 'Criterio de seleccion de almacenes para los reportes'

    warehouse_ok = fields.Boolean(
        string="Línea"
    )
    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string="Almacén"
    )
    all_warehouses_ok = fields.Boolean(
        string="Todas"
    )
    select_warehouses_ok = fields.Boolean(
        string="Seleccionar"
    )
    warehouse_ids = fields.Many2many(
        'stock.warehouse',
        string="Almacenes",
    )


# --REPORTES DE SELECCION
class report_existencia_ubicacion(models.TransientModel):
    _name = 'report.existencia_ubicacion'
    _description = 'Wizard de impresión para reporte de existencia modalida por ubicación'
    _inherit = 'report.comun_data_product_selection'

    date = fields.Datetime(
        string="Fecha",
        required=True
    )
    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string="Almacén",
        required=True
    )
    desc = fields.Text(
        string="Descripción"
    )
    inc_solo_prod_saldo = fields.Boolean(
        string="Incluir Productos solo con saldo",
        default=False
    )
    lines = fields.One2many(
        'report.existencia_ubicacion_lines',
        'report_existencia_ubicacion',
        string="Lineas"
    )

    def check_blanks(self):
        mueble = str(self.mueble)
        res = " " in mueble
        if res == True:
            raise ValidationError("No se admiten espacion en blanco en el campo mueble")
        fila = str(self.fila)
        res = " " in fila
        if res == True:
            raise ValidationError("No se admiten espacion en blanco en el campo fila")
        columna = str(self.columna)
        res = " " in columna
        if res == True:
            raise ValidationError("No se admiten espacion en blanco en el campo columna")

    def print_report(self):
        self.ensure_one()

        for rec in self:
            rec.lines.unlink()
            rec.check_blanks()
            all_the_products = []
            all_location_ids = []
            all_categ_ids = []

            if len(rec.category_ids) == 0:
                all_categ_ids = rec.env['product.category'].search([]).ids
            else:
                for cat in rec.category_ids:
                    all_categ_ids.append(cat.id)

            if rec.mueble == False and rec.fila == False and rec.columna == False:
                if rec.desc == False or rec.desc == '':
                    all_the_products = rec.env['product.product'].search([('categ_id', 'in', all_categ_ids)]).ids
                else:
                    all_the_products = rec.env['product.product'].search(
                        [('categ_id', 'in', all_categ_ids), ('name', 'ilike', rec.desc)]).ids
            else:
                prods_with_desc = []
                if rec.desc and rec.desc != '':
                    prods_with_desc = rec.env['product.product'].search([('name', 'ilike', rec.desc)]).ids

                prod_ubic_all = []
                prod_ubic_all = rec.env.get('x_ubicaciones', None)
                if prod_ubic_all:
                    if rec.mueble != False and rec.fila != False and rec.columna != False:
                        if rec.desc == False or rec.desc == '':
                            prod_ubic_all = rec.env.get('x_ubicaciones', None)
                            if prod_ubic_all:
                                prod_ubic_all.search(
                                    [('x_studio_almacen', '=', rec.warehouse_id.id), ('x_studio_mueble', 'ilike', rec.mueble),
                                    ('x_studio_fila', 'ilike', rec.fila), ('x_studio_columna', 'ilike', rec.columna)])
                        else:
                            prod_ubic_all = rec.env.get('x_ubicaciones', None)
                            if prod_ubic_all:
                                prod_ubic_all.search(
                                        [('x_studio_almacen', '=', rec.warehouse_id.id), ('x_studio_mueble', 'ilike', rec.mueble),
                                        ('x_studio_fila', 'ilike', rec.fila), ('x_studio_columna', 'ilike', rec.columna),
                                        ('x_producto', 'in', prods_with_desc)])
                    elif rec.mueble != False and rec.fila != False and rec.columna == False:
                        if rec.desc == False or rec.desc == '':
                            prod_ubic_all = rec.env['x_ubicaciones'].search(
                                [('x_studio_almacen', '=', rec.warehouse_id.id), ('x_studio_mueble', 'ilike', rec.mueble),
                                 ('x_studio_fila', 'ilike', rec.fila)])
                        else:
                            prod_ubic_all = rec.env['x_ubicaciones'].search(
                                [('x_studio_almacen', '=', rec.warehouse_id.id), ('x_studio_mueble', 'ilike', rec.mueble),
                                 ('x_studio_fila', 'ilike', rec.fila), ('x_producto', 'in', prods_with_desc)])
                    elif rec.mueble != False and rec.fila == False and rec.columna != False:
                        if rec.desc == False or rec.desc == '':
                            prod_ubic_all = rec.env.get('x_ubicaciones', None)
                            if prod_ubic_all:
                                prod_ubic_all.search(
                                    [('x_studio_almacen', '=', rec.warehouse_id.id), ('x_studio_mueble', 'ilike', rec.mueble),
                                     ('x_studio_columna', 'ilike', rec.columna)])
                        else:
                            prod_ubic_all = rec.env['x_ubicaciones'].search(
                                [('x_studio_almacen', '=', rec.warehouse_id.id), ('x_studio_mueble', 'ilike', rec.mueble),
                                 ('x_studio_columna', 'ilike', rec.columna), ('x_producto', 'in', prods_with_desc)])
                    elif rec.mueble != False and rec.fila == False and rec.columna == False:
                        if rec.desc == False or rec.desc == '':
                            prod_ubic_all = rec.env['x_ubicaciones'].search(
                                [('x_studio_almacen', '=', rec.warehouse_id.id), ('x_studio_mueble', 'ilike', rec.mueble)])
                        else:
                            prod_ubic_all = rec.env['x_ubicaciones'].search(
                                [('x_studio_almacen', '=', rec.warehouse_id.id), ('x_studio_mueble', 'ilike', rec.mueble),
                                 ('x_producto', 'in', prods_with_desc)])
                    elif rec.mueble == False and rec.fila != False and rec.columna != False:
                        if rec.desc == False or rec.desc == '':
                            prod_ubic_all = rec.env['x_ubicaciones'].search(
                                [('x_studio_almacen', '=', rec.warehouse_id.id), ('x_studio_fila', 'ilike', rec.fila),
                                 ('x_studio_columna', 'ilike', rec.columna)])
                        else:
                            prod_ubic_all = rec.env['x_ubicaciones'].search(
                                [('x_studio_almacen', '=', rec.warehouse_id.id), ('x_studio_fila', 'ilike', rec.fila),
                                 ('x_studio_columna', 'ilike', rec.columna), ('x_producto', 'in', prods_with_desc)])
                    elif rec.mueble == False and rec.fila != False and rec.columna == False:
                        if rec.desc == False or rec.desc == '':
                            prod_ubic_all = rec.env['x_ubicaciones'].search(
                                [('x_studio_almacen', '=', rec.warehouse_id.id), ('x_studio_fila', 'ilike', rec.fila)])
                        else:
                            prod_ubic_all = rec.env['x_ubicaciones'].search(
                                [('x_studio_almacen', '=', rec.warehouse_id.id), ('x_studio_fila', 'ilike', rec.fila),
                                 ('x_producto', 'in', prods_with_desc)])
                    elif rec.mueble == False and rec.fila == False and rec.columna != False:
                        if rec.desc == False or rec.desc == '':
                            prod_ubic_all = rec.env['x_ubicaciones'].search([('x_studio_almacen', '=', rec.warehouse_id.id),
                                                                             ('x_studio_columna', 'ilike', rec.columna)])
                        else:
                            prod_ubic_all = rec.env['x_ubicaciones'].search(
                                [('x_studio_almacen', '=', rec.warehouse_id.id), ('x_studio_columna', 'ilike', rec.columna),
                                 ('x_producto', 'in', prods_with_desc)])
                    if prod_ubic_all:
                        for prod in prod_ubic_all:
                            record = rec.env['product.product'].search(
                            [('id', '=', prod.x_producto.id), ('categ_id', 'in', all_categ_ids)])
                            all_the_products.append(record.id)

            for location in rec.warehouse_id.view_location_id:
                all_location_ids.append(location.id)
                for child in location.child_ids:
                    all_location_ids.append(child.id)

            date = rec.date
            min_time = datetime.min.time()
            min_date = datetime(rec.date.year, rec.date.month, rec.date.day, 0, 0, 0)
            max_time = datetime.max.time()
            max_date = datetime(rec.date.year, rec.date.month, rec.date.day, 23, 59, 59)

            for prod in all_the_products:
                move_ids = rec.env['stock.move'].search(
                    [('product_id', '=', prod), ('date', '<=', max_date), ('location_id', 'in', all_location_ids),
                     ('state', 'in', ['done'])])
                move_ids += rec.env['stock.move'].search(
                    [('product_id', '=', prod), ('date', '<=', max_date), ('location_dest_id', 'in', all_location_ids),
                     ('state', 'in', ['done'])])
                quantity = 0
                # raise ValidationError(move_ids[0].name)
                for move in move_ids:
                    if move.picking_code == "outgoing":
                        quantity -= move.product_uom_qty
                    elif move.picking_code == "incoming":
                        quantity += move.product_uom_qty
                    elif move.picking_code == False:
                        quantity += move.product_uom_qty
                    else:
                        if move.location_id.operating_unit_id.id != move.location_dest_id.operating_unit_id.id and move.location_id.operating_unit_id.id != False and move.location_dest_id.operating_unit_id.id != False:
                            quantity -= move.product_uom_qty
                        elif move.location_dest_id.operating_unit_id.id == False:
                            quantity -= move.product_uom_qty
                if (rec.inc_solo_prod_saldo == True and quantity > 0) or (rec.inc_solo_prod_saldo == False):
                    product_id = rec.env['product.product'].search([('id', '=', prod)], limit=1)

                    ubication_id = rec.env['x_ubicaciones'].search(
                        [('x_producto', '=', prod), ('x_studio_almacen', '=', rec.warehouse_id.id)], limit=1)

                    concat_ubic = ""
                    if ubication_id.x_studio_mueble:
                        concat_ubic += ubication_id.x_studio_mueble
                    if ubication_id.x_studio_fila:
                        concat_ubic += "-" + ubication_id.x_studio_fila
                    if ubication_id.x_studio_columna:
                        concat_ubic += "-" + ubication_id.x_studio_columna

                    record = rec.env['report.existencia_ubicacion_lines'].create({
                        'report_existencia_ubicacion': rec.id,
                        'code': product_id.default_code,
                        'product_id': product_id.id,
                        'exist': quantity,
                        'cost_prom': product_id.standard_price,
                        'ubication': concat_ubic,
                        'grav': True if len(product_id.taxes_id) > 0 else False,
                    })

        return self.env.ref('ctt_dassa_reports.ctt_dassa_reports_existencia_mod_ubicacion_report').with_context(
            from_transient_model=True).report_action(self)


class report_existencia_ubicacion_lines(models.TransientModel):
    _name = 'report.existencia_ubicacion_lines'
    _description = 'Lineas que muestran los datos a imprimir para el reporte exsitencia por ubicación'

    report_existencia_ubicacion = fields.Many2one(
        'report.existencia_ubicacion',
        string="Wizard"
    )
    code = fields.Char(
        string="Codigo del producto"
    )
    product_id = fields.Many2one(
        'product.product',
        string="Descripción del producto"
    )
    exist = fields.Float(
        string="Existencia"
    )
    cost_prom = fields.Float(
        string="Costo promedio"
    )
    ubication = fields.Char(
        string="Ubicación"
    )
    grav = fields.Boolean(
        string="Tiene iva?"
    )
    location_id = fields.Many2one(
        'stock.location',
        string="locacion"
    )


class marcas(models.TransientModel):
    _name = 'x_marcas'

    x_name = fields.Char()
    x_studio_field_OIAJp = fields.Char()


class report_saldos(models.TransientModel):
    _name = 'report.saldos'
    _description = 'Wizard de impresión para reporte de saldos'
    _inherit = ['report.comun_data_product_selection', 'report.comun_data_almacen_selection']

    agrupation = fields.Selection(
        [
            ('line', 'Línea'),
            ('brand', 'Marca'),
        ],
        default="line",
        string="Agrupación",
    )
    brand_ids = fields.Many2many(
        'x_marcas',
        string="Marcas"
    )
    begin_date = fields.Datetime(
        string="Fecha de inicio",
        required=True,
        default=datetime(datetime.now().year, datetime.now().month, datetime.now().day - 1, 6, 0, 0)
    )
    end_date = fields.Datetime(
        string="Fecha de terminación",
        required=True,
        default=datetime.strptime(
            str(datetime.now().year) + "-" + str(datetime.now().month) + "-" + str(datetime.now().day) + " 05:59:59",
            '%Y-%m-%d %H:%M:%S')
    )
    inc_prod_baja = fields.Boolean(
        string="Incluir Productos dados de baja",
        default=False
    )
    inc_prod_mov_saldo = fields.Boolean(
        string="Incluir Productos con movimientos o saldo",
        default=False
    )
    inc_prod_saldo_neg = fields.Boolean(
        string="Incluir Productos con saldo negativo",
        default=False
    )
    inc_solo_prod_mov = fields.Boolean(
        string="Incluir Productos solo con movimiento",
        default=False
    )
    product_ids = fields.Many2many(
        'product.product',
        string="Producto",
    )
    date_begin_char = fields.Char(
        string="Date_char begin"
    )
    date_end_char = fields.Char(
        string="Date_char end"
    )
    saldos_lines = fields.One2many(
        'report.saldos_lines',
        'saldo_id',
        string="Líneas de saldo"
    )

    def end_date_default(self):
        tz = pytz.timezone("America/Mazatlan")
        dia = datetime.now().day
        mes = datetime.now().month
        agno = datetime.now().year
        datee = str(agno) + "-" + str(mes) + "-" + str(dia) + " 06:59:59"
        date_end = datetime.strptime(datee, '%Y-%m-%d %H:%M:%S')

        self.end_date = date_end

    def check_options(self):
        if len(self.product_ids) > 0:
            self.inc_prod_baja = False
            self.inc_prod_mov_saldo = False
            self.inc_prod_saldo_neg = False
            self.inc_solo_prod_mov = False

    def print_report(self):
        self.saldos_lines.unlink()
        self.check_options()

        for rec in self:
            all_warehouses = []
            # --OBTENIENDO LOS ALMACENES
            if len(rec.warehouse_ids) == 0:
                all_warehouses = rec.env['stock.warehouse'].search([]).ids
            else:
                for warehouse_id in rec.warehouse_ids:
                    all_warehouses.append(warehouse_id.id)
            warehouse_ids = rec.env['stock.warehouse'].search([('id', 'in', all_warehouses)],
                                                              order="operating_unit_id ASC")
            user_tz = pytz.timezone("America/Mazatlan")
            date_begin = pytz.utc.localize(rec.begin_date).astimezone(user_tz)
            date_end = pytz.utc.localize(rec.end_date).astimezone(user_tz)
            rec.date_begin_char = str(date_begin.strftime("%d/%m/%Y %H:%M:%S"))
            rec.date_end_char = str(date_end.strftime("%d/%m/%Y %H:%M:%S"))

            data_get = []
            product_ids_before_filter = rec.env['product.product']
            if len(rec.product_ids) == 0:
                if rec.agrupation == "line" or rec.agrupation == 'brand':
                    if rec.agrupation == 'line':
                        if len(rec.category_ids) > 0:
                            for cat in rec.category_ids:
                                data_get.append(cat.id)
                        else:
                            data_get = rec.env['product.category'].search([]).ids

                        if rec.inc_prod_baja == True:
                            product_ids_before_filter = rec.env['product.product'].search(
                                [('categ_id', 'in', data_get), ('active', 'in', [True, False])])
                        else:
                            product_ids_before_filter = rec.env['product.product'].search(
                                [('categ_id', 'in', data_get)])
                    else:
                        if len(rec.brand_ids) > 0:
                            for brnd in rec.brand_ids:
                                data_get.append(brnd.id)
                        else:
                            data_get = rec.env['x_marcas'].search([]).ids
                        if rec.inc_prod_baja == True:
                            # product_ids_before_filter = rec.env['product.product'].search(
                            #     [('x_studio_field_68yom', 'in', data_get), ('active', 'in', [True, False])])
                            domain = [('active', 'in', [True, False])]
                            product_obj = rec.env['product.product']
                            if hasattr(product_obj,'x_studio_field_68yom'):
                                domain.append(('x_studio_field_68yom', 'in', data_get))
                                product_ids_before_filter = rec.env['product.product'].search(domain)

                        else:
                            # product_ids_before_filter = rec.env['product.product'].search(
                                # [('x_studio_field_68yom', 'in', data_get)])
                            product_obj = rec.env['product.product']
                            if hasattr(product_obj,'x_studio_field_68yom'):
                                domain=[('x_studio_field_68yom', 'in', data_get)]
                                product_ids_before_filter = rec.env['product.product'].search(domain)
            else:
                for prod in rec.product_ids:
                    data_get.append(prod.id)
                product_ids_before_filter = rec.env['product.product'].search([('id', 'in', data_get)])

            for warehouse_id in warehouse_ids:
                all_location_ids = []
                for location in warehouse_id.view_location_id:
                    for child in location.child_ids:
                        # Aqui se obtienen las ubicaciones hijos como por ejemplo mochis: MOCH1/Taller, MOCH1/Refacciones etc...
                        all_location_ids.append(child.id)

                for product_id in product_ids_before_filter:
                    for location_id in all_location_ids:
                        move_ids_before = rec.env['stock.move'].search(
                            [('product_id', '=', product_id.id), ('date', '<=', date_begin),
                             ('location_id', 'in', [location_id]), ('state', 'in', ['done'])])
                        move_ids_before += rec.env['stock.move'].search(
                            [('product_id', '=', product_id.id), ('date', '<=', date_begin),
                             ('location_dest_id', 'in', [location_id]), ('state', 'in', ['done'])])

                        move_ids = rec.env['stock.move'].search(
                            [('product_id', '=', product_id.id), ('date', '>=', date_begin), ('date', '<=', date_end),
                             ('location_id', 'in', [location_id]), ('state', 'in', ['done'])])
                        move_ids += rec.env['stock.move'].search(
                            [('product_id', '=', product_id.id), ('date', '>=', date_begin), ('date', '<=', date_end),
                             ('location_dest_id', 'in', [location_id]), ('state', 'in', ['done'])])

                        move_ids_after = rec.env['stock.move'].search(
                            [('product_id', '=', product_id.id), ('date', '<=', date_end),
                             ('location_id', 'in', [location_id]), ('state', 'in', ['done'])])
                        move_ids_after += rec.env['stock.move'].search(
                            [('product_id', '=', product_id.id), ('date', '<=', date_end),
                             ('location_dest_id', 'in', [location_id]), ('state', 'in', ['done'])])

                        balance_prev_unids = 0
                        for move_id_before in move_ids_before:
                            if move_id_before.picking_code == "outgoing":
                                balance_prev_unids -= move_id_before.product_uom_qty
                            elif move_id_before.picking_code == "incoming":
                                balance_prev_unids += move_id_before.product_uom_qty
                            elif move_id_before.picking_code == False:
                                balance_prev_unids += move_id_before.product_uom_qty
                            else:
                                if move_id_before.location_id.operating_unit_id.id != move_id_before.location_dest_id.operating_unit_id.id and move_id_before.location_id.operating_unit_id.id != False and move_id_before.location_dest_id.operating_unit_id.id != False:
                                    balance_prev_unids -= move_id_before.product_uom_qty
                                elif move_id_before.location_dest_id.operating_unit_id.id == False:
                                    balance_prev_unids -= move_id_before.product_uom_qty

                        entries = 0
                        outs = 0
                        for move_id in move_ids:
                            if move_id.picking_code == "outgoing":
                                outs -= move_id.product_uom_qty
                            elif move_id.picking_code == "incoming":
                                entries += move_id.product_uom_qty
                            elif move_id.picking_code == False:
                                entries += move_id.product_uom_qty
                            else:
                                if move_id.location_id.operating_unit_id.id != move_id.location_dest_id.operating_unit_id.id and move_id.location_id.operating_unit_id.id != False and move_id.location_dest_id.operating_unit_id.id != False:
                                    outs -= move_id.product_uom_qty
                                elif move_id.location_dest_id.operating_unit_id.id == False:
                                    outs -= move_id.product_uom_qty

                        balance_act_unids = 0
                        for move_id_after in move_ids_after:
                            if move_id_after.picking_code == "outgoing":
                                balance_act_unids -= move_id_after.product_uom_qty
                            elif move_id_after.picking_code == "incoming":
                                balance_act_unids += move_id_after.product_uom_qty
                            elif move_id_after.picking_code == False:
                                balance_act_unids += move_id_after.product_uom_qty
                            else:
                                if move_id_after.location_id.operating_unit_id.id != move_id_after.location_dest_id.operating_unit_id.id and move_id_after.location_id.operating_unit_id.id != False and move_id_after.location_dest_id.operating_unit_id.id != False:
                                    balance_act_unids -= move_id_after.product_uom_qty
                                elif move_id_after.location_dest_id.operating_unit_id.id == False:
                                    balance_act_unids -= move_id_after.product_uom_qty

                        # RESERVADOS
                        move_ids_reserved = rec.env['stock.move'].search(
                            [('product_id', '=', product_id.id), ('date', '<=', date_end),
                             ('location_id', 'in', [location_id]), ('state', 'in', ['assigned'])])
                        move_ids_reserved += rec.env['stock.move'].search(
                            [('product_id', '=', product_id.id), ('date', '<=', date_end),
                             ('location_dest_id', 'in', [location_id]), ('state', 'in', ['assigned'])])
                        reserved_quants = 0
                        for move_id_reserved in move_ids_reserved:
                            if move_id_reserved.picking_code == "outgoing":
                                reserved_quants -= move_id_reserved.product_uom_qty
                            elif move_id_reserved.picking_code == "incoming":
                                reserved_quants += move_id_reserved.product_uom_qty
                            elif move_id_reserved.picking_code == False:
                                reserved_quants += move_id_reserved.product_uom_qty
                            else:
                                if move_id_reserved.location_id.operating_unit_id.id != move_id_reserved.location_dest_id.operating_unit_id.id and move_id_reserved.location_id.operating_unit_id.id != False and move_id_reserved.location_dest_id.operating_unit_id.id != False:
                                    reserved_quants -= move_id_reserved.product_uom_qty
                                elif move_id_after.location_dest_id.operating_unit_id.id == False:
                                    reserved_quants -= move_id_reserved.product_uom_qty

                        save = False
                        if len(rec.product_ids) == 0:
                            if rec.inc_solo_prod_mov == True:
                                if entries > 0 or outs > 0:
                                    if rec.inc_prod_saldo_neg == True:
                                        save = True
                                    else:
                                        if balance_act_unids > 0 or balance_act_unids * product_id.standard_price > 0:
                                            save = True
                            elif rec.inc_prod_mov_saldo == True:
                                if entries > 0 or outs > 0 or balance_act_unids > 0:
                                    if rec.inc_prod_saldo_neg == True:
                                        save = True
                                    else:
                                        if balance_act_unids > 0 or balance_act_unids * product_id.standard_price > 0:
                                            save = True
                            elif rec.inc_prod_saldo_neg == False:
                                if balance_act_unids > 0 or balance_act_unids * product_id.standard_price > 0:
                                    save = True
                                else:
                                    save = True
                            else:
                                if balance_prev_unids != 0 or entries != 0 or outs != 0 or balance_act_unids != 0:
                                    save = True
                        else:
                            if balance_prev_unids != 0 or entries != 0 or outs != 0 or balance_act_unids != 0:
                                save = True

                        if save == True:
                            record = rec.env['report.saldos_lines'].create({
                                'type': 'd',
                                'saldo_id': rec.id,
                                'sucursal': warehouse_id.operating_unit_id.id,
                                'warehouse_id': warehouse_id.id,
                                'location_id': location_id,
                                'product_id': product_id.id,
                                'balance_prev_unids': balance_prev_unids,
                                'balance_prev_values': balance_prev_unids * product_id.standard_price,
                                'entr_unids': entries,
                                'entr_values': entries * product_id.standard_price,
                                'out_unids': outs,
                                'out_values': outs * product_id.standard_price,
                                'balance_act_unids': balance_act_unids,
                                'balance_act_values': balance_act_unids * product_id.standard_price,
                                'reserved_quants': reserved_quants
                            })
                del all_location_ids

            all_sucursals = []
            all_warehouse = []
            all_locations = []
            for line in rec.saldos_lines:
                all_sucursals.append(line.sucursal.id)
                all_warehouse.append(line.warehouse_id.id)
                all_locations.append(line.location_id.id)
            report_lines = rec.env['report.saldos_lines'].search(
                [('saldo_id', '=', rec.id), ('sucursal', 'in', all_sucursals), ('type', 'in', ['d'])])
            report_lines_grouped = report_lines.read_group([('sucursal', 'in', all_sucursals)], fields=['sucursal'],
                                                           groupby=['sucursal'])
            # SACANDO LOS TOTALES POR SUCURSAL
            for sald_ord in report_lines_grouped:
                balance_prev_unids = 0
                balance_prev_values = 0
                entr_unids = 0
                entr_values = 0
                out_unids = 0
                out_values = 0
                balance_act_unids = 0
                balance_act_values = 0
                reserved_quants = 0
                for record_line in report_lines:
                    if record_line.sucursal.id == sald_ord['sucursal'][0]:
                        balance_prev_unids += record_line.balance_prev_unids
                        balance_prev_values += record_line.balance_prev_values
                        entr_unids += record_line.entr_unids
                        entr_values += record_line.entr_values
                        out_unids += record_line.out_unids
                        out_values += record_line.out_values
                        balance_act_unids += record_line.balance_act_unids
                        balance_act_values += record_line.balance_act_values
                        reserved_quants += record_line.reserved_quants
                record = rec.env['report.saldos_lines'].create({
                    'saldo_id': rec.id,
                    'type': 's',
                    'sucursal': sald_ord['sucursal'][0],
                    'balance_prev_unids': balance_prev_unids,
                    'balance_prev_values': balance_prev_values,
                    'entr_unids': entr_unids,
                    'entr_values': entr_values,
                    'out_unids': out_unids,
                    'out_values': out_values,
                    'balance_act_unids': balance_act_unids,
                    'balance_act_values': balance_act_values,
                    'reserved_quants': reserved_quants
                })
            # SACANDO LOS TOTALES POR ALMACEN
            report_lines = rec.env['report.saldos_lines'].search(
                [('saldo_id', '=', rec.id), ('warehouse_id', 'in', all_warehouse), ('type', 'in', ['d'])])
            report_lines_grouped = report_lines.read_group([('warehouse_id', 'in', all_warehouse)],
                                                           fields=['warehouse_id'], groupby=['warehouse_id'])
            for sald_ord in report_lines_grouped:
                balance_prev_unids = 0
                balance_prev_values = 0
                entr_unids = 0
                entr_values = 0
                out_unids = 0
                out_values = 0
                balance_act_unids = 0
                balance_act_values = 0
                reserved_quants = 0
                for record_line in report_lines:
                    if record_line.warehouse_id.id == sald_ord['warehouse_id'][0]:
                        balance_prev_unids += record_line.balance_prev_unids
                        balance_prev_values += record_line.balance_prev_values
                        entr_unids += record_line.entr_unids
                        entr_values += record_line.entr_values
                        out_unids += record_line.out_unids
                        out_values += record_line.out_values
                        balance_act_unids += record_line.balance_act_unids
                        balance_act_values += record_line.balance_act_values
                        reserved_quants += record_line.reserved_quants
                record = rec.env['report.saldos_lines'].create({
                    'saldo_id': rec.id,
                    'type': 'w',
                    'warehouse_id': sald_ord['warehouse_id'][0],
                    'balance_prev_unids': balance_prev_unids,
                    'balance_prev_values': balance_prev_values,
                    'entr_unids': entr_unids,
                    'entr_values': entr_values,
                    'out_unids': out_unids,
                    'out_values': out_values,
                    'balance_act_unids': balance_act_unids,
                    'balance_act_values': balance_act_values,
                    'reserved_quants': reserved_quants
                })
            # SACANDO LOS TOTALES POR LOCACION
            report_lines = rec.env['report.saldos_lines'].search(
                [('saldo_id', '=', rec.id), ('location_id', 'in', all_locations), ('type', 'in', ['d'])])
            report_lines_grouped = report_lines.read_group([('location_id', 'in', all_locations)],
                                                           fields=['location_id'], groupby=['location_id'])
            for sald_ord in report_lines_grouped:
                balance_prev_unids = 0
                balance_prev_values = 0
                entr_unids = 0
                entr_values = 0
                out_unids = 0
                out_values = 0
                balance_act_unids = 0
                balance_act_values = 0
                reserved_quants = 0
                for record_line in report_lines:
                    if record_line.location_id.id == sald_ord['location_id'][0]:
                        balance_prev_unids += record_line.balance_prev_unids
                        balance_prev_values += record_line.balance_prev_values
                        entr_unids += record_line.entr_unids
                        entr_values += record_line.entr_values
                        out_unids += record_line.out_unids
                        out_values += record_line.out_values
                        balance_act_unids += record_line.balance_act_unids
                        balance_act_values += record_line.balance_act_values
                        reserved_quants += record_line.reserved_quants
                record = rec.env['report.saldos_lines'].create({
                    'saldo_id': rec.id,
                    'type': 'l',
                    'location_id': sald_ord['location_id'][0],
                    'balance_prev_unids': balance_prev_unids,
                    'balance_prev_values': balance_prev_values,
                    'entr_unids': entr_unids,
                    'entr_values': entr_values,
                    'out_unids': out_unids,
                    'out_values': out_values,
                    'balance_act_unids': balance_act_unids,
                    'balance_act_values': balance_act_values,
                    'reserved_quants': reserved_quants
                })

        return self.env.ref('ctt_dassa_reports.ctt_dassa_reports_saldos_report').with_context(
            from_transient_model=True).report_action(self)


class report_saldos_lines(models.TransientModel):
    _name = 'report.saldos_lines'
    _description = 'Lineas que muestran los datos a imprimir para el reporte de saldos'
    _order = "type,sucursal,warehouse_id ASC"

    type = fields.Selection(
        [
            ('d', 'Dato'),
            ('s', 'Sucursal'),
            ('w', 'Almacen'),
            ('l', 'Locacion')
        ],
        string="Tipo de dato",
    )
    saldo_id = fields.Many2one(
        'report.saldos',
        string="wizard saldos"
    )
    sucursal = fields.Many2one(
        'operating.unit',
        string="Sucursal"
    )
    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string="Almacen"
    )
    location_id = fields.Many2one(
        'stock.location',
        string="Locacion"
    )
    code = fields.Char(
        string="Código"
    )
    product_id = fields.Many2one(
        'product.product',
        string="Producto"
    )
    balance_prev_unids = fields.Float(
        string="Saldo anterior unidades"
    )
    balance_prev_values = fields.Float(
        string="Saldo anterior valores"
    )
    entr_unids = fields.Float(
        string="Entradas unidades"
    )
    entr_values = fields.Float(
        string="Entradas valores"
    )
    out_unids = fields.Float(
        string="Salidas unidades"
    )
    out_values = fields.Float(
        string="Salidas valores"
    )
    balance_act_unids = fields.Float(
        string="Saldo actual unidades"
    )
    balance_act_values = fields.Float(
        string="Saldo actual valores"
    )
    reserved_quants = fields.Float(
        string="Cantidades reservadas"
    )


class report_ventas_departamento(models.TransientModel):
    _name = 'report.ventas_departamento'
    _description = 'Wizard de impresión para reporte de ventas por departamento'

    sucursal = fields.Many2one(
        'operating.unit',
        string="Sucursal",
        required=True
    )
    date = fields.Date(
        string="Fecha al",
        required=True
    )
    journal_ids = fields.Many2many(
        'account.journal',
        string="Diario"
    )
    report_lines = fields.One2many(
        'report.ventas_departamento_lines',
        'report_departament_id',
        string="Lineas del reporte"
    )
    report_verificator_lines = fields.One2many(
        'report.ventas_departamento_verificator_lines',
        'report_departament_id',
        string="Lineas del reporte"
    )

    def print_report(self):
        self.ensure_one()
        for rec in self:
            rec.report_lines.unlink()
            rec.report_verificator_lines.unlink()
            date_min = str(rec.date.year) + "-" + str(rec.date.month) + "-01" + " 00:00:00"
            date_min = datetime.strptime(date_min, '%Y-%m-%d %H:%M:%S')
            date_max = str(rec.date.year) + "-" + str(rec.date.month) + "-" + str(rec.date.day) + " 23:59:59"
            date_max = datetime.strptime(date_max, '%Y-%m-%d %H:%M:%S')
            date_max_actual = str(rec.date.year) + "-" + str(rec.date.month) + "-" + str(rec.date.day) + " 00:00:00"
            date_max_actual = datetime.strptime(date_max_actual, '%Y-%m-%d %H:%M:%S')
            all_journal_ids = []
            if len(rec.journal_ids) == 0:
                all_journal_ids = rec.env['account.journal'].search(
                    [('operating_unit_id', '=', rec.sucursal.id), ('type', 'in', ['sale'])]).ids
            else:
                for journal_id in rec.journal_ids:
                    all_journal_ids.append(journal_id.id)

            # VENTAS DEL DIA
            invoice_ids = rec.env['account.move'].search(
                [('operating_unit_id', '=', rec.sucursal.id), ('journal_id', 'in', all_journal_ids),
                 ('invoice_date', '=', rec.date), ('state', 'in', ['open', 'in_payment', 'paid']),
                 ('move_type', 'in', ['out_invoice', 'in_invoice'])])
            invoice_ids_grouped = invoice_ids.read_group([('journal_id', 'in', all_journal_ids)], fields=['journal_id'],
                                                         groupby=['journal_id'])
            for inv in invoice_ids_grouped:
                global_total = 0
                global_iva = 0
                global_contado = 0
                global_credito = 0
                global_venta_neta = 0
                global_costo = 0
                global_margin = 0
                global_departament = False
                global_tax_amount = 0
                store = False
                for record_inv in invoice_ids:
                    if record_inv.journal_id.id == inv['journal_id'][0]:
                        store = True
                        global_venta_neta += record_inv.amount_untaxed
                        if record_inv.payment_term_id.is_immediate == True:
                            global_contado += record_inv.amount_total
                        else:
                            global_credito += record_inv.amount_total
                        global_iva += record_inv.amount_tax
                        for line in record_inv.invoice_line_ids:
                            global_costo += line.purchase_price
                            global_margin += line.margin
                        global_total += record_inv.amount_total
                        departament = record_inv.journal_id.tipo

                        global_tax_amount += record_inv.amount_tax
                        for record_inv_line in record_inv.invoice_line_ids:
                            account_id = rec.env['report.ventas_departamento_lines'].search(
                                [('report_departament_id', '=', rec.id), ('type', 'in', ['sale_day']),
                                 ('departament', '=', departament), ('account_id', '=', record_inv_line.account_id.id),
                                 ('desglosado', '=', True)])
                            if len(account_id) == 0:
                                perc = (record_inv_line.margin * 100) / record_inv_line.price_subtotal
                                record = rec.env['report.ventas_departamento_lines'].create({
                                    'report_departament_id': rec.id,
                                    'type': 'sale_day',
                                    'departament': departament,
                                    'account_id': record_inv_line.account_id.id,
                                    'cost': record_inv_line.purchase_price,
                                    'sale_neto': record_inv_line.price_subtotal,
                                    'credit': record_inv_line.price_total if record_inv.payment_term_id.is_immediate == False else 0,
                                    'debit': record_inv_line.price_total if record_inv.payment_term_id.is_immediate == True else 0,
                                    'iva': record_inv_line.price_total - record_inv_line.price_subtotal,
                                    'margin': record_inv_line.margin,
                                    'subtotal': record_inv_line.price_subtotal,
                                    'perc': perc,
                                    'desglosado': True
                                })
                            else:
                                subtotal = 0
                                credit_contado = 0
                                if record_inv.payment_term_id.is_immediate == True:
                                    credit_contado = account_id.debit + record_inv_line.price_total
                                else:
                                    credit_contado = account_id.credit + record_inv_line.price_total
                                cost = account_id.cost + record_inv_line.purchase_price
                                taxes = account_id.iva + (record_inv_line.price_total - record_inv_line.price_subtotal)
                                subtotal = account_id.subtotal + record_inv_line.price_subtotal
                                margin = account_id.margin + record_inv_line.margin
                                sale_neto = account_id.sale_neto + record_inv_line.price_subtotal
                                perc = (margin * 100) / subtotal
                                if record_inv.payment_term_id.is_immediate == True:
                                    account_id.write({
                                        'report_departament_id': rec.id,
                                        'type': 'sale_day',
                                        'departament': departament,
                                        'account_id': record_inv_line.account_id.id,
                                        'cost': cost,
                                        'sale_neto': sale_neto,
                                        'debit': credit_contado,
                                        'iva': taxes,
                                        'margin': margin,
                                        'subtotal': subtotal,
                                        'perc': perc,
                                        'desglosado': True
                                    })
                                else:
                                    account_id.write({
                                        'report_departament_id': rec.id,
                                        'type': 'sale_day',
                                        'departament': departament,
                                        'account_id': record_inv_line.account_id.id,
                                        'cost': cost,
                                        'sale_neto': sale_neto,
                                        'credit': credit_contado,
                                        'iva': taxes,
                                        'margin': margin,
                                        'subtotal': subtotal,
                                        'perc': perc,
                                        'desglosado': True
                                    })

                global_perc = 0
                if store == True:
                    global_perc = (global_margin * 100) / global_venta_neta
                    get_dep = rec.env['report.ventas_departamento_lines'].search(
                        [('report_departament_id', '=', rec.id), ('departament', '=', departament),
                         ('type', 'in', ['sale_day']), ('desglosado', 'in', [False])])
                    if len(get_dep) == 0:
                        record = rec.env['report.ventas_departamento_lines'].create({
                            'report_departament_id': rec.id,
                            'type': 'sale_day',
                            'departament': departament,
                            'cost': global_costo,
                            'sale_neto': global_venta_neta,
                            'credit': global_credito,
                            'debit': global_contado,
                            'iva': global_iva,
                            'total': global_total,
                            'margin': global_margin,
                            'perc': global_perc
                        })
                    else:
                        global_costo += get_dep.cost
                        global_venta_neta += get_dep.sale_neto
                        global_credito += get_dep.credit
                        global_contado += get_dep.debit
                        global_iva += get_dep.debit
                        global_total += get_dep.debit
                        global_margin += get_dep.margin
                        if global_venta_neta == 0:
                            global_perc = 0
                        else:
                            global_perc = (margin * 100) / global_venta_neta
                        record = get_dep.write({
                            'report_departament_id': rec.id,
                            'type': 'sale_day',
                            'departament': departament,
                            'cost': global_costo,
                            'sale_neto': global_venta_neta,
                            'credit': global_credito,
                            'debit': global_contado,
                            'iva': global_iva,
                            'total': global_total,
                            'margin': global_margin,
                            'perc': global_perc
                        })
                else:
                    global_perc = 0

            # VENTAS ACUMULADAS
            invoice_ids = rec.env['account.move'].search(
                [('operating_unit_id', '=', rec.sucursal.id), ('journal_id', 'in', all_journal_ids),
                 ('invoice_date', '<=', date_max), ('invoice_date', '>=', date_min),
                 ('state', 'in', ['open', 'in_payment', 'paid']), ('move_type', 'in', ['out_invoice', 'in_invoice'])])
            invoice_ids_grouped = invoice_ids.read_group([('journal_id', 'in', all_journal_ids)], fields=['journal_id'],
                                                         groupby=['journal_id'])
            store = False
            for inv in invoice_ids_grouped:
                total = 0
                iva = 0
                contado = 0
                credito = 0
                venta_neta = 0
                costo = 0
                margin = 0
                perc = 0
                departament = False
                store = False
                for record_inv in invoice_ids:
                    if record_inv.journal_id.id == inv['journal_id'][0]:
                        store = True
                        venta_neta += record_inv.amount_untaxed
                        if record_inv.payment_term_id.is_immediate == True:
                            contado += record_inv.amount_total
                        else:
                            credito += record_inv.amount_total
                        iva += record_inv.amount_tax
                        for line in record_inv.invoice_line_ids:
                            costo += line.purchase_price
                            margin += line.margin
                        total += record_inv.amount_total
                        departament = record_inv.journal_id.tipo

                if store == True:
                    if venta_neta == 0:
                        perc = 0
                    else:
                        perc = (margin * 100) / venta_neta
                    get_dep = rec.env['report.ventas_departamento_lines'].search(
                        [('report_departament_id', '=', rec.id), ('departament', '=', departament),
                         ('type', 'in', ['sale_acum'])])
                    if len(get_dep) == 0:
                        record = rec.env['report.ventas_departamento_lines'].create({
                            'report_departament_id': rec.id,
                            'type': 'sale_acum',
                            'departament': departament,
                            'cost': costo,
                            'sale_neto': venta_neta,
                            'credit': credito,
                            'debit': contado,
                            'iva': iva,
                            'total': total,
                            'margin': margin,
                            'perc': perc
                        })
                    else:
                        costo += get_dep.cost
                        venta_neta += get_dep.sale_neto
                        credito += get_dep.credit
                        contado += get_dep.debit
                        iva += get_dep.debit
                        total += get_dep.debit
                        margin += get_dep.margin
                        if venta_neta == 0:
                            perc = 0
                        else:
                            perc = (margin * 100) / venta_neta

                        record = get_dep.write({
                            'report_departament_id': rec.id,
                            'type': 'sale_acum',
                            'departament': departament,
                            'cost': costo,
                            'sale_neto': venta_neta,
                            'credit': credito,
                            'debit': contado,
                            'iva': iva,
                            'total': total,
                            'margin': margin,
                            'perc': perc
                        })
            # --BONIFICACIONES
            credit_notes = rec.env['account.move'].search(
                [('operating_unit_id', '=', rec.sucursal.id), ('invoice_date', '=', rec.date),
                 ('move_type', 'in', ['out_refund']), ('journal_id', 'in', all_journal_ids),
                 ('state', 'in', ['draft', 'open', 'in_payment', 'paid'])])
            credit_notes_grouped = credit_notes.read_group([('journal_id', 'in', all_journal_ids)],
                                                           fields=['journal_id'], groupby=['journal_id'])

            store = False
            total = 0
            iva = 0
            contado = 0
            credito = 0
            venta_neta = 0
            costo = 0
            margin = 0
            perc = 0

            for note in credit_notes_grouped:
                global_total = 0
                global_iva = 0
                global_contado = 0
                global_credito = 0
                global_venta_neta = 0
                global_costo = 0
                global_margin = 0
                global_perc = 0
                departament = False
                store = False

                for cred_note in credit_notes:
                    if cred_note.journal_id.id == note['journal_id'][0]:
                        store = True
                        # ESTA CONDICION ES POR QUE MEDIANTE EL CODIGO SABE SI LA CUENTA ES DE DEVOLUCION, TODAS LAS QUE TIENEN ESTE CODIGO SON DE DEVOLUCION SI SE QUIERE MEJORAR ESTA CONDICION HARIA FALTA UN CAMPO QUE SEA UN BOOLEAN
                        # QUE DIGA: ¿Es cuenta de devolucion? y si esta activado la tome como tal para evitar esto
                        global_total = 0
                        global_iva = 0
                        global_contado = 0
                        global_credito = 0
                        global_venta_neta = 0
                        global_costo = 0
                        global_margin = 0
                        global_perc = 0
                        for line in cred_note.invoice_line_ids:
                            # ES BONIFICACION
                            if line.account_id.code not in ["402", "402.01.03", "402.01.04", "402.01.05", "402.01.06",
                                                            "402.03.01", "402.03.02", "402.03.03", "402.03.04",
                                                            "402.03.08", "402.03.09", "402.05", "402.05.01",
                                                            "402.05.02"]:
                                global_venta_neta += line.price_subtotal
                                if cred_note.payment_term_id.is_immediate == True:
                                    global_contado += line.price_total
                                else:
                                    global_credito += line.price_total
                                global_iva += line.price_total - line.price_subtotal
                                global_total += line.price_total
                                global_costo += line.purchase_price
                                global_margin += line.margin
                                if global_venta_neta == 0:
                                    global_perc = 0
                                else:
                                    global_perc = (global_margin * 100) / global_venta_neta

                        for line in cred_note.invoice_line_ids:
                            if line.account_id.code not in ["402", "402.01.03", "402.01.04", "402.01.05", "402.01.06",
                                                            "402.03.01", "402.03.02", "402.03.03", "402.03.04",
                                                            "402.03.08", "402.03.09", "402.05", "402.05.01",
                                                            "402.05.02"]:
                                departament = cred_note.journal_id.tipo
                                get_dep = rec.env['report.ventas_departamento_lines'].search(
                                    [('report_departament_id', '=', rec.id), ('departament', '=', departament),
                                     ('type', 'in', ['bonif_day']), ('account_id', '=', line.account_id.id),
                                     ('desglosado', '=', True)])

                                if len(get_dep) == 0:
                                    if line.price_subtotal == 0:
                                        perc = 0
                                    else:
                                        perc = (line.margin * 100) / line.price_subtotal

                                    record = rec.env['report.ventas_departamento_lines'].create({
                                        'report_departament_id': rec.id,
                                        'type': 'bonif_day',
                                        'departament': departament,
                                        'cost': line.purchase_price,
                                        'account_id': line.account_id.id,
                                        'sale_neto': line.price_subtotal,
                                        'credit': line.price_total if cred_note.payment_term_id.is_immediate == False else 0,
                                        'debit': line.price_total if cred_note.payment_term_id.is_immediate == True else 0,
                                        'iva': line.price_total - line.price_subtotal,
                                        'subtotal': line.price_total,
                                        'margin': line.margin,
                                        'perc': perc,
                                        'desglosado': True
                                    })
                                else:
                                    subtotal = 0
                                    credito = get_dep.credit
                                    contado = get_dep.debit
                                    if cred_note.payment_term_id.is_immediate == True:
                                        contado += line.price_total
                                    else:
                                        credito += line.price_total
                                    cost = get_dep.cost + line.purchase_price
                                    taxes = get_dep.iva + (line.price_total - line.price_subtotal)
                                    subtotal = get_dep.subtotal + line.price_subtotal
                                    margin = get_dep.margin + line.margin
                                    sale_neto = get_dep.sale_neto + line.price_subtotal
                                    if sale_neto == 0:
                                        perc = 0
                                    else:
                                        perc = (margin * 100) / sale_neto

                                    record = get_dep.write({
                                        'report_departament_id': rec.id,
                                        'type': 'bonif_day',
                                        'departament': departament,
                                        'cost': cost,
                                        'account_id': line.account_id.id,
                                        'sale_neto': sale_neto,
                                        'credit': credito,
                                        'debit': contado,
                                        'iva': taxes,
                                        'subtotal': subtotal,
                                        'margin': margin,
                                        'perc': perc,
                                        'desglosado': True
                                    })

                                if store == True:
                                    get_dep = rec.env['report.ventas_departamento_lines'].search(
                                        [('report_departament_id', '=', rec.id), ('departament', '=', departament),
                                         ('type', 'in', ['bonif_day']), ('desglosado', 'in', [False])])
                                    if len(get_dep) == 0:
                                        record = rec.env['report.ventas_departamento_lines'].create({
                                            'report_departament_id': rec.id,
                                            'type': 'bonif_day',
                                            'departament': departament,
                                            'cost': global_costo,
                                            'sale_neto': global_venta_neta,
                                            'credit': global_credito,
                                            'debit': global_contado,
                                            'iva': global_iva,
                                            'total': global_total,
                                            'margin': global_margin,
                                            'perc': global_perc
                                        })
                                    else:
                                        global_costo += get_dep.cost
                                        global_venta_neta += get_dep.sale_neto
                                        global_credito += get_dep.credit
                                        global_contado += get_dep.debit
                                        global_iva += get_dep.iva
                                        global_total += get_dep.total
                                        global_margin += get_dep.margin
                                        if global_venta_neta == 0:
                                            global_perc = 0
                                        else:
                                            global_perc = (margin * 100) / global_venta_neta

                                        record = get_dep.write({
                                            'report_departament_id': rec.id,
                                            'type': 'bonif_day',
                                            'departament': departament,
                                            'cost': global_costo,
                                            'sale_neto': global_venta_neta,
                                            'credit': global_credito,
                                            'debit': global_contado,
                                            'iva': global_iva,
                                            'total': global_total,
                                            'margin': global_margin,
                                            'perc': global_perc
                                        })
            # --BONIFICACIONES ACUMULADAS
            credit_notes_acum = rec.env['account.move'].search(
                [('operating_unit_id', '=', rec.sucursal.id), ('invoice_date', '<=', date_max),
                 ('invoice_date', '>=', date_min), ('move_type', 'in', ['out_refund']),
                 ('journal_id', 'in', all_journal_ids), ('state', 'in', ['open', 'in_payment', 'paid'])])
            credit_notes_acum_grouped = credit_notes_acum.read_group([('journal_id', 'in', all_journal_ids)],
                                                                     fields=['journal_id'], groupby=['journal_id'])

            store = False
            total = 0
            iva = 0
            contado = 0
            credito = 0
            venta_neta = 0
            costo = 0
            margin = 0
            perc = 0

            for note in credit_notes_acum_grouped:
                global_total = 0
                global_iva = 0
                global_contado = 0
                global_credito = 0
                global_venta_neta = 0
                global_costo = 0
                global_margin = 0
                global_perc = 0
                departament = False
                store = False

                for cred_note in credit_notes_acum:
                    if cred_note.journal_id.id == note['journal_id'][0]:
                        store = True
                        # ESTA CONDICION ES POR QUE MEDIANTE EL CODIGO SABE SI LA CUENTA ES DE DEVOLUCION, TODAS LAS QUE TIENEN ESTE CODIGO SON DE DEVOLUCION SI SE QUIERE MEJORAR ESTA CONDICION HARIA FALTA UN CAMPO QUE SEA UN BOOLEAN
                        # QUE DIGA: ¿Es cuenta de devolucion? y si esta activado la tome como tal para evitar esto
                        global_total = 0
                        global_iva = 0
                        global_contado = 0
                        global_credito = 0
                        global_venta_neta = 0
                        global_costo = 0
                        global_margin = 0
                        global_perc = 0
                        for line in cred_note.invoice_line_ids:
                            # ES BONIFICACION
                            if line.account_id.code not in ["402", "402.01.03", "402.01.04", "402.01.05", "402.01.06",
                                                            "402.03.01", "402.03.02", "402.03.03", "402.03.04",
                                                            "402.03.08", "402.03.09", "402.05", "402.05.01",
                                                            "402.05.02"]:
                                global_venta_neta += line.price_subtotal
                                if cred_note.payment_term_id.is_immediate == True:
                                    global_contado += line.price_total
                                else:
                                    global_credito += line.price_total
                                global_iva += line.price_total - line.price_subtotal
                                global_total += line.price_total
                                global_costo += line.purchase_price
                                global_margin += line.margin

                        for line in cred_note.invoice_line_ids:
                            if line.account_id.code not in ["402", "402.01.03", "402.01.04", "402.01.05", "402.01.06",
                                                            "402.03.01", "402.03.02", "402.03.03", "402.03.04",
                                                            "402.03.08", "402.03.09", "402.05", "402.05.01",
                                                            "402.05.02"]:
                                departament = cred_note.journal_id.tipo
                                if store == True:
                                    get_dep = rec.env['report.ventas_departamento_lines'].search(
                                        [('report_departament_id', '=', rec.id), ('departament', '=', departament),
                                         ('type', 'in', ['bonif_acum']), ('desglosado', 'in', [False])])
                                    if global_venta_neta == 0:
                                        global_perc = 0
                                    else:
                                        global_perc = (global_margin * 100) / global_venta_neta
                                    if len(get_dep) == 0:
                                        record = rec.env['report.ventas_departamento_lines'].create({
                                            'report_departament_id': rec.id,
                                            'type': 'bonif_acum',
                                            'departament': departament,
                                            'cost': global_costo,
                                            'sale_neto': global_venta_neta,
                                            'credit': global_credito,
                                            'debit': global_contado,
                                            'iva': global_iva,
                                            'total': global_total,
                                            'margin': global_margin,
                                            'perc': global_perc
                                        })
                                    else:
                                        global_perc_new = 0
                                        global_costo += get_dep.cost
                                        global_venta_neta += get_dep.sale_neto
                                        global_credito += get_dep.credit
                                        global_contado += get_dep.debit
                                        global_iva += get_dep.iva
                                        global_total += get_dep.total
                                        global_margin += get_dep.margin
                                        if global_venta_neta == 0:
                                            global_perc_new = 0
                                        else:
                                            global_perc_new = (global_margin * 100) / global_venta_neta

                                        record = get_dep.write({
                                            'report_departament_id': rec.id,
                                            'type': 'bonif_acum',
                                            'departament': departament,
                                            'cost': global_costo,
                                            'sale_neto': global_venta_neta,
                                            'credit': global_credito,
                                            'debit': global_contado,
                                            'iva': global_iva,
                                            'total': global_total,
                                            'margin': global_margin,
                                            'perc': global_perc_new
                                        })

            # --DEVOLUCIONES
            store = False
            total = 0
            iva = 0
            contado = 0
            credito = 0
            venta_neta = 0
            costo = 0
            margin = 0
            perc = 0
            for note in credit_notes_grouped:
                global_total = 0
                global_iva = 0
                global_contado = 0
                global_credito = 0
                global_venta_neta = 0
                global_costo = 0
                global_margin = 0
                global_perc = 0
                departament = False
                store = False

                for cred_note in credit_notes:
                    if cred_note.journal_id.id == note['journal_id'][0]:
                        store = True
                        # ESTA CONDICION ES POR QUE MEDIANTE EL CODIGO SABE SI LA CUENTA ES DE DEVOLUCION, TODAS LAS QUE TIENEN ESTE CODIGO SON DE DEVOLUCION SI SE QUIERE MEJORAR ESTA CONDICION HARIA FALTA UN CAMPO QUE SEA UN BOOLEAN
                        # QUE DIGA: ¿Es cuenta de devolucion? y si esta activado la tome como tal para evitar esto
                        global_total = 0
                        global_iva = 0
                        global_contado = 0
                        global_credito = 0
                        global_venta_neta = 0
                        global_costo = 0
                        global_margin = 0
                        global_perc = 0
                        for line in cred_note.invoice_line_ids:
                            # ES BONIFICACION
                            if line.account_id.code in ["402", "402.01.03", "402.01.04", "402.01.05", "402.01.06",
                                                        "402.03.01", "402.03.02", "402.03.03", "402.03.04", "402.03.08",
                                                        "402.03.09", "402.05", "402.05.01", "402.05.02"]:
                                global_venta_neta += line.price_subtotal
                                if cred_note.payment_term_id.is_immediate == True:
                                    global_contado += line.price_total
                                else:
                                    global_credito += line.price_total
                                global_iva += line.price_total - line.price_subtotal
                                global_total += line.price_total
                                global_costo += line.purchase_price
                                global_margin += line.margin
                                if global_venta_neta == 0:
                                    global_perc = 0
                                else:
                                    global_perc = (global_margin * 100) / global_venta_neta

                        for line in cred_note.invoice_line_ids:
                            if line.account_id.code in ["402", "402.01.03", "402.01.04", "402.01.05", "402.01.06",
                                                        "402.03.01", "402.03.02", "402.03.03", "402.03.04", "402.03.08",
                                                        "402.03.09", "402.05", "402.05.01", "402.05.02"]:
                                departament = cred_note.journal_id.tipo
                                get_dep = rec.env['report.ventas_departamento_lines'].search(
                                    [('report_departament_id', '=', rec.id), ('departament', '=', departament),
                                     ('type', 'in', ['return_day']), ('account_id', '=', line.account_id.id),
                                     ('desglosado', '=', True)])

                                if len(get_dep) == 0:
                                    if line.price_subtotal == 0:
                                        perc = 0
                                    else:
                                        perc = (line.margin * 100) / line.price_subtotal

                                    record = rec.env['report.ventas_departamento_lines'].create({
                                        'report_departament_id': rec.id,
                                        'type': 'return_day',
                                        'departament': departament,
                                        'cost': line.purchase_price,
                                        'account_id': line.account_id.id,
                                        'sale_neto': line.price_subtotal,
                                        'credit': line.price_total if cred_note.payment_term_id.is_immediate == False else 0,
                                        'debit': line.price_total if cred_note.payment_term_id.is_immediate == True else 0,
                                        'iva': line.price_total - line.price_subtotal,
                                        'subtotal': line.price_total,
                                        'margin': line.margin,
                                        'perc': perc,
                                        'desglosado': True
                                    })
                                else:
                                    subtotal = 0
                                    credito = get_dep.credit
                                    contado = get_dep.debit
                                    if cred_note.payment_term_id.is_immediate == True:
                                        contado += line.price_total
                                    else:
                                        credito += line.price_total
                                    cost = get_dep.cost + line.purchase_price
                                    taxes = get_dep.iva + (line.price_total - line.price_subtotal)
                                    subtotal = get_dep.subtotal + line.price_subtotal
                                    margin = get_dep.margin + line.margin
                                    sale_neto = get_dep.sale_neto + line.price_subtotal
                                    perc = (margin * 100) / sale_neto

                                    record = get_dep.write({
                                        'report_departament_id': rec.id,
                                        'type': 'return_day',
                                        'departament': departament,
                                        'cost': cost,
                                        'account_id': line.account_id.id,
                                        'sale_neto': sale_neto,
                                        'credit': credito,
                                        'debit': contado,
                                        'iva': taxes,
                                        'subtotal': subtotal,
                                        'margin': margin,
                                        'perc': perc,
                                        'desglosado': True
                                    })

                                if store == True:
                                    get_dep = rec.env['report.ventas_departamento_lines'].search(
                                        [('report_departament_id', '=', rec.id), ('departament', '=', departament),
                                         ('type', 'in', ['return_day']), ('desglosado', 'in', [False])])
                                    if len(get_dep) == 0:
                                        record = rec.env['report.ventas_departamento_lines'].create({
                                            'report_departament_id': rec.id,
                                            'type': 'return_day',
                                            'departament': departament,
                                            'cost': global_costo,
                                            'sale_neto': global_venta_neta,
                                            'credit': global_credito,
                                            'debit': global_contado,
                                            'iva': global_iva,
                                            'total': global_total,
                                            'margin': global_margin,
                                            'perc': global_perc
                                        })
                                    else:
                                        global_costo += get_dep.cost
                                        global_venta_neta += get_dep.sale_neto
                                        global_credito += get_dep.credit
                                        global_contado += get_dep.debit
                                        global_iva += get_dep.iva
                                        global_total += get_dep.total
                                        global_margin += get_dep.margin
                                        if global_venta_neta == 0:
                                            global_perc = 0
                                        else:
                                            global_perc = (margin * 100) / global_venta_neta

                                        record = get_dep.write({
                                            'report_departament_id': rec.id,
                                            'type': 'return_day',
                                            'departament': departament,
                                            'cost': global_costo,
                                            'sale_neto': global_venta_neta,
                                            'credit': global_credito,
                                            'debit': global_contado,
                                            'iva': global_iva,
                                            'total': global_total,
                                            'margin': global_margin,
                                            'perc': global_perc
                                        })

            # --DEVOLUCIONES ACUMULADAS
            store = False
            total = 0
            iva = 0
            contado = 0
            credito = 0
            venta_neta = 0
            costo = 0
            margin = 0
            perc = 0
            for note in credit_notes_acum_grouped:
                global_total = 0
                global_iva = 0
                global_contado = 0
                global_credito = 0
                global_venta_neta = 0
                global_costo = 0
                global_margin = 0
                global_perc = 0
                departament = False
                store = False

                for cred_note in credit_notes_acum:
                    if cred_note.journal_id.id == note['journal_id'][0]:
                        store = True
                        # ESTA CONDICION ES POR QUE MEDIANTE EL CODIGO SABE SI LA CUENTA ES DE DEVOLUCION, TODAS LAS QUE TIENEN ESTE CODIGO SON DE DEVOLUCION SI SE QUIERE MEJORAR ESTA CONDICION HARIA FALTA UN CAMPO QUE SEA UN BOOLEAN
                        # QUE DIGA: ¿Es cuenta de devolucion? y si esta activado la tome como tal para evitar esto
                        global_total = 0
                        global_iva = 0
                        global_contado = 0
                        global_credito = 0
                        global_venta_neta = 0
                        global_costo = 0
                        global_margin = 0
                        global_perc = 0
                        for line in cred_note.invoice_line_ids:
                            # ES BONIFICACION
                            if line.account_id.code in ["402", "402.01.03", "402.01.04", "402.01.05", "402.01.06",
                                                        "402.03.01", "402.03.02", "402.03.03", "402.03.04", "402.03.08",
                                                        "402.03.09", "402.05", "402.05.01", "402.05.02"]:
                                global_venta_neta += line.price_subtotal
                                if cred_note.payment_term_id.is_immediate == True:
                                    global_contado += line.price_total
                                else:
                                    global_credito += line.price_total
                                global_iva += line.price_total - line.price_subtotal
                                global_total += line.price_total
                                global_costo += line.purchase_price
                                global_margin += line.margin

                        for line in cred_note.invoice_line_ids:
                            if line.account_id.code in ["402", "402.01.03", "402.01.04", "402.01.05", "402.01.06",
                                                        "402.03.01", "402.03.02", "402.03.03", "402.03.04", "402.03.08",
                                                        "402.03.09", "402.05", "402.05.01", "402.05.02"]:
                                departament = cred_note.journal_id.tipo
                                if store == True:
                                    get_dep = rec.env['report.ventas_departamento_lines'].search(
                                        [('report_departament_id', '=', rec.id), ('departament', '=', departament),
                                         ('type', 'in', ['return_acum']), ('desglosado', 'in', [False])])
                                    if global_venta_neta == 0:
                                        global_perc = 0
                                    else:
                                        global_perc = (global_margin * 100) / global_venta_neta
                                    if len(get_dep) == 0:
                                        record = rec.env['report.ventas_departamento_lines'].create({
                                            'report_departament_id': rec.id,
                                            'type': 'return_acum',
                                            'departament': departament,
                                            'cost': global_costo,
                                            'sale_neto': global_venta_neta,
                                            'credit': global_credito,
                                            'debit': global_contado,
                                            'iva': global_iva,
                                            'total': global_total,
                                            'margin': global_margin,
                                            'perc': global_perc
                                        })
                                    else:
                                        global_perc_new = 0
                                        global_costo += get_dep.cost
                                        global_venta_neta += get_dep.sale_neto
                                        global_credito += get_dep.credit
                                        global_contado += get_dep.debit
                                        global_iva += get_dep.iva
                                        global_total += get_dep.total
                                        global_margin += get_dep.margin
                                        if global_venta_neta == 0:
                                            global_perc_new = 0
                                        else:
                                            global_perc_new = (global_margin * 100) / global_venta_neta

                                        record = get_dep.write({
                                            'report_departament_id': rec.id,
                                            'type': 'return_acum',
                                            'departament': departament,
                                            'cost': global_costo,
                                            'sale_neto': global_venta_neta,
                                            'credit': global_credito,
                                            'debit': global_contado,
                                            'iva': global_iva,
                                            'total': global_total,
                                            'margin': global_margin,
                                            'perc': global_perc_new
                                        })

        # EL COSTO SE DEJA IGUAL,IVA SE DEJA IGUAL
        # -- Ventas - (devoluciones/bonificaciones)
        venta_dia_lines = rec.env['report.ventas_departamento_lines'].search(
            [('report_departament_id', '=', rec.id), ('type', 'in', ['sale_day']), ('desglosado', 'in', [False])])
        for venta_line in venta_dia_lines:
            departament = venta_line.departament
            global_total = venta_line.total
            global_iva = venta_line.iva
            global_contado = venta_line.debit
            global_credito = venta_line.credit
            global_venta_neta = venta_line.sale_neto
            global_costo = venta_line.cost
            global_margin = venta_line.margin
            global_perc = venta_line.perc
            devolucion_dia_lines = rec.env['report.ventas_departamento_lines'].search(
                [('report_departament_id', '=', rec.id), ('departament', '=', departament),
                 ('type', 'in', ['return_day']), ('desglosado', 'in', [False])])
            for dev in devolucion_dia_lines:
                global_total -= dev.total
                global_contado -= dev.iva
                global_contado -= dev.debit
                global_credito -= dev.credit
                global_venta_neta -= dev.sale_neto
                global_margin -= dev.margin
            bonificacion_dia_lines = rec.env['report.ventas_departamento_lines'].search(
                [('report_departament_id', '=', rec.id), ('departament', '=', departament),
                 ('type', 'in', ['bonif_day']), ('desglosado', 'in', [False])])
            for bon in bonificacion_dia_lines:
                global_total -= bon.total
                global_contado -= bon.iva
                global_contado -= bon.debit
                global_credito -= bon.credit
                global_venta_neta -= bon.sale_neto
                global_margin -= bon.margin

            if global_venta_neta > 0:
                global_perc = 0
            else:
                global_perc = (global_margin * 100) / global_venta_neta

            record = rec.env['report.ventas_departamento_lines'].create({
                'report_departament_id': rec.id,
                'type': 'sale_bonif_return',
                'departament': departament,
                'cost': global_costo,
                'sale_neto': global_venta_neta,
                'credit': global_credito,
                'debit': global_contado,
                'iva': global_iva,
                'total': global_total,
                'margin': global_margin,
                'perc': global_perc
            })

        # -- Ventas - (devoluciones/bonificaciones) ACUMULADOS
        venta_dia_lines = rec.env['report.ventas_departamento_lines'].search(
            [('report_departament_id', '=', rec.id), ('type', 'in', ['sale_acum']), ('desglosado', 'in', [False])])
        for venta_line in venta_dia_lines:
            departament = venta_line.departament
            global_total = venta_line.total
            global_iva = venta_line.iva
            global_contado = venta_line.debit
            global_credito = venta_line.credit
            global_venta_neta = venta_line.sale_neto
            global_costo = venta_line.cost
            global_margin = venta_line.margin
            global_perc = venta_line.perc
            devolucion_dia_lines = rec.env['report.ventas_departamento_lines'].search(
                [('report_departament_id', '=', rec.id), ('departament', '=', departament),
                 ('type', 'in', ['return_acum']), ('desglosado', 'in', [False])])
            for dev in devolucion_dia_lines:
                global_total -= dev.total
                global_contado -= dev.iva
                global_contado -= dev.debit
                global_credito -= dev.credit
                global_venta_neta -= dev.sale_neto
                global_margin -= dev.margin
            bonificacion_dia_lines = rec.env['report.ventas_departamento_lines'].search(
                [('report_departament_id', '=', rec.id), ('departament', '=', departament),
                 ('type', 'in', ['bonif_acum']), ('desglosado', 'in', [False])])
            for bon in bonificacion_dia_lines:
                global_total -= bon.total
                global_contado -= bon.iva
                global_contado -= bon.debit
                global_credito -= bon.credit
                global_venta_neta -= bon.sale_neto
                global_margin -= bon.margin
            if global_venta_neta == 0:
                global_perc = 0
            else:
                global_perc = (global_margin * 100) / global_venta_neta
            record = rec.env['report.ventas_departamento_lines'].create({
                'report_departament_id': rec.id,
                'type': 'sale_bonif_return_acum',
                'departament': departament,
                'cost': global_costo,
                'sale_neto': global_venta_neta,
                'credit': global_credito,
                'debit': global_contado,
                'iva': global_iva,
                'total': global_total,
                'margin': global_margin,
                'perc': global_perc
            })

        # -- CREATES PARA DETERMINAR SI EL APARTADO SE MOSTRARA O NO EN BASE A SI TIENE REGISTROS EN EL XML
        sale_day_count = rec.env['report.ventas_departamento_lines'].search_count(
            [('report_departament_id', '=', rec.id), ('type', 'in', ['sale_day']), ('desglosado', 'in', [False])])
        record = rec.env['report.ventas_departamento_verificator_lines'].create({
            'report_departament_id': rec.id,
            'type': 'sale_day',
            'show_departament': True if sale_day_count > 0 else False
        })
        sale_acum_count = rec.env['report.ventas_departamento_lines'].search_count(
            [('report_departament_id', '=', rec.id), ('type', 'in', ['sale_acum']), ('desglosado', 'in', [False])])
        record = rec.env['report.ventas_departamento_verificator_lines'].create({
            'report_departament_id': rec.id,
            'type': 'sale_acum',
            'show_departament': True if sale_acum_count > 0 else False
        })
        bonif_day_count = rec.env['report.ventas_departamento_lines'].search_count(
            [('report_departament_id', '=', rec.id), ('type', 'in', ['bonif_day']), ('desglosado', 'in', [False])])
        record = rec.env['report.ventas_departamento_verificator_lines'].create({
            'report_departament_id': rec.id,
            'type': 'bonif_day',
            'show_departament': True if bonif_day_count > 0 else False
        })
        bonif_acum_count = rec.env['report.ventas_departamento_lines'].search_count(
            [('report_departament_id', '=', rec.id), ('type', 'in', ['bonif_acum']), ('desglosado', 'in', [False])])
        record = rec.env['report.ventas_departamento_verificator_lines'].create({
            'report_departament_id': rec.id,
            'type': 'bonif_acum',
            'show_departament': True if bonif_acum_count > 0 else False
        })
        return_day_count = rec.env['report.ventas_departamento_lines'].search_count(
            [('report_departament_id', '=', rec.id), ('type', 'in', ['return_day']), ('desglosado', 'in', [False])])
        record = rec.env['report.ventas_departamento_verificator_lines'].create({
            'report_departament_id': rec.id,
            'type': 'return_day',
            'show_departament': True if return_day_count > 0 else False
        })
        return_acum_count = rec.env['report.ventas_departamento_lines'].search_count(
            [('report_departament_id', '=', rec.id), ('type', 'in', ['return_acum']), ('desglosado', 'in', [False])])
        record = rec.env['report.ventas_departamento_verificator_lines'].create({
            'report_departament_id': rec.id,
            'type': 'return_acum',
            'show_departament': True if return_acum_count > 0 else False
        })
        sale_bonif_return_count = rec.env['report.ventas_departamento_lines'].search_count(
            [('report_departament_id', '=', rec.id), ('type', 'in', ['sale_bonif_return']),
             ('desglosado', 'in', [False])])
        record = rec.env['report.ventas_departamento_verificator_lines'].create({
            'report_departament_id': rec.id,
            'type': 'sale_bonif_return',
            'show_departament': True if sale_bonif_return_count > 0 else False
        })
        sale_bonif_return_acum_count = rec.env['report.ventas_departamento_lines'].search_count(
            [('report_departament_id', '=', rec.id), ('type', 'in', ['sale_bonif_return_acum']),
             ('desglosado', 'in', [False])])
        record = rec.env['report.ventas_departamento_verificator_lines'].create({
            'report_departament_id': rec.id,
            'type': 'sale_bonif_return_acum',
            'show_departament': True if sale_bonif_return_acum_count > 0 else False
        })
        return self.env.ref('ctt_dassa_reports.ctt_dassa_reports_ventas_departamento_report').with_context(
            from_transient_model=True).report_action(self)


class report_ventas_departamento_lines(models.TransientModel):
    _name = 'report.ventas_departamento_lines'
    _description = 'Lineas que muestran los datos a imprimir para el reporte de saldos'

    report_departament_id = fields.Many2one(
        'report.ventas_departamento',
        string="Reporte ventas por departamento"
    )
    type = fields.Selection(
        [
            ('sale_day', 'Venta del día'),
            ('sale_acum', 'Ventas acumuladas'),
            ('bonif_day', 'Bonificaciones del día'),
            ('bonif_acum', 'Bonificaciones acumuladas'),
            ('return_day', 'Devolcuiones del dia'),
            ('return_acum', 'Devolcuiones acumuladas'),
            ('sale_bonif_return', 'Ventas - bonificaciones/devoluciones'),
            ('sale_bonif_return_acum', 'Ventas bonificaciones/devoluciones acumuladas'),
        ],
        string="Tipo",
    )
    departament = fields.Selection(
        [
            ('refacciones', 'Refacciones'),
            ('taller', 'Taller'),
            ('maquinaria', 'Maquinaria'),
            ('gastos', 'Gastos'),
            ('no_asignado', 'not_asign')
        ],

        string="departamento",
    )
    # ---- CAMPOS PADA LOS DESGLOSES----
    account_id = fields.Many2one(
        'account.account',
        string="Cuenta contable"
    )
    subtotal = fields.Float(
        string="Subtotal"
    )
    desglosado = fields.Boolean(
        string="Es parte del desglose del total de departament?",
        default=False
    )
    tax_amount = fields.Float(
        string="Monto de impuestos"
    )
    cost = fields.Float(
        string="Costo"
    )
    sale_neto = fields.Float(
        string="Venta neta"
    )
    credit = fields.Float(
        string="Crédito"
    )
    debit = fields.Float(
        string="Contado"
    )
    iva = fields.Float(
        string="Iva"
    )
    total = fields.Float(
        string="Total"
    )
    margin = fields.Float(
        string="Margen"
    )
    perc = fields.Float(
        string="Porcentaje"
    )


class report_ventas_departamento_verificator_lines(models.TransientModel):
    _name = 'report.ventas_departamento_verificator_lines'
    _description = 'Lineas que dicen si se muestra o no un apartado'

    report_departament_id = fields.Many2one(
        'report.ventas_departamento',
        string="Reporte ventas por departamento"
    )
    type = fields.Selection(
        [
            ('sale_day', 'Venta del día'),
            ('sale_acum', 'Ventas acumuladas'),
            ('bonif_day', 'Bonificaciones del día'),
            ('bonif_acum', 'Bonificaciones acumuladas'),
            ('return_day', 'Devolcuiones del dia'),
            ('return_acum', 'Devolcuiones acumuladas'),
            ('sale_bonif_return', 'Ventas - bonificaciones/devoluciones'),
            ('sale_bonif_return_acum', 'Ventas bonificaciones/devoluciones acumuladas'),
        ],
        string="Tipo",
    )
    show_departament = fields.Boolean(
        string="Mostar departamento?",
        default=False
    )


class report_exist_ventas(models.TransientModel):
    _name = 'report.exist_ventas'
    _description = 'Wizard de impresión para reporte de existencias y ventas'
    _inherit = 'report.comun_data_product_selection'

    sucursal = fields.Many2one(
        'operating.unit',
        string="Sucursal",
        required=True
    )
    warehouse_ids = fields.Many2many(
        'stock.warehouse',
        string="Almacén",
        domain="[('operating_unit_id','=',sucursal)]",

    )
    product_ids = fields.Many2many(
        'product.product',
        string="Producto",
    )
    begin_month = fields.Selection(
        [
            ('1', 'Enero'),
            ('2', 'Febrero'),
            ('3', 'Marzo'),
            ('4', 'Abril'),
            ('5', 'Mayo'),
            ('6', 'Junio'),
            ('7', 'Julio'),
            ('8', 'Agosto'),
            ('9', 'Septiembre'),
            ('10', 'Octubre'),
            ('11', 'Noviembre'),
            ('12', 'Diciembre'),
        ],
        string="Mes",
        required=True,
    )
    begin_year = fields.Char(
        string="Año",
        required=True,
    )
    end_month = fields.Selection(
        [
            ('1', 'Enero'),
            ('2', 'Febrero'),
            ('3', 'Marzo'),
            ('4', 'Abril'),
            ('5', 'Mayo'),
            ('6', 'Junio'),
            ('7', 'Julio'),
            ('8', 'Agosto'),
            ('9', 'Septiembre'),
            ('10', 'Octubre'),
            ('11', 'Noviembre'),
            ('12', 'Diciembre'),
        ],
        string="Mes",
        required=True,
    )
    end_year = fields.Char(
        string="Año",
        required=True,
    )
    exedentes_ok = fields.Boolean(
        string="Exedentes"
    )
    no_exedentes_ok = fields.Boolean(
        string="No exedentes"
    )
    month_sales = fields.Selection(
        [
            ('1', '1'),
            ('2', '2'),
            ('3', '3'),
            ('4', '4'),
            ('5', '5'),
            ('6', '6'),
        ],
        default="1",
        required=True,
        string="Meses venta",
    )
    inc_solo_prod_saldo = fields.Boolean(
        string="Solo incluir productos con saldo"
    )
    agrupation = fields.Selection(
        [
            ('line', 'Línea'),
            ('brand', 'Marca'),
        ],
        default="line",
        string="Agrupación",
    )
    brand_ids = fields.Many2many(
        'x_marcas',
        string="Marcas"
    )
    count_months = fields.Integer(
        string="Cantidad de meses"
    )
    exist_vent_line = fields.One2many(
        'report.exist_ventas_lines',
        'exist_vent_id',
        string="Lineas"
    )

    def print_report(self):
        self.ensure_one()
        for rec in self:
            rec.exist_vent_line.unlink()
            begin_month = int(rec.begin_month)
            begin_year = int(rec.begin_year)
            end_month = int(rec.end_month)
            end_year = int(rec.end_year)
            dif = 0
            # raise ValidationError(rec.no_exedentes_ok)
            if end_year < begin_year:
                raise ValidationError("El año final del intervalo no puede ser mayor al año inicial del intervalo")
            if end_year == begin_year:
                if begin_month > end_month:
                    raise ValidationError("La fecha de inicio del intervalo es mayor que la final")
            while True:
                month = ""

                if begin_month > 12:
                    begin_year += 1
                    begin_month = 1
                    month = "Ene/" + str(begin_year)
                    record = rec.env['report.exist_ventas_lines'].create({
                        'exist_vent_id': rec.id,
                        'type': 'h',
                        'month_name': month
                    })
                else:
                    if begin_month == 1:
                        month = "Ene/" + str(begin_year)
                    if begin_month == 2:
                        month = "Feb/" + str(begin_year)
                    if begin_month == 3:
                        month = "Mar/" + str(begin_year)
                    if begin_month == 4:
                        month = "Abr/" + str(begin_year)
                    if begin_month == 5:
                        month = "May/" + str(begin_year)
                    if begin_month == 6:
                        month = "Jun/" + str(begin_year)
                    if begin_month == 7:
                        month = "Jul/" + str(begin_year)
                    if begin_month == 8:
                        month = "Ago/" + str(begin_year)
                    if begin_month == 9:
                        month = "Sep/" + str(begin_year)
                    if begin_month == 10:
                        month = "Oct/" + str(begin_year)
                    if begin_month == 11:
                        month = "Nov/" + str(begin_year)
                    if begin_month == 12:
                        month = "Dic/" + str(begin_year)

                    record = rec.env['report.exist_ventas_lines'].create({
                        'exist_vent_id': rec.id,
                        'type': 'h',
                        'month_name': month
                    })

                if begin_month == end_month and begin_year == end_year:
                    break
                begin_month += 1
                dif += 1
            count_headers = 0
            for exist in rec.exist_vent_line:
                if exist.type == 'h':
                    count_headers += 1
            if count_headers > 12:
                raise ValidationError("El intervalo de fechas supera el límite de 12 meses")
            self.count_months = count_headers
            # --------------------------------------------------------------------------------
            data_get = []
            product_ids = rec.env['product.product']
            if len(rec.product_ids) == 0:
                if rec.agrupation == "line":
                    if len(rec.category_ids) > 0:
                        for cat in rec.category_ids:
                            data_get.append(cat.id)
                    else:
                        consult_cat = rec.env['product.category'].search([])
                        for cat in consult_cat:
                            data_get.append(cat.id)
                    product_ids = rec.env['product.product'].search([('categ_id', 'in', data_get)])
                else:
                    if len(rec.brand_ids) > 0:
                        for brnd in rec.brand_ids:
                            data_get.append(brnd.id)
                    else:
                        consult_brand = rec.env['x_marcas'].search([])
                        for brnd in consult_brand:
                            data_get.append(brnd.id)
                    # product_ids = rec.env['product.product'].search([('x_studio_field_68yom', 'in', data_get)])
                    product_obj = rec.env['product.product']
                    if hasattr(product_obj,'x_studio_field_68yom'):
                        domain = [('x_studio_field_68yom', 'in', data_get)]
                        product_ids = rec.env['product.product'].search(domain)
            else:
                for prod in rec.product_ids:
                    data_get.append(prod.id)
                product_ids = rec.env['product.product'].search([('id', 'in', data_get)])

            all_locations = []
            all_warehouse_ids = []
            if len(rec.warehouse_ids) == 0:
                warehouse_ids = rec.env['stock.warehouse'].search([('operating_unit_id', '=', rec.sucursal.id)])
                for warehouse_id in warehouse_ids:
                    all_warehouse_ids.append(warehouse_id.id)
                    for location_id in warehouse_id.view_location_id:
                        all_locations.append(location_id.id)
                        for child_id in location_id.child_ids:
                            all_locations.append(child_id.id)
            else:
                for warehouse_id in rec.warehouse_ids:
                    all_warehouse_ids.append(warehouse_id.id)
                    for location_id in warehouse_id.view_location_id:
                        all_locations.append(location_id.id)
                        for child_id in location_id.child_ids:
                            all_locations.append(child_id.id)

            line_headers = rec.env['report.exist_ventas_lines'].search(
                [('exist_vent_id', '=', rec.id), ('type', 'in', ['h'])])
            for product_id in product_ids:
                header_count = 0
                headers_count_len = len(line_headers)
                cant_vend = 0
                cant_vend2 = 0
                cant_vend3 = 0
                cant_vend4 = 0
                cant_vend5 = 0
                cant_vend6 = 0
                cant_vend7 = 0
                cant_vend8 = 0
                cant_vend9 = 0
                cant_vend10 = 0
                cant_vend11 = 0
                cant_vend12 = 0
                exist_actual = 0
                reserved_quants = 0
                sale_total = 0
                frec = 0
                for line in line_headers:
                    month, year = str(line.month_name).split('/')
                    month_num = self.date_conversor(month)

                    last_days = [31, 30, 29, 28, 27]
                    date_max = False
                    for i in last_days:
                        try:
                            end = datetime(int(year), int(month_num), int(i), 23, 59, 59)
                        except ValueError:
                            continue
                        else:
                            date_max = end
                            break
                    date_min = datetime(int(year), int(month_num), 1, 0, 0, 0)

                    # HACER CONSULTA A LAS FACTURAS
                    # AQUI FALTA AGREGAR EL ALMACEN EN LA FACTURA PARA QUE CONTEMPLE LOS ALMACENES O ALMACEN EN ESTA CONSULTA
                    account_ids = rec.env['account.move.line'].search(
                        [('invoice_operating_unit_id', '=', rec.sucursal.id), ('invoice_date_invoice', '>=', date_min),
                         ('invoice_date_invoice', '<=', date_max),
                         ('invoice_state', 'in', ['open', 'in_payment', 'paid']),
                         ('invoice_type', 'in', ['out_invoice'])])

                    ultimo_mes = 0
                    actual_mes = 0

                    prim_vez_aparicion = False
                    for inv in account_ids:
                        if inv.product_id.id == product_id.id:
                            warehouse_inv = False
                            if inv.move_id.origin == False:
                                warehouse_inv = inv.invoice_operating_unit_id.warehouse_id.id
                            else:
                                record_sale = rec.env['sale.order'].search([('name', '=', inv.move_id.origin)], limit=1)
                                warehouse_inv = record_sale.warehouse_id.id

                            if warehouse_inv in all_warehouse_ids:
                                if header_count == 0:
                                    cant_vend += inv.quantity
                                elif header_count == 1:
                                    cant_vend2 += inv.quantity
                                elif header_count == 2:
                                    cant_vend3 += inv.quantity
                                elif header_count == 3:
                                    cant_vend4 += inv.quantity
                                elif header_count == 4:
                                    cant_vend5 += inv.quantity
                                elif header_count == 5:
                                    cant_vend6 += inv.quantity
                                elif header_count == 6:
                                    cant_vend7 += inv.quantity
                                elif header_count == 7:
                                    cant_vend8 += inv.quantity
                                elif header_count == 8:
                                    cant_vend9 += inv.quantity
                                elif header_count == 9:
                                    cant_vend10 += inv.quantity
                                elif header_count == 10:
                                    cant_vend11 += inv.quantity
                                elif header_count == 11:
                                    cant_vend12 += inv.quantity

                                sale_total += inv.quantity
                                if prim_vez_aparicion == False:
                                    frec += 1
                                    prim_vez_aparicion = True

                    if header_count == 0:
                        # TODOS LOS MOVES SE OBTIENEN YA QUE EL REPORTE MUESTRA LA EXISTENCIA ACTUAL POR ESO NO HAY FILTRO POR FECHA
                        move_ids = rec.env['stock.move'].search(
                            [('product_id', '=', product_id.id), ('location_dest_id', 'in', all_locations),
                             ('state', 'in', ['done'])])
                        move_ids += rec.env['stock.move'].search(
                            [('product_id', '=', product_id.id), ('location_id', 'in', all_locations),
                             ('state', 'in', ['done'])])

                        for move_id in move_ids:
                            if move_id.picking_code == "outgoing":
                                exist_actual -= move_id.product_uom_qty
                            elif move_id.picking_code == "incoming":
                                exist_actual += move_id.product_uom_qty
                            elif move_id.picking_code == False:
                                exist_actual += move_id.product_uom_qty
                            else:
                                if move_id.location_id.operating_unit_id.id != move_id.location_dest_id.operating_unit_id.id and move_id.location_id.operating_unit_id.id != False and move_id.location_dest_id.operating_unit_id.id != False:
                                    exist_actual -= move_id.product_uom_qty
                                elif move_id.location_dest_id.operating_unit_id.id == False:
                                    exist_actual -= move_id.product_uom_qty

                        # AQUI OBTENGO LAS CONSULTAS PARA OBTENER LOS RESERVADOS
                        move_ids = rec.env['stock.move'].search(
                            [('product_id', '=', product_id.id), ('location_dest_id', 'in', all_locations),
                             ('state', 'in', ['assigned'])])
                        move_ids += rec.env['stock.move'].search(
                            [('product_id', '=', product_id.id), ('location_id', 'in', all_locations),
                             ('state', 'in', ['assigned'])])
                        for move_id in move_ids:
                            if move_id.picking_code == "outgoing":
                                reserved_quants -= move_id.product_uom_qty
                            elif move_id.picking_code == "incoming":
                                reserved_quants += move_id.product_uom_qty
                            elif move_id.picking_code == False:
                                reserved_quants += move_id.product_uom_qty
                            else:
                                if move_id.location_id.operating_unit_id.id != move_id.location_dest_id.operating_unit_id.id and move_id.location_id.operating_unit_id.id != False and move_id.location_dest_id.operating_unit_id.id != False:
                                    reserved_quants -= move_id.product_uom_qty
                                elif move_id.location_dest_id.operating_unit_id.id == False:
                                    reserved_quants -= move_id.product_uom_qty

                    # CONSULTA A SALE.ORDER CON LAS FECHAS DETERMINADAS ESTO SE DEBE CAMBIAR POR FACTURA
                    save = False
                    if rec.inc_solo_prod_saldo == True:
                        if exist_actual * product_id.standard_price > 0:
                            save = True
                    else:
                        save = True

                    header_count += 1

                if save == True:
                    record = rec.env['report.exist_ventas_lines'].create({
                        'exist_vent_id': rec.id,
                        'type': 'd',
                        'product_id': product_id.id,
                        'product_id_name': product_id.name,
                        'exist_actual': exist_actual,
                        'cant_vend': cant_vend,
                        'cant_vend2': cant_vend2,
                        'cant_vend3': cant_vend3,
                        'cant_vend4': cant_vend4,
                        'cant_vend5': cant_vend5,
                        'cant_vend6': cant_vend6,
                        'cant_vend7': cant_vend7,
                        'cant_vend8': cant_vend8,
                        'cant_vend9': cant_vend9,
                        'cant_vend10': cant_vend10,
                        'cant_vend11': cant_vend11,
                        'cant_vend12': cant_vend12,
                        'exist_actual': exist_actual,
                        'frec': frec,
                        'header_count': headers_count_len,
                        'sale_prom': product_id.standard_price,
                        'saldo_i_al_actual': exist_actual * product_id.standard_price,
                        'sale_total': sale_total,
                        'reserved_quants': reserved_quants
                    })
                    # NOTAS
                    # las frecuencias (frec), el grupo, sale_total ojo este es el total pero de
                    # UNIDADES no de precio o costo, deben sumarse en el xml ya que se crea un
                    # registro por fecha de cada producto
        return self.env.ref('ctt_dassa_reports.ctt_dassa_reports_exist_ventas_report').with_context(
            from_transient_model=True).report_action(self)

    def date_conversor(self, month):
        month_num = 0
        if month == "Ene":
            month_num = 1
        if month == "Feb":
            month_num = 2
        if month == "Mar":
            month_num = 3
        if month == "Abr":
            month_num = 4
        if month == "May":
            month_num = 5
        if month == "Jun":
            month_num = 6
        if month == "Jul":
            month_num = 7
        if month == "Ago":
            month_num = 8
        if month == "Sep":
            month_num = 9
        if month == "Oct":
            month_num = 10
        if month == "Nov":
            month_num = 11
        if month == "Dic":
            month_num = 12
        return month_num


class report_exist_ventas(models.TransientModel):
    _name = 'report.exist_ventas_lines'

    exist_vent_id = fields.Many2one(
        'report.exist_ventas',
        string="report vent exist"
    )
    type = fields.Selection(
        [
            ('h', 'Header'),
            ('d', 'Dato'),

        ],
        string="Tipo de registro",
    )
    product_id = fields.Many2one(
        'product.product',
        string="Producto"
    )
    product_id_name = fields.Char(
        'Nombre del producto'
    )
    month_name = fields.Char(
        string="Mes"
    )
    cant_vend = fields.Float(
        string="Cantidad vendida para el mes1"
    )
    cant_vend2 = fields.Float(
        string="Cantidad vendida para el mes2"
    )
    cant_vend3 = fields.Float(
        string="Cantidad vendida para el mes3"
    )
    cant_vend4 = fields.Float(
        string="Cantidad vendida para el mes4"
    )
    cant_vend5 = fields.Float(
        string="Cantidad vendida para el mes5"
    )
    cant_vend6 = fields.Float(
        string="Cantidad vendida para el mes6"
    )
    cant_vend7 = fields.Float(
        string="Cantidad vendida para el mes7"
    )
    cant_vend8 = fields.Float(
        string="Cantidad vendida para el mes8"
    )
    cant_vend9 = fields.Float(
        string="Cantidad vendida para el mes9"
    )
    cant_vend10 = fields.Float(
        string="Cantidad vendida para el mes10"
    )
    cant_vend11 = fields.Float(
        string="Cantidad vendida para el mes11"
    )
    cant_vend12 = fields.Float(
        string="Cantidad vendida para el mes12"
    )
    exist_actual = fields.Float(
        string="Existencia Actual"
    )
    frec = fields.Float(
        string="Frecuencia"
    )
    saldo_i_al_mes = fields.Float(
        string="saldo_i_al_mes"
    )
    saldo_i_al_actual = fields.Float(
        string="saldo_i_al_actual"
    )
    sale_prom = fields.Float(
        string="Venta promedio"
    )
    sale_total = fields.Float(
        string="Ventas totales"
    )
    reserved_quants = fields.Float(
        string="Cantidades reservadas"
    )
    header_count = fields.Integer(
        string="Conteo de headers"
    )


class account_invoice_line_inherit(models.Model):
    _inherit = "account.move.line"

    invoice_operating_unit_id = fields.Many2one(
        'operating.unit',
        related="move_id.operating_unit_id",
        store=True
    )
    invoice_date_invoice = fields.Date(
        related="move_id.invoice_date",
        string="Date",
        store=True
    )
    invoice_state = fields.Selection(
        related="move_id.state",
        string="Seleccion",
        store=True
    )
    invoice_type = fields.Selection(
        related="move_id.move_type",
        string="Tipo",
        store=True
    )
