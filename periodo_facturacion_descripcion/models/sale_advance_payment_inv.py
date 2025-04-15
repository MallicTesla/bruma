import logging
from odoo import models

_logger = logging.getLogger(__name__)

class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    def create_invoices(self):
        _logger.info("000000000000 Custom override of create_invoices called")
        res = super(SaleAdvancePaymentInv, self).create_invoices()
        
        # Si el resultado no es del tipo esperado, se retorna sin modificaciones.
        if isinstance(res, str):
            _logger.info("1111111111111 El resultado de create_invoices es un string, sin modificaciones.")
            return res
        
        invoices = None
        # Caso en que se retorna un diccionario de acción con 'res_id'
        if isinstance(res, dict) and 'res_id' in res:
            invoices = self.env['account.move'].browse(res['res_id'])
        # Si es un recordset directo o una lista/tupla de recordsets.
        elif hasattr(res, 'invoice_line_ids'):
            invoices = res
        elif isinstance(res, (list, tuple)) and res and hasattr(res[0], 'invoice_line_ids'):
            invoices = res
        
        if invoices:
            for inv in invoices:
                for line in inv.invoice_line_ids:
                    # Se verifica que la línea de factura tenga relacionada alguna línea de venta
                    if line.sale_line_ids:
                        sale_line = line.sale_line_ids[0]
                        # Se obtiene el plan asociado en la orden de venta
                        plan = sale_line.order_id.plan_id
                        # Si existe el plan y está activado el checkbox, se reestablece la descripción
                        if plan and getattr(plan, 'usar_descripcion_cotizacion', False):
                            original_description = sale_line.name or ''
                            _logger.info("22222222222 Resetting invoice line description: SaleOrderLine id: %s", sale_line.id)
                            line.write({'name': original_description})
        else:
            _logger.info("3333333333333333 No se pudo determinar un recordset de facturas a partir del resultado de create_invoices.")
        
        return res

