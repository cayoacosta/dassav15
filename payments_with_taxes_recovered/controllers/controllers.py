# -*- coding: utf-8 -*-
from odoo import http

# class Tecnika(http.Controller):
#     @http.route('/tecnika/tecnika/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tecnika/tecnika/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('tecnika.listing', {
#             'root': '/tecnika/tecnika',
#             'objects': http.request.env['tecnika.tecnika'].search([]),
#         })

#     @http.route('/tecnika/tecnika/objects/<model("tecnika.tecnika"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tecnika.object', {
#             'object': obj
#         })