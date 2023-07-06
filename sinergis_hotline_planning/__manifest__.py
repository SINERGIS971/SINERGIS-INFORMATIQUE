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

    'depends': ['web','mail','training'],

    'data': [
        'security/ir.model.access.csv',
        'views/event.xml',
        'report/hotline_planning_sheet.xml',
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
