# -*- coding: utf-8 -*-
{
    'name': "sinergis_billing_control",

    'version': '1.0',

    'summary': """
        Module Sinergis de verification de la facturation""",

    'description': """
        Module Sinergis de verification de la facturation
    """,

    'author': "Productivity",
    'website': "https://www.sinergis.fr",

    'category': 'Authentication',
    'version': '0.1',

    'depends': ['web','mail'],

    'data': [
        'security/ir.model.access.csv',
        'views/sinergis_billing_control.xml',
    ],
    'assets': {
        'web.assets_backend': [
        ],
        'web.assets_qweb': [
        ],
    },
}
