from odoo import models
import logging

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        for move in self:
            productos = move.invoice_line_ids.mapped('product_id.product_tmpl_id')
            if any(producto.limpiar_lineas_factura for producto in productos):
                _logger.info("Limpieza de 'name' en invoice lines de factura %s antes de confirmar.", move.id)
                for line in move.invoice_line_ids:
                    line.name = ''
        return super().action_post()
