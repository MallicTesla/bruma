# -*- coding: utf-8 -*-
{
    'name': 'Periodo Facturación - Descripción simplificada',

    'summary': 'Evita que el plazo de la suscripción se agregue a la descripción de la factura.',

    'description': """
Este módulo añade un campo booleano en el plan de suscripción que, de estar activo,
se agregará en la sección de "Notas o Descripción" de la suscripción el siguiente texto:
    {Nombre de la Plantilla de cotización} - {Plan recurrente}
Por ejemplo: "Plan Básico - Mensualmente".
    """,

    'version': '17.0.1.0.0',
    'category': 'Accounting',
    'author': 'PrimateUY',
    'website': 'https://primate.uy',


    'depends': ['sale', 'account', 'sale_subscription'],

    'data': [
        'views/sale_subscription_plan_view.xml',
    ],

    'installable': True,
    'application': False,
}

