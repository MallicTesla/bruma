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
        """Formatea el RUT eliminando guiones/puntos y asegurando 12 dígitos."""
        clean = (vat or '').replace('-', '').replace('.', '')
        return clean.zfill(12)

    def _get_emp_code(self):
        """Obtiene EmpCod según el modo (testing/live) o campo manual."""
        company = self.env.company
        if company.cfe_provider == 'datalogic':
            if company.einvoice_mode == 'testing':
                return company.company_code_test or ''
            if company.einvoice_mode == 'live':
                return company.company_code or ''
        return company.vat_query_emp_code or ''

    def _build_soap_envelope(self, rut):
        """Construye el envelope SOAP con CDATA interno para CONSULTARRECEPTORES."""
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
        return envelope

    @api.onchange('consulta_rut')
    def _onchange_consulta_rut(self):
        """Onchange que envía la consulta SOAP y muestra todo en consola."""
        if not self.consulta_rut or not self.vat:
            return
        rut = self._format_rut(self.vat)
        soap_url = (self.env.company.api_server_url or '').split('?')[0]

        # 1) Mostrar URL y Envelope
        print("===== ENVÍO SOAP URL =====", soap_url)
        envelope = self._build_soap_envelope(rut)
        print("===== ENVÍO SOAP ENVELOPE =====")
        print(envelope)

        headers = {
            'Content-Type': 'text/xml; charset=UTF-8',
            'SOAPAction': 'CONSULTARRECEPTORES'
        }

        # 2) Enviar petición
        try:
            response = requests.post(soap_url, data=envelope.encode('utf-8'), headers=headers, timeout=30)
        except Exception as e:
            print("===== ERROR DE CONEXIÓN =====", e)
            raise UserError(_("No se pudo conectar al servicio SOAP: %s") % e)

        # 3) Imprimir respuesta completa
        print("===== HTTP STATUS =====", response.status_code)
        print("===== RESPUESTA RAW =====")
        print(response.text)
        self.xml_result = response.text

        if response.status_code != 200:
            raise UserError(_("Error HTTP %s al consultar SOAP:\n%s") % (response.status_code, response.text))

        # 4) Parsear Fault si existe
        root = ET.fromstring(response.content)
        fault = root.find('.//{http://schemas.xmlsoap.org/soap/envelope/}Fault')
        if fault is not None:
            fault_el = fault.find('faultstring') or fault.find('.//{*}faultstring')
            fault_str = fault_el.text if fault_el is not None else 'Error desconocido'
            print("===== SOAP FAULT =====", fault_str)
            raise UserError(_("Fault en respuesta SOAP: %s") % fault_str)

        # 5) Extraer <Xmlretorno>
        xmlret = root.find('.//{GFE_Client}Xmlretorno') or root.find('.//{*}Xmlretorno')
        if xmlret is None or not xmlret.text:
            print("===== NO SE ENCONTRÓ Xmlretorno =====")
            raise UserError(_("No se encontró la sección <Xmlretorno> en la respuesta SOAP."))

        # 6) Mostrar contenido escapado
        print("===== Xmlretorno ESCAPADO =====")
        print(xmlret.text)

        # 7) Desescapar y mostrar
        inner_xml = html.unescape(xmlret.text)
        print("===== Xmlretorno DESESCAPADO =====")
        print(inner_xml)

        # 8) Parseo interno
        try:
            data_root = ET.fromstring(inner_xml)
        except ET.ParseError as e:
            print("===== ERROR PARSEANDO XML INTERNO =====", e)
            raise UserError(_("El XML interno no es válido:\n%s") % inner_xml)

        # 9) Validar Resultado
        resultado = data_root.find('.//{*}Resultado')
        descripcion = data_root.find('.//{*}Descripcion')
        if resultado is not None and resultado.text != '1':
            msg = descripcion.text if descripcion is not None else _('Error desconocido')
            print("===== RESULTADO NO 1 =====", resultado.text, descripcion.text if descripcion is not None else '')
            raise UserError(_("Error al consultar RUT: %s") % msg)

        # 10) Consulta exitosa
        print("===== CONSULTA EXITOSA =====")
        # Aquí puedes llamar load_dgi_data(inner_xml) para actualizar campos
