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
    
    user_x3 = fields.Char(string="Nom d'utilisateur",
                              config_parameter='sinergis_x3.user_x3')
    
    password_x3 = fields.Char(string="Mot de passe",
                              config_parameter='sinergis_x3.password_x3')
    
    def test_x3_connection (self):
        if self.base_url_x3:
            code = requests.get(self.base_url_x3).status_code
            if code == 200:
                raise ValidationError("Connexion : SUCCESS")
            else :
                raise ValidationError(f"Connexion : ECHEC | Code : {str(code)}")