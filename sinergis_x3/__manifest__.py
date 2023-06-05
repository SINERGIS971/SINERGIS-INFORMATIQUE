# -*- coding: utf-8 -*-
{
    'name': "Connecteur Odoo - X3",

    'version': '1.0',

    'summary': """
        Module de synchronisation entre Odoo et X3""",

    'description': """
        Module permettant le transfert des commandes vers X3 et la remontée des contrats annuels.
    """,

    'author': "Sinergis",
    'website': "https://www.sinergis.fr",

    'category': 'Tools',
    'version': '0.1',

    'depends': ['sinergis','mail'],

    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/product.xml',
        'views/settings.xml',
    ],
    'assets': {
        'web.assets_backend': [
        ],
        'web.assets_qweb': [
        ],
    },
}
