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

    'depends': ['web','mail'],

    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/partner.xml',
        'views/sensitive_data.xml',
        'data/activity_type.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'sinergis_rgpd/static/src/js/systray.js',
            'sinergis_rgpd/static/src/js/service.js',
            'sinergis_rgpd/static/src/js/user_menu.js',
        ],
        'web.assets_qweb': [
            'sinergis_rgpd/static/src/xml/templates.xml',
        ],
    },
}
