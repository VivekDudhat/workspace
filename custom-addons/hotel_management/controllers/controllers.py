# -*- coding: utf-8 -*-
# from odoo import http


# class HotelManagement(http.Controller):
#     @http.route('/hotel__management/hotel__management', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hotel__management/hotel__management/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('hotel__management.listing', {
#             'root': '/hotel__management/hotel__management',
#             'objects': http.request.env['hotel__management.hotel__management'].search([]),
#         })

#     @http.route('/hotel__management/hotel__management/objects/<model("hotel__management.hotel__management"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hotel__management.object', {
#             'object': obj
#         })

