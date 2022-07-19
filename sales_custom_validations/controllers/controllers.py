# -*- coding: utf-8 -*-
from odoo import http

# class SalesCustomValidations(http.Controller):
#     @http.route('/sales_custom_validations/sales_custom_validations/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sales_custom_validations/sales_custom_validations/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sales_custom_validations.listing', {
#             'root': '/sales_custom_validations/sales_custom_validations',
#             'objects': http.request.env['sales_custom_validations.sales_custom_validations'].search([]),
#         })

#     @http.route('/sales_custom_validations/sales_custom_validations/objects/<model("sales_custom_validations.sales_custom_validations"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sales_custom_validations.object', {
#             'object': obj
#         })
