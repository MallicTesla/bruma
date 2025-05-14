# -*- coding: utf-8 -*-
import logging
import requests
import html
from xml.etree import ElementTree as ET
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    consulta_rut = fields.Boolean(string="Consultar RUT")
    xml_result = fields.Text(string="Última respuesta SOAP", readonly=True)

    def _format_rut(self, vat):
        """Formatea el RUT para eliminar guiones o puntos, y asegurar 12 dígitos."""
        clean = (vat or '').replace('-', '').replace('.', '')
        return clean.zfill(12)

    def _get_emp_code(self):
        """Devuelve EmpCod según ambiente o valor manual."""
        company = self.env.company
        if company.cfe_provider == 'datalogic':
            if company.einvoice_mode == 'testing':
                return company.company_code_test or ''
            if company.einvoice_mode == 'live':
                return company.company_code or ''
        return company.vat_query_emp_code or ''

    def _build_soap_envelope(self, rut):
        emp_code = self._get_emp_code()
        if not emp_code:
            raise UserError(_("No se ha encontrado 'EmpCod' para el servicio SOAP."))
        inner = (
            f'<ReceptorActEmpresarial xmlns="GFE_Client">'
            f'<EmpCod>{emp_code}</EmpCod>'
            f'<RUT>{rut}</RUT>'
            f'</ReceptorActEmpresarial>'
        )
        cdata = f"<![CDATA[{inner}]]>"
        xmlentrada = (
            '<XMLEntrada>'
                '<Datos>'
                    '<Dato><Valor>%s</Valor></Dato>'
                '</Datos>'
            '</XMLEntrada>' % cdata
        )
        # Usamos CONSULTARRECEPTORES (servicio aceptado por el endpoint)
        envelope = (
            '<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" '
                             'xmlns:gfe="GFE_Client">'
                '<soapenv:Header/>'
                '<soapenv:Body>'
                    '<gfe:WSExternoStandalone.CONSULTARRECEPTORES>'
                        f'<gfe:Xmlentrada>{xmlentrada}</gfe:Xmlentrada>'
                    '</gfe:WSExternoStandalone.CONSULTARRECEPTORES>'
                '</soapenv:Body>'
            '</soapenv:Envelope>'
        )
        _logger.info("[l10n_uy_vat_query] SOAP Envelope RUT %s: %s", rut, envelope)
        return envelope

    @api.onchange('consulta_rut')
    def _onchange_consulta_rut(self):
        if not self.consulta_rut or not self.vat:
            return
        rut = self._format_rut(self.vat)
        soap_url = (self.env.company.api_server_url or '').split('?')[0]
        _logger.info("[l10n_uy_vat_query] Iniciando consulta RUT %s a %s", rut, soap_url)

        envelope = self._build_soap_envelope(rut)
        headers = {
            'Content-Type': 'text/xml; charset=UTF-8',
            'SOAPAction': 'CONSULTARRECEPTORES'
        }

        try:
            response = requests.post(soap_url, data=envelope.encode('utf-8'), headers=headers, timeout=30)
        except Exception as e:
            _logger.exception("Error de conexión al servicio SOAP")
            raise UserError(_("No se pudo conectar al servicio SOAP: %s") % e)

        _logger.debug("[l10n_uy_vat_query] HTTP %s – %s", response.status_code, response.text)
        self.xml_result = response.text

        if response.status_code != 200:
            raise UserError(_("Error HTTP %s al consultar SOAP:\n%s") % (response.status_code, response.text))

        # Parsear Envelope y detectar Fault
        root = ET.fromstring(response.content)
        fault = root.find('.//{http://schemas.xmlsoap.org/soap/envelope/}Fault')
        if fault is not None:
            # buscamos faultstring sin importar namespace
            fault_str_el = fault.find('faultstring') or fault.find('.//{*}faultstring')
            fault_str = fault_str_el.text if fault_str_el is not None else 'Error desconocido'
            raise UserError(_("Fault en respuesta SOAP: %s") % fault_str)

        # Extraer <Xmlretorno> con contenido escapado
        xmlret = root.find('.//{GFE_Client}Xmlretorno') or root.find('.//{*}Xmlretorno')
        if xmlret is None or not xmlret.text:
            raise UserError(_("No se encontró la sección <Xmlretorno> en la respuesta SOAP."))

        # Desescape y parseo interno
        inner_xml = html.unescape(xmlret.text)
        _logger.debug("[l10n_uy_vat_query] Inner XML:\n%s", inner_xml)

        try:
            data_root = ET.fromstring(inner_xml)
        except ET.ParseError:
            raise UserError(_("El XML interno no es válido:\n%s") % inner_xml)

        # Validar resultado
        resultado = data_root.find('.//{*}Resultado')
        descripcion = data_root.find('.//{*}Descripcion')
        if resultado is not None and resultado.text != '1':
            msg = descripcion.text if descripcion is not None else _("Error desconocido")
            raise UserError(_("Error al consultar RUT: %s") % msg)

        # Si quieres poblar datos, llama aquí a load_dgi_data(inner_xml)

