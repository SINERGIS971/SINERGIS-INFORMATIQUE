{
    'name': "Limite temporelle mot de passe",

    'summary': """
        Module permettant de notifier l'utilisateur si son dernier changement de mot de passe date d'il y a plus d'une certaine durée.
        """,

    'description': """
        Module permettant de notifier l'utilisateur si son dernier changement de mot de passe date d'il y a plus d'une certaine durée.
    """,

    'author': "Esteban ANTONIO-MOTA",
    'website': "http://www.estedev.fr",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base','web','mail'],

    'data': [
        'views/sinergis_password_time_limit.xml',
    ],
    'assets': {
        'web.assets_qweb': [
            'sinergis_password_time_limit/static/src/xml/panel.xml',
        ]
    },
}

