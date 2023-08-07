# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.addons.sinergis_x3.utils.soap import order_to_soap

from base64 import b64encode
from datetime import datetime

import base64
import requests
import urllib3
import xmltodict

class MyActions(models.Model):
    _inherit = "sinergis.myactions"

    # Transfert de Odoo vers X3
    def _send_order_for_x3 (self):
        # Vérification si l'utilisateur possède les droits
        if not self.env.user.has_group('sinegis_x3.group_myactivity_transfer'):
            return [False, f"Vous n'êtes pas autorisé à transférer cette intervention dans X3. Veuillez contacter un administrateur système."]
        # Chargement du code produit et sous-produit
        product_code = self.env["sinergis_x3.settings.sinergis_product"].search([("sinergis_product_id","=",self.sinergis_product_id.id)], limit=1).code
        subproduct_code = self.env["sinergis_x3.settings.sinergis_subproduct"].search([("sinergis_subproduct_id","=",self.sinergis_subproduct_id.id)], limit=1).code
        # Vérification si le transcodage produit / sous-produit existe bien
        if not product_code:
            return [False, f"Le produit {self.sinergis_product_id} n'est pas transcodé."]
        if not subproduct_code:
            return [False, f"Le sous-produit {self.sinergis_subproduct_id} n'est pas transcodé."]
        
        # Vérification de l'activation du module Odoo - X3
        enable = self.env['ir.config_parameter'].sudo().get_param('sinergis_x3.enable')
        if not enable:
            return [False, "Le module de transfert d'X3 n'est pas activé. Veuillez l'activer dans les paramètres."]
        
        missing_data = [] # Tableau qui comprend toutes les données manquantes
        commercial = self.env["sinergis_x3.settings.commercial"].search([("user_id","=",self.consultant.id)], limit=1).code
        sinergis_x3_company_id = self.env["sinergis_x3.settings.company"].search([("company_id","=",self.company_id.id)], limit=1)
        partner_id_x3_code = self.client.sinergis_x3_code
        if not sinergis_x3_company_id :
            missing_data.append(f"site de vente X3 ({self.company_id.name})")
        if not commercial :
            missing_data.append(f"transcodage du commercial ({self.consultant.name})")
        if not partner_id_x3_code:
            missing_data.append(f"code X3 du client ({self.client.name})")
        if not self.date:
            missing_data.append(f"date de l'activité")

        # Stop le processus s'il y a une donnée manquante
        if len(missing_data) > 0:
            raise ValidationError(f"Echec du transfert ! Éléments manquants : {','.join(missing_data)} ")

        # Génération du nom de commande Odoo
        X_DEVODOO = "S00000"
        if self.origin == "helpdesk":
            X_DEVODOO = f"A-{self.link_id}"
        elif self.origin == "calendar":
            X_DEVODOO = f"I-{self.link_id}"

        # Construction du tableau de paramètres
        data = {"SALFCY" : sinergis_x3_company_id.code,
                "SOHTYP" : "NEW",
                "CUSORDREF " : self.name,
                "X_DEVODOO" : X_DEVODOO,
                "ORDDAT" : fields.Datetime.context_timestamp(self.date).strftime("%Y%m%d"),
                "BPCORD" : partner_id_x3_code,
                "REP" : commercial,
                "REP(1)" : False,
                "DEMDLVDAT" : False}
        
        # Création du paramétrage de la ligne
        line_product_format = f"I{product_code}{subproduct_code}PH"
        # Ajout d'une description à la ligne
        if self.date:
            line_description = f"Intervention le {self.date.strftime('%d/%m/%Y %H:%M:%S')}"
        else :
            line_description = "Intervention"
        line_qty = self.time # Quantité en heures
        line_text = f"Intervention par {self.consultant.name}"
        
        # Chargement du prix horaire de l'intervention en fonction du type de produit
        line_price_unit = 0
        if self.sinergis_product_id.type == "PME":
            line_price_unit = self.env['ir.config_parameter'].sudo().get_param('sinergis_x3.hour_list_price_pme')
        elif self.sinergis_product_id.type == "MGE":
            line_price_unit = self.env['ir.config_parameter'].sudo().get_param('sinergis_x3.hour_list_price_mge')

        data_line = {
            "ITMREF" : line_product_format,
            "ITMDES" : line_description,
            "QTY" : line_qty,
            "SAU" : "H",
            "GROPRI" : line_price_unit,
            "DISCRGVAL1" : 0,
            "CPRPRI" : 0,
            "TEXT": line_text
        }
        data["lines"] = [data_line]
        
        # Chargement données Reverse Proxy
        user_rproxy = self.env['ir.config_parameter'].sudo().get_param('sinergis_x3.user_rproxy')
        password_rproxy = self.env['ir.config_parameter'].sudo().get_param('sinergis_x3.password_rproxy')
        authentication_token_rproxy = False
        if user_rproxy:
            authentication_token_rproxy = base64.b64encode(f"{user_rproxy}:{password_rproxy}".encode('utf-8')).decode("ascii")
        # Obtention de la requete SOAP
        user_x3 = self.env['ir.config_parameter'].sudo().get_param('sinergis_x3.user_x3')
        password_x3 = self.env['ir.config_parameter'].sudo().get_param('sinergis_x3.password_x3')
        pool_alias = self.env['ir.config_parameter'].sudo().get_param('sinergis_x3.pool_alias')
        public_name = self.env['ir.config_parameter'].sudo().get_param('sinergis_x3.public_name')
        authentication_token = b64encode(f"{user_x3}:{password_x3}".encode('utf-8')).decode("ascii")
        if authentication_token_rproxy:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            headers = {'content-type': 'text/xml;charset=UTF-8',
                   'Authorization': f'Basic {authentication_token}',
                   'sinergisauthorization': f'Basic {authentication_token_rproxy}',
                   'soapaction': "\"\"",}
        else:
            headers = {'content-type': 'text/xml;charset=UTF-8',
                   'Authorization': f'Basic {authentication_token}',
                   'soapaction': "\"\"",}
        data_soap = order_to_soap(data, pool_alias=pool_alias, public_name=public_name)
        #Connexion à X3
        base_url = self.env['ir.config_parameter'].sudo().get_param('sinergis_x3.base_url_x3')
        path_x3_orders = self.env['ir.config_parameter'].sudo().get_param('sinergis_x3.path_x3_orders')
        response = requests.post(base_url+path_x3_orders, data=data_soap.encode('utf-8'), headers=headers, verify=False).content
        
        # On obtient le résultat de la requête
        try:
            response_dict = xmltodict.parse(response)
            status = response_dict["soapenv:Envelope"]["soapenv:Body"]["wss:saveResponse"]["saveReturn"]["status"]["#text"]
        except:
            return [False, "Erreur rencontrée au moment de lire la réponse d'X3"]
        
        # Si le status n'est pas à "1", il y a une erreur
        if status != "1":
            return [False, f"Erreur rencontrée sur X3! Réponse : {response}"]
        
        # Le transfert est validé
        # Chargement des informations sur la commande depuis la réponse d'X3
        sinergis_x3_id = False
        sinergis_x3_price_subtotal = False           
        sinergis_x3_price_total = False
        try:
            result_xml = response_dict["soapenv:Envelope"]["soapenv:Body"]["wss:saveResponse"]["saveReturn"]["resultXml"]["#text"]
            result_xml = result_xml.replace("""'<?xml version="1.0" encoding="UTF-8"?>""","")
            result_dict = xmltodict.parse(result_xml)
            sinergis_x3_price_subtotal = False           
            sinergis_x3_price_total = False
            for grp in result_dict["RESULT"]["GRP"]:
                if grp["@ID"] == "SOH0_1":
                    for fld in grp["FLD"]:
                        if fld["@NAME"] == "SOHNUM":
                            sinergis_x3_id = fld["#text"]
                if grp["@ID"] == "SOH4_4":
                    for fld in grp["FLD"]:
                        if fld["@NAME"] == "ORDINVNOT":
                            sinergis_x3_price_subtotal = fld["#text"]
                        if fld["@NAME"] == "ORDINVATI":
                            sinergis_x3_price_total = fld["#text"]
        except:
            print("Récupération des données de la commande impossible")

        # On retourne True car le transfert a été effectué avec succès
        # On ajoute les données d'X3 pour l'ajout des infos dans Odoo
        return [True, {'sinergis_x3_id': sinergis_x3_id,
                       'sinergis_x3_price_subtotal': sinergis_x3_price_subtotal,
                       'sinergis_x3_price_total': sinergis_x3_price_total}]