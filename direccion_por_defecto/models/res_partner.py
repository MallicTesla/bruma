# -*- coding: utf-8 -*-
import logging

from odoo import models, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def load_dgi_data(self, xml_result=None):
        """
        Llamamos al método original; si falla por datos de domicilio faltantes,
        capturamos el AttributeError y ponemos 'Dirección no definida'.
        """
        try:
            return super(ResPartner, self).load_dgi_data(xml_result)
        except AttributeError as e:
            _logger.warning(
                "No se encontraron datos de domicilio en la respuesta DGI: %s", e
            )
            # Para cada registro en self, aseguramos valores por defecto
            for partner in self:
                partner.street = 'Dirección no definida'
                partner.street2 = 'Dirección no definida'
            return True

    @api.onchange('consulta_rut')
    def onchange_consulta_rut(self):
        """
        Si al consultar el RUT ocurre cualquier error (incluido el AttributeError anterior),
        capturamos y asignamos la dirección por defecto.
        """
        if self.consulta_rut:
            try:
                self._consultar_partner_ruc()
            except Exception as e:
                _logger.warning("Error al consultar RUT: %s", e)
                # Valor por defecto en ambos campos de dirección
                self.street = 'Dirección no definida'
                self.street2 = 'Dirección no definida'
                # Opcional: avisar al usuario
                # raise UserError('No fue posible completar la dirección; se asignó valor por defecto.')
