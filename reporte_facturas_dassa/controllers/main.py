# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import serialize_exception
from odoo.http import content_disposition

from xlsxwriter.workbook import Workbook
import csv
#from io import StringIO
import time
from datetime import datetime
from io import BytesIO

    
class BinaryFacturas(http.Controller):
    @http.route('/web/binary/download_xls', type='http', auth="public")
    @serialize_exception
    def download_xls(self,invoice_report_id, **kw):
        invoice_report = request.env['xls.invoice.report'].sudo().browse(int(invoice_report_id))
        invoice_ids = invoice_report.invoice_ids.split('-')
        invoice_ids = [int(s) for s in invoice_ids]
        Model = request.env['account.move']
        #cr, uid, context = request.cr, request.uid, request.context
        invoices = Model.browse(invoice_ids)
        timestamp = int(time.mktime(datetime.now().timetuple()))   
        csvfile = open('%s%s.csv' % ('/tmp/invoices_', timestamp), 'w')
        fieldnames = ['Folio', 'Cliente', 'Nombre', 'Costo', 'Subtotal', 'Impuestos', 'Contado','Credito', 'Margen', '% Margen']
        writer = csv.DictWriter(csvfile, quoting=csv.QUOTE_NONE, fieldnames=fieldnames)
        writer.writeheader()

        for inv in invoices:
            costo_de_ventas = sum(line.product_id.standard_price * line.quantity for line in inv.invoice_line_ids)
            utilidad = inv.amount_untaxed - costo_de_ventas
            writer.writerow({'Folio': inv.move_name.replace('INV','').replace('/','') or '',
                            'Cliente': inv.partner_id.ref or '',
                            'Nombre': inv.partner_id.name.replace(',','').replace('"','') or '', #.encode('ascii', 'ignore') or '',
                            'Costo':  round(costo_de_ventas,2),
                            'Subtotal' : round(inv.amount_untaxed,2),
                            'Impuestos' : round(inv.amount_tax,2),
                            'Contado' : inv.payment_term_id.name == 'Pago inmediato' and inv.amount_total or 0,
                            'Credito' : inv.payment_term_id.name != 'Pago inmediato' and inv.amount_total or 0,
                            'Margen' : round(utilidad,2),
                            '% Margen' : inv.amount_untaxed > 0 and round(utilidad / inv.amount_untaxed,2)*100 or 0,
                            })
               
        csvfile.close()   
        output = BytesIO() #StringIO()
        workbook = Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet()
        bold = workbook.add_format({'bold': True, 'border':   1,})
        border = workbook.add_format({'border':   1,})
        with open('%s%s.csv' % ('/tmp/invoices_', timestamp), 'rt') as f:
            reader = csv.reader(f)
            for r, row in enumerate(reader):
                for c, col in enumerate(row):
                    #print (r, c, col)
                    if r == 0:
                        worksheet.write(r, c, col, bold)
                    else:
                        worksheet.write(r, c, col, border)
                        # worksheet.set_column(c, c, len(col),formater)
        workbook.close()
        output.seek(0)	 
        binary = output.read()
            
        #res = Model.to_xml(cr, uid, context=context)
        if not binary:
            #print 'no binary'
            return request.not_found()
        else:
            filename = '%s%s.xls' % ('invoices_', timestamp)
            return request.make_response(binary,
                               [('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                                ('Pragma', 'public'), 
                                ('Expires', '0'),
                                ('Cache-Control', 'must-revalidate, post-check=0, pre-check=0'),
                                ('Cache-Control', 'private'),
                                ('Content-Length', len(binary)),
                                ('Content-Transfer-Encoding', 'binary'),
                                ('Content-Disposition', content_disposition(filename))])
        
