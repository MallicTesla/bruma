from odoo import models
import logging
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        # Antes de confirmar (publicar) la factura, se limpia el nombre de las líneas
        for move in self:
            _logger.info("Limpieza de 'name' en invoice lines de factura %s antes de confirmar.", move.id)
            for line in move.invoice_line_ids:
                line.name = ''
        return super(AccountMove, self).action_post()
