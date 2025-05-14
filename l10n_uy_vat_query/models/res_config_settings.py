# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    api_server_url = fields.Char(
        string="URL del servicio SOAP",
        related='company_id.api_server_url', readonly=False
    )
    vat_query_emp_code = fields.Char(
        string="Código de Empresa (EmpCod)",
        related='company_id.vat_query_emp_code', readonly=False
    )

    @api.model
    def get_values(self):
        res = super().get_values()
        company = self.env.company
        # Autocompletar EmpCod según modo y proveedor
        emp_code = ''
        if company.cfe_provider == 'datalogic':
            if company.einvoice_mode == 'testing':
                emp_code = company.company_code_test
            elif company.einvoice_mode == 'live':
                emp_code = company.company_code
        # si no aplica, queda vacío y puede editarse manualmente
        res.update({
            'vat_query_emp_code': emp_code,
        })
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.company_id.write({
            'api_server_url': self.api_server_url,
            'vat_query_emp_code': self.vat_query_emp_code,
        })
