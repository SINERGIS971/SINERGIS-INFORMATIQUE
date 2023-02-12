# -*- coding: utf-8 -*-
{
    'name': "sinergis_outlook",

    'version': '1.0',

    'summary': """
        Module Sinergis de synchronisation Outlook""",

    'description': """
        Module Sinergis de synchronisation Outlook
    """,

    'author': "Productivity",
    'website': "https://www.sinergis.fr",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Authentication',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['microsoft_account', 'calendar'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
    'assets': {
        'web.assets_backend': [],
        'web.assets_qweb': [],
    },

}
