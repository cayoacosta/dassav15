# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare

# mapping invoice type to refund type
TYPE2REFUND = {
    'out_invoice': 'out_refund',  # Customer Invoice
    'in_invoice': 'in_refund',  # Vendor Bill
    'out_refund': 'out_invoice',  # Customer Credit Note
    'in_refund': 'in_invoice',  # Vendor Credit Note
}


class AccountInvoice(models.Model):
    _inherit = ['account.move']

    reference = fields.Char(string='Payment Ref.',
                            copy=False,
                            readonly=True,
                            states={'draft': [('readonly', False)]},
                            help='The payment communication that will be automatically populated once the invoice '
                                 'validation. You can also write a free communication.')
    user_id = fields.Many2one('res.users',
                              string='Salesperson',
                              track_visibility='onchange',
                              readonly=True,
                              states={'draft': [('readonly', False)]},
                              default=lambda self: self.env.user,
                              copy=False,
                              domain=[('groups_id.name', 'ilike', 'interno')])

    def _get_default_usage(self):
        if self._context.get('type') and self._context.get('type') in 'out_refund':
            return 'G02'
        else:
            if self._context.get('type') and self._context.get('type') \
                    in 'out_invoice' and self._context.get('active_id'):
                return 'G02'
            else:
                return 'P01'

    l10n_mx_edi_usage = fields.Selection([
        ('G01', 'Acquisition of merchandise'),
        ('G02', 'Returns, discounts or bonuses'),
        ('G03', 'General expenses'),
        ('I01', 'Constructions'),
        ('I02', 'Office furniture and equipment investment'),
        ('I03', 'Transportation equipment'),
        ('I04', 'Computer equipment and accessories'),
        ('I05', 'Dices, dies, molds, matrices and tooling'),
        ('I06', 'Telephone communications'),
        ('I07', 'Satellite communications'),
        ('I08', 'Other machinery and equipment'),
        ('D01', 'Medical, dental and hospital expenses.'),
        ('D02', 'Medical expenses for disability'),
        ('D03', 'Funeral expenses'),
        ('D04', 'Donations'),
        ('D05', 'Real interest effectively paid for mortgage loans (room house)'),
        ('D06', 'Voluntary contributions to SAR'),
        ('D07', 'Medical insurance premiums'),
        ('D08', 'Mandatory School Transportation Expenses'),
        ('D09', 'Deposits in savings accounts, premiums based on pension plans.'),
        ('D10', 'Payments for educational services (Colegiatura)'),
        ('P01', 'To define'), ], 'Usage',
        default=_get_default_usage,
        help='Used in CFDI 3.3 to express the key to the usage that will '
             'gives the receiver to this invoice. This value is defined by the '
             'customer. \nNote: It is not cause for cancellation if the key set is '
             'not the usage that will give the receiver of the document.')
    l10n_mx_edi_payment_method_id = fields.Many2one('l10n_mx_edi.payment.method',
                                                    string='Payment Way',
                                                    readonly=True,
                                                    states={'draft': [('readonly', False)]},
                                                    help='Indicates the way the invoice was/will be paid, where the '
                                                         'options could be: Cash, Nominal Check, Credit Card, '
                                                         'etc. Leave empty '
                                                         'if unknown and the XML will show "Unidentified".',
                                                    default=lambda self: self.env.ref('l10n_mx_edi.payment_method_15',
                                                                                      raise_if_not_found=False)
                                                    if self._context.get('type') and self._context.get(
                                                        'type') in 'out_invoice' and
                                                       self._context.get('active_id') or
                                                       self._context.get('type') and self._context.get(
                                                        'type') in 'out_refund'
                                                    else self.env.ref('l10n_mx_edi.payment_method_otros'))
    payment_term_id = fields.Many2one('account.payment.term',
                                      string='Payment Terms',
                                      oldname='payment_term',
                                      readonly=True,
                                      states={'draft': [('readonly', False)]},
                                      help="If you use payment terms, the due date will be computed automatically at "
                                           "the generation "
                                           "of accounting entries. If you keep the payment terms and the due date "
                                           "empty, it means direct payment. "
                                           "The payment terms may compute several due dates, for example 50% now, "
                                           "50% in one month.",
                                      default=lambda self: self.env.ref('account.account_payment_term_immediate',
                                                                        raise_if_not_found=False)
                                      if self._context.get('type') and self._context.get('type') in 'out_invoice' and
                                         self._context.get('active_id') or
                                         self._context.get('type') and self._context.get('type') in 'out_refund'
                                      else False)

    def action_invoice_open(self):
        # lots of duplicate calls to action_invoice_open, so we remove those already open
        to_open_invoices = self.filtered(lambda inv: inv.state != 'open')
        if to_open_invoices.filtered(lambda inv: not inv.partner_id):
            raise UserError(_("The field Vendor is required, please complete it to validate the Vendor Bill."))
        if to_open_invoices.filtered(lambda inv: inv.state != 'draft'):
            raise UserError(_("Invoice must be in draft state in order to validate it."))
        if to_open_invoices.filtered(
                lambda inv: float_compare(inv.amount_total, 0.0, precision_rounding=inv.currency_id.rounding) == -1):
            raise UserError(
                _("You cannot validate an invoice with a negative total amount. You should create a credit note "
                  "instead."))
        if to_open_invoices.filtered(lambda inv: not inv.account_id):
            raise UserError(
                _('No account was found to create the invoice, be sure you have installed a chart of account.'))
        # Validaciones para facturas de clientes
        if to_open_invoices.filtered(lambda inv: inv.type not in ['in_invoice', 'in_refund']):
            # Si es de contado la forma de pago no puede ser "Por definir"
            if to_open_invoices.filtered(
                    lambda inv: inv.l10n_mx_edi_payment_method_id.display_name == 'Por definir' and inv.payment_term_id.is_immediate):
                raise UserError(_('La forma de pago no puede ser "Por definir"'))
            # Si el cliente no trae RFC no se debe facturar
            if to_open_invoices.filtered(lambda inv: not inv.partner_id.vat):
                raise UserError(_('El cliente no cuenta con un RFC'))
            # No facturar sin termino de pago
            if to_open_invoices.filtered(lambda inv: not inv.payment_term_id):
                raise UserError(_('Favor de verificar el termino de pago'))
            # Si el cliente es público en general no se puede facturar de crédito
            if to_open_invoices.filtered(
                    lambda inv: not inv.tipo == 'maquinaria' and not inv.payment_term_id.is_immediate and 'XAXX010101000' in inv.partner_id.vat):
                raise UserError(_('No se puede vender a publico en general de crédito'))
            # No olvidar registrar la serie del artículo de venta de maquinaria
            if to_open_invoices.filtered(lambda inv: inv.tipo == 'maquinaria'):
                for invLines in to_open_invoices.invoice_line_ids:
                    if invLines.product_id.type != 'service' and invLines.product_id.tracking == 'serial' \
                            and not invLines.serie_id:
                        raise UserError(_('Revisar el numero de serie del producto'))

        to_open_invoices.action_date_assign()
        to_open_invoices.action_move_create()

        return to_open_invoices.invoice_validate()

    @api.model
    def _prepare_refund(self, invoice, date_invoice=None, date=None, description=None, journal_id=None):
        """ Prepare the dict of values to create the new credit note from the invoice.
            This method may be overridden to implement custom
            credit note generation (making sure to call super() to establish
            a clean extension chain).

            :param record invoice: invoice as credit note
            :param string date_invoice: credit note creation date from the wizard
            :param integer date: force date from the wizard
            :param string description: description of the credit note from the wizard
            :param integer journal_id: account. Journal from the wizard
            :return: dict of value to create() the credit note
        """
        values = {}
        for field in self._get_refund_copy_fields():
            if invoice._fields[field].type == 'many2one':
                values[field] = invoice[field].id
            else:
                values[field] = invoice[field] or False

        values['invoice_line_ids'] = self._refund_cleanup_lines(invoice.invoice_line_ids)

        tax_lines = invoice.tax_line_ids
        taxes_to_change = {
            line.tax_id.id: line.tax_id.refund_account_id.id
            for line in tax_lines.filtered(lambda l: l.tax_id.refund_account_id != l.tax_id.account_id)
        }
        cleaned_tax_lines = self._refund_cleanup_lines(tax_lines)
        values['tax_line_ids'] = self._refund_tax_lines_account_change(cleaned_tax_lines, taxes_to_change)

        if journal_id:
            journal = self.env['account.journal'].browse(journal_id)
        elif invoice['type'] == 'in_invoice':
            journal = self.env['account.journal'].search([('type', '=', 'purchase')], limit=1)
        else:
            journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)
        values['journal_id'] = journal.id

        values['type'] = TYPE2REFUND[invoice['type']]
        values['date_invoice'] = date_invoice or fields.Date.context_today(invoice)
        values['date_due'] = values['date_invoice']
        values['state'] = 'draft'
        values['number'] = False
        values['origin'] = invoice.number
        if values['type'] == 'out_refund' and self._context.get('active_id') or values['type'] == 'out_refund':
            values['payment_term_id'] = 1
            if invoice.l10n_mx_edi_cfdi_uuid:
                values['l10n_mx_edi_origin'] = '01|' + invoice.l10n_mx_edi_cfdi_uuid
            else:
                values['l10n_mx_edi_origin'] = '01|UUID'
        else:
            values['payment_term_id'] = False
        values['refund_invoice_id'] = invoice.id

        if values['type'] == 'in_refund':
            partner_bank_result = self._get_partner_bank_id(values['company_id'])
            if partner_bank_result:
                values['partner_bank_id'] = partner_bank_result.id

        if date:
            values['date'] = date
        if description:
            values['name'] = description
        return values
