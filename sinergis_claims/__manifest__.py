# -*- coding: utf-8 -*-
{
    'name': "Sinergis Réclamations",

    'version': '1.0',

    'summary': """
        Module Sinergis de suivi des réclamations""",

    'description': """
        Module Sinergis de suivi des réclamations
    """,

    'author': "Productivity",
    'website': "https://www.sinergis.fr",

    'category': 'Authentication',
    'version': '0.1',

    'depends': ['web','mail','training'],

    'data': [
        'security/ir.model.access.csv',
        'views/partner.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'sinergis_hotline_planning/static/src/js/systray.js',
        ],
        'web.assets_qweb': [
            'sinergis_hotline_planning/static/src/xml/systray.xml',
        ],
    },
}
