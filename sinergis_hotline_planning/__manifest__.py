# -*- coding: utf-8 -*-
{
    'name': "Sinergis Hotline Planning",

    'version': '1.0',

    'summary': """
        Module Sinergis de gestion du planning des hotlines""",

    'description': """
        Module Sinergis de gestion du planning des hotlines
    """,

    'author': "Productivity",
    'website': "https://www.sinergis.fr",

    'category': 'Authentication',
    'version': '0.1',

    'depends': ['web','mail'],

    'data': [
        'security/ir.model.access.csv',
        'views/event.xml',
    ],
    'assets': {
        'web.assets_backend': [
        ],
        'web.assets_qweb': [
        ],
    },
}
