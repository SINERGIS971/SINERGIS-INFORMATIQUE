# -*- coding: utf-8 -*-
{
    'name': "sinergis_rgpd",

    'version': '1.0',

    'summary': """
        Module Sinergis de gestion des données confidentielles""",

    'description': """
        Module Sinergis de gestion des données confidentielles
    """,

    'author': "Productivity",
    'website': "https://www.sinergis.fr",

    'category': 'Authentication',
    'version': '0.1',

    'depends': ['web'],

    'data': [
        'views/sensitive_data.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
    ],
}
