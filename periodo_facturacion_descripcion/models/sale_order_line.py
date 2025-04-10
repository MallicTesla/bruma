from odoo import models
import logging
_logger = logging.getLogger(__name__)

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _prepare_invoice_line(self, **kwargs):
        res = super()._prepare_invoice_line(**kwargs)
        _logger.info("Limpieza de 'name' en invoice line en _prepare_invoice_line (sale order line %s)", self.id)
        # Se elimina el nombre del producto dejando el campo en blanco
        res['name'] = ''
        return res


