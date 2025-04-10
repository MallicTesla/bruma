from odoo import models
import logging

_logger = logging.getLogger(__name__)

def remove_subscription_period(text):
    """
    Función similar que remueve la parte del periodo del campo 'name'.
    """
    if text:
        for keyword in ["Periodo:", "Plazo:"]:
            if keyword in text:
                text = text.split(keyword)[0].strip()
                break
    return text

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        for move in self:
            # Mostramos la definición de los campos del registro (metadatos)
            fields_info = move.fields_get()
            _logger.info("000000000000 Definición de campos de move %s: %s", move.id, fields_info)
            
            # Mostramos los valores actuales de los campos
            move_values = move.read()[0]
            _logger.info("1111111111111 Valores de move %s: %s", move.id, move_values)

            # (Aquí iría el código de limpieza o cualquier otra modificación)
            for line in move.invoice_line_ids:
                # Ejemplo: eliminamos la parte del periodo del campo 'name'
                # Imaginamos que ya tenés una función remove_subscription_period definida.
                line.name = remove_subscription_period(line.name)
                _logger.info("222222222222222 Línea limpia: %s", line.name)
        
        return super(AccountMove, self).action_post()

