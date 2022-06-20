# -*- coding: utf-8 -*-
{
    'name': "sinergis",

    'summary': """
        Module Sinergis""",

    'description': """
        Module Sinergis
    """,

    'author': "Sinergis",
    'website': "http://www.sinergis.fr",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Authentication',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['mail','contacts','base','project','l10n_fr','l10n_fr_siret','hr','sale','project','account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/partner.xml',
        'views/helpdesk.xml',
        'views/calendar.xml',
        'views/sale.xml',
        'views/project.xml',
        'views/users.xml',
        'views/company.xml',
        'views/mail.xml',
        'report/report_helpdesk.xml',
        'report/report_calendar.xml',
        'report/report_devis_ventes.xml',
        'data/mail_template.xml',
        'data/mail_helpdesk_ticket.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
