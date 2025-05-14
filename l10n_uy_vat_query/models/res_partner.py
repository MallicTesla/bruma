# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import xmltodict
import requests

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    consulta_rut = fields.Boolean("Consultar RUT")
    xml_result = fields.Text(string="Última respuesta SOAP", readonly=True)

    def get_param(self, field_name):
        self = self.sudo()
        value = getattr(self.env.company, field_name, False)
        if not value:
            raise ValidationError(f"No está configurado '{field_name}' en la Compañía.")
        return value

    def _get_emp_code(self):
        """
        Retorna el EmpCod automático según el proveedor y modo:
        - si provider='datalogic' y mode='testing' -> company_code_test
        - si provider='datalogic' y mode='live'    -> company_code
        - en otro caso, usa vat_query_emp_code configurado manualmente
        """
        company = self.env.company
        if company.cfe_provider == 'datalogic':
            if company.einvoice_mode == 'testing':
                return company.company_code_test or ''
            elif company.einvoice_mode == 'live':
                return company.company_code or ''
        # fallback manual
        return company.vat_query_emp_code or ''

    def _build_soap_envelope(self, rut):
        emp_code = self._get_emp_code()
        if not emp_code:
            raise ValidationError("No se ha encontrado 'EmpCod' para el servicio SOAP.")
        # Construir el contenido CDATA con los tags case-sensitive
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
                    '<Dato>'
                        '<Valor>%s</Valor>'
                    '</Dato>'
                '</Datos>'
            '</XMLEntrada>' % cdata
        )
        envelope = (
            '<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" '
                            'xmlns:gfe="GFE_Client">'
                '<soapenv:Header/>'
                '<soapenv:Body>'
                    '<gfe:WSExternoStandalone.CONSULTARRECEPTORDGI>'
                        f'<gfe:Xmlentrada>{xmlentrada}</gfe:Xmlentrada>'
                    '</gfe:WSExternoStandalone.CONSULTARRECEPTORDGI>'
                '</soapenv:Body>'
            '</soapenv:Envelope>'
        )
        return envelope

    def _parse_response(self, content):
        tree = ET.fromstring(content)
        for valor in tree.iterfind('.//{*}Valor'):
            text = valor.text or ''
            if text.strip().startswith('<'):
                return text
        return False

    def _consultar_partner_ruc(self):
        url = self.get_param('api_server_url')
        envelope = self._build_soap_envelope(self.vat)
        headers = {
            'Content-Type': 'text/xml;charset=UTF-8',
            'SOAPAction': 'ConsultarReceptorDGI'
        }
        response = requests.post(url, data=envelope, headers=headers, timeout=30)
        if response.status_code != 200:
            raise ValidationError(
                f"Error HTTP {response.status_code} al consultar SOAP: {response.text}"    
            )
        self.xml_result = response.text
        inner_xml = self._parse_response(response.text)
        if not inner_xml:
            raise ValidationError("No se encontró la sección de datos en la respuesta SOAP.")
        return self.load_dgi_data(inner_xml)

    @api.onchange('consulta_rut')
    def onchange_consulta_rut(self):
        if self.consulta_rut and self.vat:
            self._consultar_partner_ruc()