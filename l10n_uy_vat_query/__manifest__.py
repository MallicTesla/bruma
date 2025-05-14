# -*- coding: utf-8 -*-
{
    'name': "Consulta de RUT en DGI (SOAP)",
    'summary': "API SOAP para consultar datos de un RUT en el servicio de DGI",
    'description': """
        Sustituye la antigua consulta REST por un servicio SOAP conforme a la especificación 
        de DGI: enveloping SOAP, CDATA con <ReceptorActEmpresarial/>, respuesta en <WS_PersonaActEmpresarial/>.
    """,
    'author': "Primate, Proyectasoft",
    'website': "https://primate.uy",
    'category': 'Localization/Uruguay',
    'version': '0.2',
    'license': 'LGPL-3',
    'depends': ['base', 'l10n_uy_einvoice_base'],
    'data': [
        'security/security.xml',
        'views/res_config_settings.xml',
        'views/res_partner.xml',
    ],
    'installable': True,
    'application': False,
}
