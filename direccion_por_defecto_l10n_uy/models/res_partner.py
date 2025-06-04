# -*- coding: utf-8 -*-
from odoo import models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _consultar_partner_ruc(self):
        """
        Llama primero al método SOAP original (super) y luego asegura que exista siempre
        un valor en street, evitando errores si no se obtuvo dirección.
        """
        # Ejecuta la consulta SOAP definida en l10n_uy_vat_query
        result = super(ResPartner, self)._consultar_partner_ruc()
        # Asegurar valor por defecto en street si está vacío
        for partner in self:
            if not partner.street:
                partner.street = 'Dirección no definida'
        return result
