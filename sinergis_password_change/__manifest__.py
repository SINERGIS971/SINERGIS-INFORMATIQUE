# -*- coding: utf-8 -*-
{
    'name': "sinergis_password_change",

    'version': '1.0',

    'summary': """
        Module Sinergis de changement de mot de passe""",

    'description': """
        Module Sinergis de changement de mot de passe
    """,

    'author': "Productivity",
    'website': "https://www.sinergis.fr",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Authentication',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['web','sinergis'],

    # always loaded
    'data': [
        'views/users.xml',
        'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    'demo': [],
    'assets': {
        'web.assets_backend': [
            'sinergis_password_change/static/src/js/user_menu.js',
            'sinergis_password_change/static/src/js/widgets.js',
            'sinergis_password_change/static/src/js/systray.js',
        ],
        'web.assets_qweb': [
            'sinergis_password_change/static/src/xml/templates.xml',
        ],
    },

}
