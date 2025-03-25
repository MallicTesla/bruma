# -*- coding: utf-8 -*-
{
    'name': "Período de facturación en descripción",

    'summary': "Incluye en la descripción de la suscripción el nombre de la Plantilla de cotización y el Plan recurrente.",

    'description': """
Este módulo añade un campo booleano en el plan de suscripción que, de estar activo,
se agregará en la sección de "Notas o Descripción" de la suscripción el siguiente texto:
    {Nombre de la Plantilla de cotización} - {Plan recurrente}
Por ejemplo: "Plan Básico - Mensualmente".
    """,

    'version': '17.0.1.0.0',
    'category': 'Ventas',
    'author': 'PrimateUY',
    'website': 'https://primate.uy',


    'depends': ['sale_subscription', 'sale_management'],

    'data': [
        # 'security/ir.model.access.csv',
        'views/sale_subscription_plan_view.xml',
    ],

    'installable': True,
    'application': False

}

