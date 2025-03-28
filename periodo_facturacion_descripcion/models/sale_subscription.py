from odoo import models, fields, api
import logging
import re

_logger = logging.getLogger(__name__)

class SaleSubscription(models.Model):
    _inherit = 'sale.order'

    incluir_temporalidad = fields.Boolean(string="Incluir temporalidad en notas")

    # Marcadores para identificar nuestro bloque en internal_note
    FACT_MARKER_START = "<!-- FACTURACION_START -->"
    FACT_MARKER_END = "<!-- FACTURACION_END -->"

    def _update_internal_note_with_facturacion(self):
        """
        Actualiza el campo internal_note conservando el contenido manual,
        y añadiendo (o removiendo) la información de facturación en un bloque marcado.
        """
        # Obtenemos la nota actual; si es None, se convierte en cadena vacía
        current_note = self.internal_note or ""
        # Eliminamos cualquier bloque previamente agregado con nuestros marcadores
        pattern = re.compile(
            re.escape(self.FACT_MARKER_START) + ".*?" + re.escape(self.FACT_MARKER_END),
            re.DOTALL
        )
        cleaned_note = pattern.sub("", current_note).strip()
        if self.incluir_temporalidad:
            plantilla = self.sale_order_template_id.name or ''
            plan = self.plan_id.name or ''
            concatenated = f"{plantilla} - {plan}"
            fact_block = f"{self.FACT_MARKER_START}{concatenated}{self.FACT_MARKER_END}"
            # Si hay texto manual, se concatena; de lo contrario, solo el bloque
            if cleaned_note:
                new_note = f"{cleaned_note}\n{fact_block}"
            else:
                new_note = fact_block
        else:
            new_note = cleaned_note
        return new_note

    @api.onchange('incluir_temporalidad', 'sale_order_template_id', 'plan_id')
    def _onchange_incluir_temporalidad(self):
        _logger.info(">>> Se llamó a _onchange_incluir_temporalidad")
        new_note = self._update_internal_note_with_facturacion()
        self.internal_note = new_note
        _logger.info(">>> Nota actualizada en onchange: %s", new_note)

    def write(self, vals):
        result = super(SaleSubscription, self).write(vals)
        # Si se modificó alguno de los campos de interés, actualizamos la nota
        fields_of_interest = {'incluir_temporalidad', 'sale_order_template_id', 'plan_id'}
        if any(f in vals for f in fields_of_interest):
            for rec in self:
                new_note = rec._update_internal_note_with_facturacion()
                # Usamos una bandera en el contexto para evitar recursión
                rec.with_context(skip_internal_note_update=True).write({'internal_note': new_note})
        return result

    @api.model
    def create(self, vals):
        rec = super(SaleSubscription, self).create(vals)
        new_note = rec._update_internal_note_with_facturacion()
        rec.with_context(skip_internal_note_update=True).write({'internal_note': new_note})
        return rec







