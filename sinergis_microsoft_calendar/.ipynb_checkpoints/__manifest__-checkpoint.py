# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Module Calendrier Outlook Sinergis',
    'version': '1.0',
    'category': 'Productivity',
    'description': "",
    'depends': ['microsoft_account', 'calendar'],
    'data': [
        'data/microsoft_calendar_data.xml',
        'security/ir.model.access.csv',
        'wizard/reset_account_views.xml',
        'views/res_config_settings_views.xml',
        'views/res_users_views.xml',
        'views/microsoft_calendar_views.xml',
        ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'post_init_hook': 'init_initiating_microsoft_uuid',
    'assets': {
        'web.assets_backend': [
            'sinergis_microsoft_calendar/static/src/js/microsoft_calendar_popover.js',
            'sinergis_microsoft_calendar/static/src/js/microsoft_calendar.js',
            'sinergis_microsoft_calendar/static/src/scss/microsoft_calendar.scss',
        ],
        'web.assets_qweb': [
            'sinergis_microsoft_calendar/static/src/xml/*.xml',
        ],
    },
    'license': 'LGPL-3',
}
