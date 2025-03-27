from odoo import models, fields, api

class SaleSubscription(models.Model):
    _inherit = 'sale.order'

    incluir_temporalidad = fields.Boolean(string="Incluir temporalidad en notas")

    @api.onchange('incluir_temporalidad', 'sale_order_template_id', 'plan_id')
    def _onchange_incluir_temporalidad(self):
        """Si el checkbox está marcado, actualiza el campo de notas con la concatenación de
            Nombre de la Plantilla de cotización y Plan recurrente.
        """
        if self.incluir_temporalidad:
            plantilla = self.sale_order_template_id.name or ''
            plan = self.plan_id.name or ''
            temporalidad = f"{plantilla} - {plan}"
            self.note = temporalidad
        else:
            # Si se desmarca el checkbox, se limpia el campo de notas (o puedes dejarlo sin modificar)
            self.note = ''



