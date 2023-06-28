from odoo import models, fields, api
from odoo.exceptions import ValidationError

from datetime import date, datetime, timedelta

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
    SALFCY = fields.Char(string="Site de vente") # S1, S2 OU S3 #DEF
    SOHTYP = fields.Char(string="Type") # REAB OU NEW #OPT
    SOHNUM = fields.Char(string="Numéro de commande") #OPT
    CUSORDREF = fields.Char(string="Type de contrat") #DEF
    ORDDAT = fields.Date(string="Date de commande")  #DEF

    #SORDERP ET SORDERQ
    TSICOD0 = fields.Char(string="Type d'article") #OPT
    TSICOD1 = fields.Char(string="Logiciel") #DEF
    TSICOD2 = fields.Char(string="Module") #DEF
    TSICOD4 = fields.Char(string="Hébergement") #DEF
    ITMDES = fields.Char(string="Désignation") #OPT
    X_SERNUM = fields.Char(string="N° de série") #DEF PREMIERE COLONNE
    X_EVO= fields.Char(string="Évolution") #OPT
    X_COMEVO = fields.Char(string="Commande évolution") #OPT
    X_PERIOD = fields.Char(string="Périodicité") #OPT
    X_RENOUVELE = fields.Char(string="Renouvelé") #OPT
    STRDAT = fields.Date(string="Début de contrat") #DEF
    ENDDAT = fields.Date(string="Fin de contrat") #DEF
    QTY = fields.Integer(string="Quantité") #OPT
    SAU = fields.Char(string="Unité") #OPT
    NETPRI = fields.Float(string="Prix net unitaire") #OPT
    PFM = fields.Float(string="Marge unitaire") #OPT
    X_RESILIE = fields.Char(string="Résilié") #DEF
    X_DATRESIL = fields.Date(string="Date résiliation") #OPT
    LASINVNUM = fields.Char(string="No de facture") #OPT

    #GACCDUDATE
    AMTLOC = fields.Float(string="Montant échéance") #OPT
    PAYLOC = fields.Float(string="Montant payé comptabilisé") #OPT
    TMPLOC = fields.Float(string="Montant payé provisoire") #OPT

    expired = fields.Boolean(compute="_compute_expired")

    @api.depends("expired")
    def _compute_expired(self):
        for rec in self:
            if rec.ENDDAT :
                if rec.ENDDAT <= date.today():
                    rec.expired = True
                else :
                    rec.expired = False
            else:
                rec.expired = False

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
        
        count = 0
        while next_exists:
            print("Count : "+str(count))
            count += count_per_page

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
                SOHNUM = resource["SOHNUM"]
                CUSORDREF = resource["CUSORDREF"]
                ORDDAT = resource["ORDDAT"]
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
                X_RESILIE = resource["X_RESILIE"]
                X_DATRESIL = resource["X_DATRESIL"]
                LASINVNUM = resource["LASINVNUM"]

                AMTLOC = resource["AMTLOC"]
                PAYLOC = resource["PAYLOC"]
                TMPLOC = resource["TMPLOC"]

                # Ajout de la date de commande
                if ORDDAT:
                    try:
                        ORDDAT = datetime.strptime(ORDDAT, '%Y-%m-%d')
                        contract_duration_validity = self.env['ir.config_parameter'].sudo().get_param('sinergis_x3.contract_duration_validity')
                        if not contract_duration_validity:
                            contract_duration_validity = 365
                        if ORDDAT + timedelta(days=int(contract_duration_validity)) < datetime.now() :
                            continue # Si la date de la commande date depuis plus d'une certaine durée, ne pas la prendre en compte
                    except ValueError as e:
                        continue # On saute l'itération actuelle
            
                if STRDAT and ENDDAT:
                    try:
                        STRDAT = datetime.strptime(STRDAT, '%Y-%m-%d')
                        ENDDAT = datetime.strptime(ENDDAT, '%Y-%m-%d')
                    except ValueError:
                        STRDAT = False
                        ENDDAT = False
                if X_DATRESIL:
                    try:
                        X_DATRESIL = datetime.strptime(X_DATRESIL, '%Y-%m-%d')
                    except ValueError:
                        X_DATRESIL = False
                        
                # On regarde si l'élément existe déjà dans la base
                entity = self.env['sinergis_x3.annual_contract'].search([('BPCORD','=',BPCORD),('SOHNUM','=',SOHNUM),('SOHTYP','=',SOHTYP),('TSICOD0','=',TSICOD0),('TSICOD1','=',TSICOD1),('TSICOD2','=',TSICOD2),('TSICOD4','=',TSICOD4)], limit=1)
                if not entity :
                    partner_id = self.env['res.partner'].search([("sinergis_x3_code","=",BPCORD)],limit=1)
                    if partner_id:
                        print(f"Ajout d'un contrat annuel pour le client : {partner_id.name}")
                        data = {
                                "partner_id": partner_id.id,
                                "SALFCY": SALFCY,
                                "SOHTYP": SOHTYP,
                                "SOHNUM": SOHNUM,
                                "CUSORDREF": CUSORDREF,
                                "ORDDAT": ORDDAT,
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
                                "X_RESILIE": X_RESILIE,
                                "X_DATRESIL": X_DATRESIL,
                                "PFM": PFM,
                                "LASINVNUM": LASINVNUM,
                                "AMTLOC": AMTLOC,
                                "PAYLOC": PAYLOC,
                                "TMPLOC": TMPLOC
                        }
                        self.env['sinergis_x3.annual_contract'].create(data)
                else:
                    data = {
                                "SALFCY": SALFCY,
                                "SOHTYP": SOHTYP,
                                "SOHNUM": SOHNUM,
                                "CUSORDREF": CUSORDREF,
                                "ORDDAT": ORDDAT,
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
                                "X_RESILIE": X_RESILIE,
                                "X_DATRESIL": X_DATRESIL,
                                "PFM": PFM,
                                "LASINVNUM": LASINVNUM,
                                "AMTLOC": AMTLOC,
                                "PAYLOC": PAYLOC,
                                "TMPLOC": TMPLOC
                        }
                    entity.write(data)
        
        # Suppression des anciens contrats annuels
        contract_duration_validity = self.env['ir.config_parameter'].sudo().get_param('sinergis_x3.contract_duration_validity')
        if not contract_duration_validity:
            contract_duration_validity = 365
        limit_date = datetime.now() - timedelta(days=int(contract_duration_validity))
        self.env["sinergis_x3.annual_contract"].search([("ORDDAT","<",datetime.strptime(limit_date, '%Y-%m-%d'))]).unlink()


class ResPartner(models.Model):
    _inherit = "res.partner"

    x_sinergis_x3_annual_contract = fields.One2many('sinergis_x3.annual_contract', 'partner_id', string="Contrats annuels X3", readonly=True)