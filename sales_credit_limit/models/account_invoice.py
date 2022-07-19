# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError
from datetime import datetime

class AccountInvoice(models.Model):
    _inherit = 'account.move'