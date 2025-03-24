# -*- coding: utf-8 -*-
# from odoo import http


# class L10nUyDireccionPorDefecto(http.Controller):
#     @http.route('/l10n_uy_direccion_por_defecto/l10n_uy_direccion_por_defecto', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/l10n_uy_direccion_por_defecto/l10n_uy_direccion_por_defecto/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('l10n_uy_direccion_por_defecto.listing', {
#             'root': '/l10n_uy_direccion_por_defecto/l10n_uy_direccion_por_defecto',
#             'objects': http.request.env['l10n_uy_direccion_por_defecto.l10n_uy_direccion_por_defecto'].search([]),
#         })

#     @http.route('/l10n_uy_direccion_por_defecto/l10n_uy_direccion_por_defecto/objects/<model("l10n_uy_direccion_por_defecto.l10n_uy_direccion_por_defecto"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('l10n_uy_direccion_por_defecto.object', {
#             'object': obj
#         })

