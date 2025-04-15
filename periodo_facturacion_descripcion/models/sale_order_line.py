import logging
from odoo import models

_logger = logging.getLogger(__name__)

class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    def create_invoices(self):
        _logger.info("000000000000 Custom override of create_invoices called")
        res = super(SaleAdvancePaymentInv, self).create_invoices()
        
        # Si res es un string o no tiene la estructura esperada, se retorna sin modificaciones
        if isinstance(res, str):
            _logger.info("11111111111 Resultado de create_invoices es un string, sin modificaciones.")
            return res
        
        # Si res es un diccionario con 'res_id', asumimos que es la acción con un ID y buscamos el recordset
        invoices = None
        if isinstance(res, dict) and 'res_id' in res:
            invoices = self.env['account.move'].browse(res['res_id'])
        # Si res es un recordset directamente o una lista/tuple de recordsets, lo usamos
        elif hasattr(res, 'invoice_line_ids'):
            invoices = res
        elif isinstance(res, (list, tuple)) and res and hasattr(res[0], 'invoice_line_ids'):
            invoices = res
        
        if invoices:
            for inv in invoices:
                for line in inv.invoice_line_ids:
                    # Verificamos que exista la relación con la línea de venta
                    if line.sale_line_ids:
                        original_description = line.sale_line_ids[0].name or ''
                        _logger.info("22222222222 Resetting invoice line description: SaleOrderLine id: %s", line.sale_line_ids[0].id)
                        line.write({'name': original_description})
        else:
            _logger.info("333333333333333 No se pudo determinar un recordset de facturas a partir del resultado de create_invoices.")
        
        return res




