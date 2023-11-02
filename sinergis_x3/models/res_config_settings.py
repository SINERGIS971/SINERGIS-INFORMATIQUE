# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import ValidationError

from datetime import datetime

import requests
import urllib3


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    enable = fields.Boolean(string="Activer le module",
                            config_parameter='sinergis_x3.enable')

    # CONFIGURATION URL

    base_url_x3 = fields.Char(string="URL X3 DE BASE",
                              config_parameter='sinergis_x3.base_url_x3',
                              placeholder="https://domain.fr")
    path_x3_orders = fields.Char(string="CHEMIN POST DES COMMANDES",
                              config_parameter='sinergis_x3.path_x3_orders',
                              placeholder="/exemple/")
    path_x3_contracts = fields.Char(string="CHEMIN GET DES CONTRATS ANNUELS",
                              config_parameter='sinergis_x3.path_x3_contracts',
                              placeholder="/exemple/")
    
    path_x3_actions = fields.Char(string="CHEMIN GET DES ACTIVITES ODOO",
                              config_parameter='sinergis_x3.path_x3_actions',
                              placeholder="/exemple/")
    
    # REVERSE PROXY CONNEXION

    user_rproxy = fields.Char(string="Nom d'utilisateur reverse proxy",
                              config_parameter='sinergis_x3.user_rproxy')
    password_rproxy = fields.Char(string="Mot de passe reverse proxy",
                              config_parameter='sinergis_x3.password_rproxy')

    # CONFIGURATION CONNEXION

    user_x3 = fields.Char(string="Nom d'utilisateur",
                              config_parameter='sinergis_x3.user_x3')
    password_x3 = fields.Char(string="Mot de passe",
                              config_parameter='sinergis_x3.password_x3')
    
    # CONFIGURATION WEB SERVICE

    pool_alias = fields.Char(string="Pool alias",
                              config_parameter='sinergis_x3.pool_alias')
    public_name = fields.Char(string="Nom du web service",
                              config_parameter='sinergis_x3.public_name')
    
    # PARAMETRAGE D'IMPORTATION DES DONNEES
    
    contract_duration_validity = fields.Integer(string="Durée de validité d'un contrat annuel",
                              config_parameter='sinergis_x3.contract_duration_validity')
    
    # PARAMETRAGE TARIF AU TEMPS PASSE

    hour_list_price_pme = fields.Float(string="Prix horaire d'une intervention au temps passé pour la PME",
                              config_parameter='sinergis_x3.hour_list_price_pme')
    
    hour_list_price_mge = fields.Float(string="Prix horaire d'une intervention au temps passé pour la MGE",
                              config_parameter='sinergis_x3.hour_list_price_mge')

    day_list_price_pme = fields.Float(string="Prix journalier d'une intervention au temps passé pour la PME",
                              config_parameter='sinergis_x3.day_list_price_pme')
    
    day_list_price_mge = fields.Float(string="Prix journalier d'une intervention au temps passé pour la MGE",
                              config_parameter='sinergis_x3.day_list_price_mge')
    
    # PARAMETRAGE DE LA SYNCHRONISATION DU FACTURABLE ODOO AVEC LA VUE X3

    last_billable_update_x3 = fields.Char(string="Date de la dernière MàJ (UTC)" , readonly=True, config_parameter='sinergis_x3.last_billable_update_x3')
    
    def test_x3_connection (self):
        if self.base_url_x3:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            code = requests.get(self.base_url_x3, verify=False).status_code
            if code == 200:
                raise ValidationError("Connexion : SUCCESS")
            else :
                raise ValidationError(f"Connexion : ECHEC | Code : {str(code)}")

    # Remise à zero des contrats annuels    
    def reset_annual_contracts(self):
        self.env["sinergis_x3.annual_contract"].search([], limit=1000000).unlink()

    def billiable_update_x3(self):
        self.env['ir.config_parameter'].sudo().set_param('sinergis_x3.last_billable_update_x3', datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        #raise ValidationError("Fonctionnalité en développement")