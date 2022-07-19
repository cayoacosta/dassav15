# -*- coding: utf-8 -*-
from odoo import http

# class StockCustomEnhancements(http.Controller):
#     @http.route('/stock_custom_enhancements/stock_custom_enhancements/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/stock_custom_enhancements/stock_custom_enhancements/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('stock_custom_enhancements.listing', {
#             'root': '/stock_custom_enhancements/stock_custom_enhancements',
#             'objects': http.request.env['stock_custom_enhancements.stock_custom_enhancements'].search([]),
#         })

#     @http.route('/stock_custom_enhancements/stock_custom_enhancements/objects/<model("stock_custom_enhancements.stock_custom_enhancements"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('stock_custom_enhancements.object', {
#             'object': obj
#         })