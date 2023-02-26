{
    'name': "Formation",

    'summary': """
        Module de gestion de formations sur odoo
        """,

    'description': """
        Module de gestion de formations sur odoo
    """,

    'author': "Esteban ANTONIO-MOTA",
    'website': "http://www.estedev.fr",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base','product','sale','mail','calendar','sinergis'],

    'data': [
        'security/ir.model.access.csv',
        'views/training.xml',
        'views/training_quiz.xml',
        'views/product.xml',
        'views/calendar.xml',
        'views/sale.xml',
        'views/settings.xml',
        'views/company.xml',
        'report/training_agreement_report.xml',
        'report/training_consultant_evaluation_report.xml',
        'report/layout_training_attendance_sheet.xml',
        'report/training_attendance_sheet.xml',
        'report/training_certificate_of_attendance.xml',
        'data/mail_training_agreement.xml',
        'data/mail_training_invitation.xml',
        'data/mail_training_invitation_remote.xml',
        'data/mail_training_diagnostic_quiz.xml',
        'data/mail_training_ended_quiz.xml',
        'data/mail_training_delayed_assessment.xml',
        'data/mail_training_opco_quiz.xml',
        'static/web/quiz_template.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'training/static/src/scss/training.scss',
            'training/static/src/js/training.js',
        ]
    },
}
