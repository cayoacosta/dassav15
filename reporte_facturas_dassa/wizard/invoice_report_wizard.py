# -*- coding: utf-8 -*-

from odoo import fields, models, api
from datetime import datetime, timedelta

class XlsInvoiceReport(models.Model):
    _name = "xls.invoice.report"
    _description = "Invoice Report"

    date_from = fields.Date(string='Periodo', required=True)
    date_to = fields.Date(string='Al', required=True)
    no_result = fields.Boolean(string='No Result', default=False)
    invoice_ids = fields.Char(string='Invoice IDs', readonly=True)
    
    
    def export_xls(self): 
        end_day = self.date_to + timedelta(hours=19)
        start_day = self.date_from + timedelta(hours=5)
        #print 'print_report: '
        invoice_ids = self.env['account.move'].search([
                                                             ('move_type', '=', 'out_invoice'),
                                                      #       ('state', '!=', 'cancel'),
                                                      #       ('estado_factura', '!=', 'factura_cancelada'),
                                                             ('invoice_date', '>=', start_day),
                                                             ('invoice_date', '<=', end_day)], order='invoice_date asc')
        #print 'invoices: cantu_invoice_report ', invoice_ids
        if not invoice_ids:
            self.write({'no_result': True})
            return {
                    "type": "ir.actions.do_nothing",
                }
            
        invs = '-'.join([str(i.id) for i in invoice_ids])
        #print invs
        self.write({'invoice_ids': invs})
        return {
                 'type' : 'ir.actions.act_url',
                 'url': '/web/binary/download_xls?invoice_report_id=%s'%(self.id),
                 'target': 'new',
                 }
        return True

    
    def print_report(self):    
        self.ensure_one()      
        datas =  {
                'ids': [],
                'model': 'account.move',
                'form': self.read()[0]
            }
        self = self.with_context({'active_model':self._name,'active_ids':self.ids})
        return self.env.ref('reporte_facturas_dassa.report_invoice_total').with_context({'active_model':self._name,'active_ids':self.ids}).report_action(self, data=datas)
