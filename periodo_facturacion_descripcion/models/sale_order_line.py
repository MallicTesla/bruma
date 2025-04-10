from odoo import models
import logging

_logger = logging.getLogger(__name__)

def remove_subscription_period(text):
    """
    Si en el texto aparece una indicación del periodo (ej. "Periodo:" o "Plazo:"),
    se elimina esa parte y todo lo que sigue.
    """
    if text:
        for keyword in ["Periodo:", "Plazo:"]:
            if keyword in text:
                # Se toma la parte anterior al keyword y se remueve espacios
                text = text.split(keyword)[0].strip()
                break
    return text

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _prepare_invoice_line(self, **kwargs):
        res = super()._prepare_invoice_line(**kwargs)
        _logger.info("Antes de limpiar 'name' en invoice line: %s", res.get('name', ''))
        # Se limpia solamente la parte que corresponde al periodo de suscripción
        res['name'] = remove_subscription_period(res.get('name', ''))
        _logger.info("Después de limpiar 'name': %s", res.get('name', ''))
        return res



