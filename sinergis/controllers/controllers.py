# -*- coding: utf-8 -*-
# from odoo import http


# class Sinergis(http.Controller):
#     @http.route('/sinergis/sinergis', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sinergis/sinergis/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('sinergis.listing', {
#             'root': '/sinergis/sinergis',
#             'objects': http.request.env['sinergis.sinergis'].search([]),
#         })

#     @http.route('/sinergis/sinergis/objects/<model("sinergis.sinergis"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sinergis.object', {
#             'object': obj
#         })
