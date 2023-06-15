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

    'depends': ['sinergis','mail','helpdesk'],

    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/product.xml',
        'views/sale.xml',
        'views/settings.xml',
        'views/res_config.xml',
        'views/partner.xml',
        'views/annual_contract.xml',
        'data/automation.xml',
        'data/helpdesk.xml',
    ],
    'assets': {
        'web.assets_backend': [
        ],
        'web.assets_qweb': [
        ],
    },
}
