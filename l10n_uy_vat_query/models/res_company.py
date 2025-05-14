# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    api_server_url = fields.Char(
        string="URL del servicio SOAP",
        help="URL del endpoint SOAP para consultar RUT en DGI"
    )
    vat_query_emp_code = fields.Char(
        string="Código de Empresa (EmpCod)",
        help="(Opcional) se usará solo si no se detecta automáticamente"
    )

