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

    'depends': ['base','product','sale','mail'],

    'data': [
        'security/ir.model.access.csv',
        'views/training.xml',
        'views/training_quiz.xml',
        'views/product.xml',
        'views/settings.xml',
        'report/training_agreement_report.xml',
        'report/training_consultant_evaluation_report.xml',
        'report/training_attendance_sheet.xml',
        'data/mail_training_agreement.xml',
        'data/mail_training_invitation.xml',
        'data/mail_training_positioning_quiz.xml',
        'data/mail_training_ended_quiz.xml',
        'data/mail_training_delayed_assessment.xml',
        'data/mail_training_opco_quiz.xml',
        'static/web/quiz_template.xml',
    ],
}
