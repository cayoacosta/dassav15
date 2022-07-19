# -*- coding: utf-8 -*-
from odoo import http

# class AccountCustomization(http.Controller):
#     @http.route('/account_customization/account_customization/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/account_customization/account_customization/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('account_customization.listing', {
#             'root': '/account_customization/account_customization',
#             'objects': http.request.env['account_customization.account_customization'].search([]),
#         })

#     @http.route('/account_customization/account_customization/objects/<model("account_customization.account_customization"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('account_customization.object', {
#             'object': obj
#         })