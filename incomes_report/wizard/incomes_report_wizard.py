# Copyright 2022, TECNIKA GLOBAL, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, fields, models
import textwrap


class IncomesReportWizard(models.TransientModel):
    _name = 'tecnika.incomes.report.wizard'
    _description = 'Wizard to create Incomes Report for daily operations'

    date_from = fields.Date(
        string='From', required=True,
        default=fields.Date.context_today)
    date_to = fields.Date(
        string='To', required=True,
        default=fields.Date.context_today)
    ou_ids = fields.Many2one('operating.unit', string='Operating Unit')
    report_type = fields.Selection(
        selection=[('0', 'By Document'), ('1', 'By Operation'), ],
        string="Report Type",
        help="Select By Document if you want Amount in one Column",
        default='0'
    )

    def create_report(self):

        rtypes = ['bydoc', '']
        rtype = rtypes[int(self.report_type)]
        title = 'Verificador de Ingresos'
        if self.report_type == '0':
            title += ' por Documento'
        sql, group_by = eval("self._get_sql{}()".format(rtype))
        model = 'tecnika.incomes.report{}'.format(rtype)
        self.env[model].search([]).unlink()
        self._cr.execute(sql)
        report_list = self._cr.dictfetchall()
        self.env[model].create(report_list)

        tree_view_id = self.env.ref(
            'incomes_report.tecnika_incomes_report{}_tree_view'.format(rtype)).id
        search_view_id = self.env.ref(
            'incomes_report.tecnika_incomes_report{}_search_view'.format(rtype)).id
        action = {
            'type': 'ir.actions.act_window',
            'views': [(tree_view_id, 'tree')],
            'view_id': tree_view_id,
            'view_mode': 'tree',
            'name': _(title),
            'search_view_id': search_view_id,
            'res_model': 'tecnika.incomes.report{}'.format(rtype),
            'context': {'group_by': group_by},
        }
        return action

    def _get_sql(self):

        ou_where = ''
        ou_where_payment = ''
        group_by = ['operating_unit_id', 'operation_type', 'date:day']
        if self.ou_ids:
            group_by = ['operation_type', 'date:day']
            ou_where = "and ai.operating_unit_id = {}".format(self.ou_ids.id)
            ou_where_payment = "and ap.operating_unit_id = {}".format(self.ou_ids.id)
        select_expedition_date = ''
        where_expedition_date = ''
        if 'l10n_mx_edi_expedition_date' in self.env['account.payment']._fields:
            select_expedition_date = 'ap.l10n_mx_edi_expedition_date "date",'
            where_expedition_date = "and ap.l10n_mx_edi_expedition_date between '%s' and '%s'"
        else:
            select_expedition_date = "null,"
            where_expedition_date = "and null"
        sql = '''
                    select ai.id invoice_id, null as payment_id, ai.reversed_entry_id, ai.partner_id,
                            ai.operating_unit_id, ai.journal_id,
                            case when apt.is_immediate then ai.amount_total else 0.00 end cash_amount,
                            case when apt.is_immediate then ai.amount_tax else 0.00 end cash_tax_amount,
                            case when apt.is_immediate is null or not apt.is_immediate then ai.amount_total else 0.00 end credit_amount,
                            case when apt.is_immediate is null or not apt.is_immediate then ai.amount_tax else 0.00 end credit_tax_amount,
                            ai.invoice_date "date", ai."move_type" operation_type
                    from account_move ai
                        join account_payment_term apt on (apt.id = ai.invoice_payment_term_id)
                    where ai."move_type" in ('out_invoice', 'out_refund') 
                        and ai.state not in ('cancel', 'draft')
                        and ai.invoice_date between '%s' and '%s' %s
                    union
                    select null invoice_id, ap.id as payment_id, null reversed_entry_id, 
                        ap.partner_id, ap.operating_unit_id, ap.journal_id, 
                        ap.cash_payment cash_amount, 
                        ap.cash_tax_paid cash_tax_amount,
                        case when ap.credit_payment + ap.cash_payment = 0 
                            then ap.amount else ap.credit_payment end credit_amount, 
                        ap.credit_tax_paid credit_tax_amount,
                        %s 'cash_payment' operation_type 
                    from account_payment ap
                        join account_journal aj on (aj.id = ap.journal_id)
                    where ap.payment_type = 'inbound' 
                        and ap.partner_type = 'customer'    
                        and ap.state = 'posted'
                        and aj."type" = 'cash'
                        %s %s
                    union
                    select null invoice_id, ap.id as payment_id, null reversed_entry_id, 
                        ap.partner_id, ap.operating_unit_id, ap.journal_id, 
                        ap.cash_payment cash_amount, 
                        ap.cash_tax_paid cash_tax_amount,
                        case when ap.credit_payment + ap.cash_payment = 0 
                            then ap.amount else ap.credit_payment end credit_amount, 
                        ap.credit_tax_paid credit_tax_amount,
                        %s 'credit_payment' operation_type 
                    from account_payment ap
                        join account_journal aj on (aj.id = ap.journal_id)
                    where ap.payment_type = 'inbound' 
                        and ap.partner_type = 'customer'    
                        and ap.state = 'posted'
                        and aj."type" = 'bank'
                        %s %s
                    order by operating_unit_id, operation_type, "date";
                ''' % (self.date_from, self.date_to, ou_where, select_expedition_date,
                       where_expedition_date, ou_where_payment, select_expedition_date,
                       where_expedition_date, ou_where_payment)
        return sql, group_by

    def _get_sqlbydoc(self):

        ou_where = ''
        ou_where_payment = ''
        group_by = ['operating_unit_id', 'doctype', 'date:day']
        select_expedition_date = ''
        where_expedition_date = ''
        if self.ou_ids:
            group_by = ['doctype', 'date:day']
            ou_where = "and ai.operating_unit_id = {}".format(self.ou_ids.id)
            ou_where_payment = "and ap.operating_unit_id = {}".format(self.ou_ids.id)
            if 'l10n_mx_edi_expedition_date' in self.env['account.payment']._fields:
                select_expedition_date = 'ap.l10n_mx_edi_expedition_date "date",'
                where_expedition_date = "and ap.l10n_mx_edi_expedition_date between '%s' and '%s' %s" % (
                self.date_from, self.date_to, ou_where_payment)

            else:
                select_expedition_date="null,"
                where_expedition_date="and null"
            """use the reversed_entry_id in query """
            # ai.move_id ==reversed_entry_id
        sql = """
                 select ai.id invoice_id, null::int4 as payment_id, ai.reversed_entry_id, ai.partner_id,
                         ai.operating_unit_id, ai.journal_id,
                         ai.amount_total, ai.amount_tax, ai.invoice_date "date", ai."move_type" operation_type, 
                         case when apt.is_immediate then 'Facturas Contado' else 'Facturas Crédito' end doctype
                 from account_move ai
                     join account_payment_term apt on (apt.id = ai.invoice_payment_term_id)
                 where ai."move_type" in ('out_invoice') 
                     and ai.state not in ('cancel', 'draft')
                     and ai.invoice_date between '%s' and  '%s' %s
                 union
                 select ai.id invoice_id, null::int4 as payment_id, ai.reversed_entry_id, ai.partner_id,
                         ai.operating_unit_id, ai.journal_id,
                         ai.amount_total, ai.amount_tax, ai.invoice_date "date", ai."move_type" operation_type, 
                         case when apt.is_immediate then 'NC Contado' else 'NC Crédito' end doctype
                 from account_move ai
                     join account_payment_term apt on (apt.id = ai.invoice_payment_term_id)
                 where ai."move_type" in ('out_refund') 
                     and ai.state not in ('cancel', 'draft')
                     and ai.invoice_date between '%s' and  '%s' %s
                 union
                 select null invoice_id, ap.id as payment_id, null reversed_entry_id, ap.partner_id, 
                     ap.operating_unit_id, ap.journal_id, 
                     ap.cash_payment amount_total, ap.cash_tax_paid amount_tax,
                  
                   %s  'credit_payment' operation_type,
                  
                     'Pagos de Contado' doctype
                 from account_payment ap
                     join account_journal aj on (aj.id = ap.journal_id)
                 where ap.payment_type = 'inbound' 
                     and ap.partner_type = 'customer' 	
                     and ap.state = 'posted'
                     and cash_payment > 0
                    
                   %s 
                 union
                 select null invoice_id, ap.id as payment_id, null move_id, ap.partner_id, 
                     ap.operating_unit_id, ap.journal_id, 
                     ap.credit_payment amount_total,  
                     ap.credit_tax_paid amount_tax,
                   
                    %s 'credit_payment' operation_type,
                     'Pagos de Crédito' doctype
                 from account_payment ap
                     join account_journal aj on (aj.id = ap.journal_id)
                 where ap.payment_type = 'inbound' 
                     and ap.partner_type = 'customer' 	
                     and ap.state = 'posted'
                     and ap.credit_payment  > 0 
                    
                   %s 
                 union
                 select null invoice_id, ap.id as payment_id, null move_id, ap.partner_id, 
                     ap.operating_unit_id, ap.journal_id, 
                     ap.amount amount_total, 
                     0.00 amount_tax,
                     
                    %s   'credit_payment' operation_type,
                     'Pagos sin Asignar' doctype
                 from account_payment ap
                     join account_journal aj on (aj.id = ap.journal_id)
                 where ap.payment_type = 'inbound' 
                     and ap.partner_type = 'customer'	
                     and ap.state = 'posted'
                     and (ap.cash_payment + ap.credit_payment = 0 )
                     and (ap.credit_payment  > 0  or (ap.cash_payment + ap.credit_payment = 0 ))
                    
                    %s 
                   
                              
         """ % (self.date_from, self.date_to, ou_where,
                self.date_from, self.date_to, ou_where,
                select_expedition_date,where_expedition_date, select_expedition_date,
                where_expedition_date, select_expedition_date, where_expedition_date)
        return sql, group_by


class StockMoveLine(models.Model):
    _inherit = "account.payment"
    state = fields.Selection(related='move_id.state', store=True)
