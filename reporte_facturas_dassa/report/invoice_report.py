# -*- encoding: utf-8 -*-

import time
from datetime import datetime
from dateutil import relativedelta
from odoo import models, api


# from odoo.report import report_sxw


class CantuInvoiceReport(models.AbstractModel):
    _name = 'report.reporte_facturas_dassa.report_invoice_report'

    def _get_report_values(self, docids, data=None):

        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_ids', []))

        return {
            'doc_ids': self.ids,
            'doc_model': model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'get_lines': self._get_lines,
            # 'get_sub_total': self.get_sub_total,
            # 'get_total': self.get_total,
            # 'get_taxes': self.get_taxes,
            # 'get_currency': self.get_currency,
        }

    def set_context(self, objects, data, ids, report_type=None):
        self.date_from = data['form'].get('date_from', time.strftime('%Y-%m-%d'))
        self.date_to = data['form'].get('date_to',
                                        str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[
                                        :10])
        return super(CantuInvoiceReport, self).set_context(objects, data, ids, report_type=report_type)

    def get_currency(self):
        return self.currency

    def get_sub_total(self):
        return self.sub_total

    def get_total(self):
        return self.total

    def get_taxes(self):
        return self.taxes

    def _get_lines(self, obj):
        invoice_obj = obj.env['account.move']
        invoice_ids = invoice_obj.search([('move_type', '=', 'out_invoice'),
                                          ('state', '!=', 'draft'),
                                          #       ('estado_factura', '!=', 'factura_cancelada'),
                                          ('invoice_date', '>=', obj.date_from),
                                          ('invoice_date', '<=', obj.date_to)], order='invoice_date asc')
        # print 'invoices: cantu_invoice_report ', invoice_ids
        # invoices = invoice_obj.browse(invoice_ids)
        sub_total = 0
        total = 0
        taxes = []
        taxes_dict = {}
        currency = None
        for inv in invoice_ids:
            currency = inv.currency_id
            if inv.state != 'cancel':
                sub_total += inv.amount_untaxed
                total += inv.amount_total
                for tax in inv.line_ids.tax_ids:
                    if tax.name in taxes_dict:
                        taxes_dict[tax.name] += tax.amount
                    else:
                        taxes_dict[tax.name] = tax.amount
        for tax in taxes_dict:
            taxes.append({'name': tax, 'amount': taxes_dict[tax]})
        return [invoice_ids, sub_total, total, taxes, currency]
