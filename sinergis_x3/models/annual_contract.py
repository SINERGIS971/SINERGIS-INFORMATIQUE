from odoo import models, fields, api
from odoo.exceptions import ValidationError

import requests
import json
import base64
import sys

class SinergisAnnualContracts(models.Model):
    _name = "sinergis_x3.annual_contract"
    _description = "Contrats Annuels"

    # Relié via code client X3
    BPCORD = fields.Char(string="Code X3 du client")
    partner_id = fields.Many2one("res.partner",string="Client",required=True)

    # SORDER
    SALFCY = fields.Char(string="Site de vente", required=True) # S1, S2 OU S3
    SOHTYP = fields.Char(string="Type") # REAB OU NEW
    CUSORDREF = fields.Char(string="Type de contrat")
    ORDDAT = fields.Date(string="Date de commande",required=True)

    #SORDERP ET SORDERQ
    TSICOD0 = fields.Char(string="Type d'article")
    TSICOD1 = fields.Char(string="Logiciel")
    TSICOD2 = fields.Char(string="Module")
    TSICOD3 = fields.Char(string="Hébergement")
    TSICOD4 = fields.Char(string="Logiciel")
    ITMDES = fields.Char(string="Désignation")
    X_SERNUM = fields.Char(string="N° de série")
    X_EVO= fields.Char(string="Évolution")
    X_COMEVO = fields.Char(string="Commande évolution")
    X_PERIOD = fields.Char(string="Périodicité")
    X_RENOUVELE = fields.Char(string="Renouvelé")
    STRDAT = fields.Date(string="Début de contrat")
    ENDDAT = fields.Date(string="Fin de contrat")
    QTY = fields.Integer(string="Quantité")
    SAU = fields.Char(string="Unité")
    NETPRI = fields.Float(string="Prix net unitaire")
    PFM = fields.Float(string="Marge unitaire")
    X_RESILIE = fields.Char(string="Résilié")
    X_DATRESIL = fields.Date(string="Date résiliation")
    LASINVNUM = fields.Char(string="No de facture")

    #GACCDUDATE
    AMTLOC = fields.Float(string="Montant échéance")
    PAYLOC = fields.Float(string="Montant payé comptabilisé")
    TMPLOC = fields.Float(string="Montant payé provisoire")

    def load_xctrencours_x3 (self):
        # Chargement authentification
        user_x3 = self.env['ir.config_parameter'].sudo().get_param('sinergis_x3.user_x3')
        password_x3 = self.env['ir.config_parameter'].sudo().get_param('sinergis_x3.password_x3')
        authentication_token = base64.b64encode(f"{user_x3}:{password_x3}".encode('utf-8')).decode("ascii")
        # Chargement URL
        base_url = self.env['ir.config_parameter'].sudo().get_param('sinergis_x3.base_url_x3')
        path_x3_contracts = self.env['ir.config_parameter'].sudo().get_param('sinergis_x3.path_x3_contracts')
        # Parametres
        url = base_url + path_x3_contracts
        cookies = False # Initalisation des cookies
        count_per_page = 1000 # Nombre d'items par page
        next_exists = True # Permet de savoir si une page existe ensuite

        headers = {'content-type': 'text/xml;charset=UTF-8',
         'Authorization': f'Basic {authentication_token}'}
        
        while next_exists:
            response = requests.get(f"{url}&count={str(count_per_page)}",
                            headers=headers,
                            cookies=cookies)
            cookies = response.cookies
            response_content = response.content
            response_json = json.loads(response_content)
            if not "$links" in response_json:
                raise ValidationError("Impossible de se connecter à X3 pour charger les contrats annuels")
            if not '$next' in response_json['$links']:
                next_exists = False
            else :
                url = response_json['$links']['$next']["$url"]

            #Chargement des données
            for resource in response_json['$resources']:
                SALFCY = resource["SALFCY"]
                SOHTYP = resource["SOHTYP"]
                CUSORDREF = resource["CUSORDREF"]
                # Il manque la date de commande ORDDAT
                BPCORD = resource["BPCORD"]
                TSICOD0 = resource["TSICOD0"]
                TSICOD1 = resource["TSICOD1"]
                TSICOD2 = resource["TSICOD2"]
                TSICOD4 = resource["TSICOD4"]

                ITMDES = resource["ITMDES"]
                X_SERNUM = resource["X_SERNUM"]
                X_EVO = resource["X_EVO"]
                X_COMEVO = resource["X_COMEVO"]
                X_PERIOD = resource["X_PERIOD"]
                X_RENOUVELE = resource["X_RENOUVELE"]
                STRDAT = resource["STRDAT"]
                ENDDAT = resource["ENDDAT"]
                QTY = resource["QTY"]
                SAU = resource["SAU"]
                NETPRI = resource["NETPRI"]
                PFM = resource["PFM"]
                # Il manque X_RESILIE
                # Il manque X_DATRESIL
                LASINVNUM = resource["LASINVNUM"]
                AMTLOC = resource["AMTLOC"]
                PAYLOC = resource["PAYLOC"]
                TMPLOC = resource["TMPLOC"]

                # On regarde si l'élément existe déjà dans la base
                entity = self.env['sinergis_x3.annual_contract'].search([('BPCORD','=',BPCORD),('CUSORDREF','=',CUSORDREF),('TSICOD0','=',TSICOD0),('TSICOD1','=',TSICOD1),('TSICOD2','=',TSICOD2),('TSICOD4','=',TSICOD4)])
                if not entity :
                    partner_id = self.env['res.partner'].search([("sinergis_x3_code","=",BPCORD)],limit=1)
                    data = {
                        "partner_id": partner_id,
                        "SALFCY": SALFCY,
                        "SOHTYP": SOHTYP,
                        "CUSORDREF": CUSORDREF,
                        "BPCORD": BPCORD,
                        "TSICOD0": TSICOD0,
                        "TSICOD1": TSICOD1,
                        "TSICOD2": TSICOD2,
                        "TSICOD4": TSICOD4,
                        "ITMDES": ITMDES,
                        "X_SERNUM": X_SERNUM,
                        "X_EVO": X_EVO,
                        "X_COMEVO": X_COMEVO,
                        "X_PERIOD": X_PERIOD,
                        "X_RENOUVELE": X_RENOUVELE,
                        "STRDAT": STRDAT,
                        "ENDDAT": ENDDAT,
                        "QTY": QTY,
                        "SAU": SAU,
                        "NETPRI": NETPRI,
                        "PFM": PFM,
                        "LASINVNUM": LASINVNUM,
                        "AMTLOC": AMTLOC,
                        "PAYLOC": PAYLOC,
                        "TMPLOC": TMPLOC
                    }
                    self.env['sinergis_x3.annual_contract'].create(data)
            

        

class ResPartner(models.Model):
    _inherit = "res.partner"
    _sql_constraints = [('x_sinergis_x3_annual_contract_unique', 'unique(x_sinergis_x3_annual_contract)', 'X3 code already exists!')]

    x_sinergis_x3_annual_contract = fields.One2many('sinergis_x3.annual_contract', 'partner_id', string="Contrats annuels X3", readonly=True)
