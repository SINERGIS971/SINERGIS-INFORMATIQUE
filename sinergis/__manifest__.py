# -*- coding: utf-8 -*-
{
    'name': "sinergis",

    'summary': """
        Module Sinergis""",

    'description': """
        Module Sinergis
    """,

    'author': "Sinergis",
    'website': "https://www.sinergis.fr",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Authentication',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['web','mail','contacts','base','project','l10n_fr','l10n_fr_siret','hr','sale','project','account'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/partner.xml',
        'views/helpdesk.xml',
        'views/calendar.xml',
        'views/sale.xml',
        'views/sale_report.xml',
        'views/project.xml',
        'views/crm.xml',
        'views/users.xml',
        'views/company.xml',
        'views/mail.xml',
        'views/movementArea.xml',
        'views/sentmail.xml',
        'views/my_actions.xml',
        'views/product.xml',
        'views/hr_employee.xml',
        'views/reports_overview.xml',
        'views/res_config.xml',
        'report/report_helpdesk.xml',
        'report/report_calendar.xml',
        'report/layout_devis_ventes.xml',
        'report/report_devis_ventes.xml',
        'report/report_myactions.xml',
        'report/report_timesheet.xml',
        'data/mail_template.xml',
        'data/mail_helpdesk_ticket.xml',
        'data/mail_calendar_event_intervention.xml',
        'data/mail_res_partner_litige.xml',
        'data/mail_helpdesk_ticket_last_call_button.xml',
        'data/mail_helpdesk_ticket_partner_reminder_button.xml',
        'data/mail_helpdesk_consultant_assignated.xml',
        'data/helpdesk_automation.xml',
        'static/web/statistics_dashboard.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'sinergis/static/src/js/button_confirm.js',
            'sinergis/static/src/js/help_button.js',
            # Permet de toujours avoir toutes les sociétés Sinergis cochées.
            'sinergis/static/src/js/all_companies.js',
            'sinergis/static/src/js/calendar_vacation.js',
            'sinergis/static/src/js/calendar_vacation_widget.js',
            'sinergis/static/src/js/helpdesk_widget.js',
            'sinergis/static/src/js/partner_widget.js',
            #'sinergis/static/src/js/dialog_popup.js',
            'sinergis/static/src/css/style.css',
        ],
        'web.assets_qweb': [
            #'sinergis/static/src/xml/menu_company.xml',
            'sinergis/static/src/xml/help_button.xml',
            'sinergis/static/src/xml/sinergis_base_calendar.xml',
            'sinergis/static/src/xml/calendar_vacation.xml',
            #'sinergis/static/src/xml/chatter.xml',
            'sinergis/static/src/xml/helpdesk.xml',
            'sinergis/static/src/xml/partner_unlock_technical_notes.xml',
        ],
    },

}
