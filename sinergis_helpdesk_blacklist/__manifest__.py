# -*- coding: utf-8 -*-
{
    'name': "Sinergis Helpdesk Blacklist",

    'version': '1.0',

    'summary': """
        Module Sinergis de blacklist des spams dans l'assistance""",

    'description': """
        Module Sinergis de blacklist des spams dans l'assistance.
        Le module 'sinergis' est requis.
    """,

    'author': "Productivity",
    'website': "https://www.sinergis.fr",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Authentication',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ["helpdesk","base","sinergis"],

    # always loaded
    'data': [
        'security/security.xml',
        'views/helpdesk.xml',
        'data/automation.xml',
        'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    'demo': [],
    'assets': {
        'web.assets_backend': [
        ],
        'web.assets_qweb': [
        ],
    },

}
