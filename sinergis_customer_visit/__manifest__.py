# -*- coding: utf-8 -*-
{
    'name': "Sinergis Visite Client",

    'version': '1.0',

    'summary': """
        Module Sinergis permettant d'organiser les visites chez les clients""",

    'description': """
        Module Sinergis permettant d'organiser les visites chez les clients
    """,

    'author': "Productivity",
    'website': "https://www.sinergis.fr",

    'category': 'Authentication',
    'version': '0.1',

    'depends': ['web','mail','base','sinergis'],

    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/calendar.xml',
        'views/visit.xml',
        'views/partner.xml',
    ],
    'assets': {
        'web.assets_backend': [
        ],
        'web.assets_qweb': [
        ],
    },
}
