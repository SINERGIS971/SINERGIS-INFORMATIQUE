# -*- coding: utf-8 -*-
{
    'name': "Sinergis Mailchimp",

    'version': '1.0',

    'summary': """
        Connecteur Mailchimp pour Sinergis""",

    'description': """
        Connecteur Mailchimp pour Sinergis
    """,

    'author': "Productivity",
    'website': "https://www.sinergis.fr",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Authentication',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ["base","sinergis","contacts"],

    # always loaded
    'data': [
        'views/res_config.xml',
        'views/settings.xml',
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
