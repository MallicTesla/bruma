# -*- coding: utf-8 -*-
from odoo import models, fields, api

class SaleSubscriptionPlan(models.Model):
    _inherit = 'sale.subscription.plan'
    
    incluir_periodo_facturacion = fields.Boolean(
        string="Incluir período de facturación en descripción",
        help="Si está activo, se incluirá en la descripción de la suscripción el nombre de la Plantilla de cotización y el Plan recurrente."
    )

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    @api.model
    def create(self, vals):
        order = super(SaleOrder, self).create(vals)
        order._actualizar_descripcion_periodo_facturacion()

        return order

    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        self._actualizar_descripcion_periodo_facturacion()

        return res

    def _actualizar_descripcion_periodo_facturacion(self):
        for order in self:
            # Se actualiza la descripción si existe un plan y este tiene activo el booleano
            if order.plan_id and order.plan_id.incluir_periodo_facturacion:
                # Suponemos que la orden tiene un campo relacionado a la Plantilla de cotización,
                # por ejemplo, 'plantilla_cotizacion_id' (many2one a sale.order.template)
                if order.plantilla_cotizacion_id:
                    nuevo_texto = "{} - {}".format(order.plantilla_cotizacion_id.name, order.plan_id.name)
                    # Asumimos que el campo de Notas o Descripción es 'note'
                    order.note = nuevo_texto

