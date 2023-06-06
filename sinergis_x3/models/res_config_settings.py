# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import ValidationError

import requests


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    base_url_x3 = fields.Char(string="URL X3 DE BASE",
                              config_parameter='sinergis_x3.base_url_x3',
                              placeholder="https://domain.fr")

    path_x3_orders = fields.Char(string="CHEMIN POST DES COMMANDES",
                              config_parameter='sinergis_x3.path_x3_orders',
                              placeholder="/exemple/")
    path_x3_contracts = fields.Char(string="CHEMIN GET DES CONTRATS ANNUELS",
                              config_parameter='sinergis_x3.path_x3_contracts',
                              placeholder="/exemple/")
    
    def test_x3_connection (self):
        code = requests.get(self.base_url_x3).status_code
        if code == 200:
            raise ValidationError("Connexion : SUCCES")
        else :
            raise ValidationError(f"Connexion : ECHEC | Code : {code}")