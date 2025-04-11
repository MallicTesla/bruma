from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    limpiar_lineas_factura = fields.Boolean(
        string='Limpiar líneas de factura al confirmar',
        help='Si está activo, se limpiará el nombre de las líneas de factura al confirmar la factura.'
    )
