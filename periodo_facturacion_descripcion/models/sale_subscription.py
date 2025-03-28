from odoo import models, fields, api
import re

class SuscripcionVenta(models.Model):
    _inherit = 'sale.order'

    # Campo booleano para decidir si incluir la temporalidad en las notas
    incluir_temporalidad = fields.Boolean(string="Incluir temporalidad en notas")

    # Marcadores para identificar nuestro bloque de facturación dentro de internal_note
    MARCADOR_FACTURACION_INICIO = "<!-- FACTURACION_START -->"
    MARCADOR_FACTURACION_FIN = "<!-- FACTURACION_END -->"

    def _actualizar_nota_interna_con_facturacion(self):
        """
        Actualiza el campo internal_note conservando el contenido manual,
        y añadiendo (o removiendo) la información de facturación en un bloque marcado.
        """
        # Obtenemos la nota actual; si es None, se convierte en cadena vacía
        nota_actual = self.internal_note or ""

        # Eliminamos cualquier bloque previamente agregado con nuestros marcadores de facturación
        patron = re.compile(
            re.escape(self.MARCADOR_FACTURACION_INICIO) + ".*?" + re.escape(self.MARCADOR_FACTURACION_FIN),
            re.DOTALL
        )
        nota_limpia = patron.sub("", nota_actual).strip()

        # Si se debe incluir la temporalidad, generamos el bloque de facturación
        if self.incluir_temporalidad:
            plantilla = self.sale_order_template_id.name or ''  # Nombre de la plantilla de la orden
            plan = self.plan_id.name or ''                      # Nombre del plan de suscripción
            concatenado = f"{plantilla} - {plan}"               # Concatenamos ambos para formar la descripción
            bloque_facturacion = f"{self.MARCADOR_FACTURACION_INICIO}{concatenado}{self.MARCADOR_FACTURACION_FIN}"
            
            # Si ya hay contenido en la nota, concatenamos el bloque de facturación al final
            if nota_limpia:
                nueva_nota = f"{nota_limpia}\n{bloque_facturacion}"

            else:
                nueva_nota = bloque_facturacion  # Si no hay contenido, solo se coloca el bloque

        else:
            nueva_nota = nota_limpia  # Si no se debe incluir la temporalidad, devolvemos solo la nota limpia

        return nueva_nota

    @api.onchange('incluir_temporalidad', 'sale_order_template_id', 'plan_id')
    def _onchange_incluir_temporalidad(self):
        """
        Se activa cuando cambia alguno de los campos relacionados con la temporalidad.
        Actualiza la nota interna con el nuevo valor de facturación si es necesario.
        """
        nueva_nota = self._actualizar_nota_interna_con_facturacion()
        self.internal_note = nueva_nota  # Actualizamos la nota interna con la nueva información

    def write(self, vals):
        """
        Sobrescribe el método write para actualizar la nota interna si se modifican los campos de interés.
        """
        resultado = super(SuscripcionVenta, self).write(vals)
        
        # Comprobamos si alguno de los campos de interés ha sido modificado
        campos_de_interes = {'incluir_temporalidad', 'sale_order_template_id', 'plan_id'}
        if any(f in vals for f in campos_de_interes):
            for rec in self:
                nueva_nota = rec._actualizar_nota_interna_con_facturacion()
                # Para evitar recursión al actualizar la nota
                rec.with_context(skip_internal_note_update=True).write({'internal_note': nueva_nota})
        
        return resultado

    @api.model
    def create(self, vals):
        """
        Sobrescribe el método create para actualizar la nota interna al crear un nuevo registro.
        """
        rec = super(SuscripcionVenta, self).create(vals)
        nueva_nota = rec._actualizar_nota_interna_con_facturacion()
        rec.with_context(skip_internal_note_update=True).write({'internal_note': nueva_nota})
        return rec
