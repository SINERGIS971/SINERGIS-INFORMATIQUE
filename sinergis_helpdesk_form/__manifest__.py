# -*- coding: utf-8 -*-
{
    'name': "Sinergis Helpdesk Form",

    'version': '1.0',

    'summary': """
        Module Sinergis permettant la mise en place d'un formulaire de saisie de tickets""",

    'description': """
        Module Sinergis permettant la mise en place d'un formulaire de saisie de tickets
    """,

    'author': "Productivity",
    'website': "https://www.sinergis.fr",

    'category': 'Authentication',
    'version': '0.1',

    'depends': ['web','mail'],

    'data': [
        'security/ir.model.access.csv',
        'static/web/quiz_template.xml',
    ],
    'assets': {
        'web.assets_backend': [
        ],
        'web.assets_qweb': [
        ],
    },
}
