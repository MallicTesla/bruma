# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class periodo_facturacion_descripcion(models.Model):
#     _name = 'periodo_facturacion_descripcion.periodo_facturacion_descripcion'
#     _description = 'periodo_facturacion_descripcion.periodo_facturacion_descripcion'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

