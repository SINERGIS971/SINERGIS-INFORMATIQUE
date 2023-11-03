# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.addons.sinergis_x3.utils.soap import order_to_soap, order_line_text_to_soap, action_to_soap

from base64 import b64encode
from bs4 import BeautifulSoup 
from datetime import datetime

import base64
import markdown
import json
import requests
import urllib3
import xmltodict

class MyActions(models.Model):
    _inherit = "sinergis.myactions"

    #=====================================
    #Transférer les activités en commande#
    #=====================================

    # Transfert de Odoo vers X3
    def _send_order_for_x3 (self):
        # Vérification si l'utilisateur possède les droits
        if not self.env.user.has_group('sinergis_x3.group_myactivity_transfer'):
            return [False, f"Vous n'êtes pas autorisé à transférer cette intervention dans X3. Veuillez contacter un administrateur système."]
        # Chargement du code produit et sous-produit
        product_code = self.env["sinergis_x3.settings.sinergis_product"].search([("sinergis_product_id","=",self.sinergis_product_id.id)], limit=1).code
        subproduct_code = self.env["sinergis_x3.settings.sinergis_subproduct"].search([("sinergis_subproduct_id","=",self.sinergis_subproduct_id.id)], limit=1).code
        # Vérification si le transcodage produit / sous-produit existe bien
        if not product_code:
            return [False, f"Le produit {self.sinergis_product_id.name} n'est pas transcodé."]
        if not subproduct_code:
            return [False, f"Le sous-produit {self.sinergis_subproduct_id.name} n'est pas transcodé."]
        
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

        # Génération du nom
        CUSORDEF = "Intervention"
        if self.date :
            CUSORDEF = f"Intervention le : {self.date.strftime('%d/%m/%Y')}"
        # Construction du tableau de paramètres
        data = {"SALFCY" : sinergis_x3_company_id.code,
                "SOHTYP" : "NEW",
                "CUSORDREF " : CUSORDEF,
                "X_DEVODOO" : X_DEVODOO,
                "ORDDAT" : self.date.strftime("%Y%m%d"),
                "BPCORD" : partner_id_x3_code,
                "REP" : commercial,
                "REP(1)" : False,
                "DEMDLVDAT" : False}
        
        # Création du paramétrage de la ligne
        line_product_format = f"I{product_code}{subproduct_code}PH"
        # Ajout d'une description à la ligne
        line_description = f"Prestation {self.sinergis_product_id.name} {self.sinergis_subproduct_id.name}"

        line_qty = self.time # Quantité en heures
        line_text = f"Intervention par {self.consultant.name}"
        
        # Chargement du prix horaire de l'intervention en fonction du type de produit et du nombre d'horaires
        line_price_unit = 0
        hours_in_day = self.env['uom.uom'].search([('name',"=","Heures")]).ratio # On récupère le nombre d'heures en une journée dans les paramètres d'unités d'Odoo.
        if line_qty < hours_in_day :
            SAU = "H"
            QTY = line_qty
            if self.sinergis_product_id.type == "PME":
                line_price_unit = self.env['ir.config_parameter'].sudo().get_param('sinergis_x3.hour_list_price_pme')
            elif self.sinergis_product_id.type == "MGE":
                line_price_unit = self.env['ir.config_parameter'].sudo().get_param('sinergis_x3.hour_list_price_mge')
        else :
            SAU = "J"
            QTY = line_qty/hours_in_day
            if self.sinergis_product_id.type == "PME":
                line_price_unit = self.env['ir.config_parameter'].sudo().get_param('sinergis_x3.day_list_price_pme')
            elif self.sinergis_product_id.type == "MGE":
                line_price_unit = self.env['ir.config_parameter'].sudo().get_param('sinergis_x3.day_list_price_mge')

        data_line = {
            "ITMREF" : line_product_format,
            "ITMDES" : line_description,
            "QTY" : QTY,
            "SAU" : SAU,
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
            # Vérification si le POOL Odoo est bien allumé dans X3:
            if "No Pool:" in str(response):
                return [False, f"Le POOL: {pool_alias} n'est pas démarré dans Sage X3. Veuillez vous rapprocher de l'administrateur X3."]
            else: # Sinon on affiche toute l'erreur
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

        # Création des lignes de texte dans X3 pour la commande pour y saisir la description de l'intervention
        if sinergis_x3_id:
            intervention_description = ""
            if self.origin == 'helpdesk':
                ticket_id = self.env['helpdesk.ticket'].search([('id','=',self.link_id)], limit=1)
                start_date = fields.Datetime.context_timestamp(self, ticket_id.x_sinergis_helpdesk_ticket_start_time).strftime('%d/%m/%Y %H:%M:%S')
                end_date = fields.Datetime.context_timestamp(self, ticket_id.x_sinergis_helpdesk_ticket_end_time).strftime('%d/%m/%Y %H:%M:%S')
                intervention_description = f"Intervention du {start_date} au {end_date} par {self.consultant.name} - Description : {ticket_id.x_sinergis_helpdesk_ticket_ticket_resolution}"
            elif self.origin == "calendar":
                event_id = self.env['calendar.event'].search([('id','=',self.link_id)], limit=1)
                start_date = fields.Datetime.context_timestamp(self, event_id.x_sinergis_calendar_event_start_time).strftime('%d/%m/%Y %H:%M:%S')
                end_date = fields.Datetime.context_timestamp(self, event_id.x_sinergis_calendar_event_end_time).strftime('%d/%m/%Y %H:%M:%S')
                intervention_description = f"Intervention du {start_date} au {end_date} par {self.consultant.name} - Description : {event_id.x_sinergis_calendar_event_desc_intervention}"
            intervention_description = markdown.markdown(intervention_description)
            intervention_description_beautiful = BeautifulSoup(intervention_description, 'html.parser')   
            data_line_text_soap = order_line_text_to_soap(sinergis_x3_id,intervention_description_beautiful.get_text(),'1',pool_alias=pool_alias, public_name="INSTEXLIG")
            response = requests.post(base_url+path_x3_orders, data=data_line_text_soap.encode('utf-8'), headers=headers, verify=False).content

        # On retourne True car le transfert a été effectué avec succès
        # On ajoute les données d'X3 pour l'ajout des infos dans Odoo
        return [True, {'sinergis_x3_id': sinergis_x3_id,
                       'sinergis_x3_price_subtotal': sinergis_x3_price_subtotal,
                       'sinergis_x3_price_total': sinergis_x3_price_total}]
    
    #=======================================
    #Transférer les activités vers XODOOACT#
    #=======================================

    # CHARGEMENT DES DONNEES X3

    # Fonction pour charger toutes les activités dans X3
    def load_x3_actions(self):
        #Stockage des données X3
        x3_actions_data = {}
        #x3_actions_ids = []
        # Chargement données Reverse Proxy
        user_rproxy = self.env['ir.config_parameter'].sudo().get_param('sinergis_x3.user_rproxy')
        password_rproxy = self.env['ir.config_parameter'].sudo().get_param('sinergis_x3.password_rproxy')
        authentication_token_rproxy = False
        if user_rproxy:
            authentication_token_rproxy = base64.b64encode(f"{user_rproxy}:{password_rproxy}".encode('utf-8')).decode("ascii")
        # Chargement authentification
        user_x3 = self.env['ir.config_parameter'].sudo().get_param('sinergis_x3.user_x3')
        password_x3 = self.env['ir.config_parameter'].sudo().get_param('sinergis_x3.password_x3')
        authentication_token = base64.b64encode(f"{user_x3}:{password_x3}".encode('utf-8')).decode("ascii")
        # Chargement URL
        base_url = self.env['ir.config_parameter'].sudo().get_param('sinergis_x3.base_url_x3')
        path_x3_actions = self.env['ir.config_parameter'].sudo().get_param('sinergis_x3.path_x3_actions')
        # Parametres
        url = base_url + path_x3_actions
        cookies = False # Initalisation des cookies
        count_per_page = 2 # Nombre d'items par page
        next_exists = True # Permet de savoir si une page existe ensuite

        if authentication_token_rproxy:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            headers = {'content-type': 'text/xml;charset=UTF-8',
            'Authorization': f'Basic {authentication_token}',
            'sinergisauthorization': f'Basic {authentication_token_rproxy}'}
        else:
            headers = {'content-type': 'text/xml;charset=UTF-8',
            'Authorization': f'Basic {authentication_token}'}

        count = 0
        #DEBUG : ERREUR X3 DONC POUR LE MOMENT ON BYPASS ÇA
        """
        while next_exists:
            print("Count : "+str(count))
            count += count_per_page
            response = requests.get(f"{url}&count={str(count_per_page)}",
                            headers=headers,
                            cookies=cookies,
                            verify=False)
            cookies = response.cookies
            response_content = response.content
            response_json = json.loads(response_content)

            if not "$links" in response_json:
                print("Impossible de se connecter à X3 pour charger les contrats annuels")
                raise ValidationError("Impossible de se connecter à X3 pour charger les contrats annuels")
            if not '$next' in response_json['$links']:
                next_exists = False
            else :
                url = response_json['$links']['$next']["$url"]
            #Chargement des données
            for resource in response_json['$resources']:
                x3_actions_data[str(resource['ODOO_ID'])] = resource['WRITE_DATE']
                #x3_actions_data.append({
                #"ODOO_ID": resource['ODOO_ID'],
                #"WRITE_DATE": resource['WRITE_DATE'],
                #})
                #x3_actions_ids.append("ODOO_ID")
        """
        return x3_actions_data

    # TRANSFORMATION DES DONNEES INTERNES

    def action_to_dict(self, action_id, company_id_transcode, user_transcode):
        object = {}
        object['SALFCY'] = company_id_transcode[action_id.company_id.id] if action_id.company_id.id in company_id_transcode else '' # Agence rattachée au client
        object['ODOOCLIENTID'] = action_id.client.id if action_id.client else '' # Identifiant du client Odoo
        object['BPCORD'] = action_id.client.sinergis_x3_code if action_id.client.sinergis_x3_code else '' # Code client X3
        object['CLIENT_NAME'] = action_id.client.name if action_id.client else '' # Nom du client
        object['REP'] = user_transcode[action_id.consultant.id] if action_id.consultant.id in user_transcode else '' # Consultant
        object['ODOO_ID'] = action_id.id # Identifiant
        object['CATEGORIE'] = action_id.origin # Calendrier ou assistance
        object['BILLING_TYPE'] = action_id.billing_type if action_id.billing_type else '' # Type de facturation
        object['ITEMLINEODOO'] = action_id.billing_order_line.product_id.name if action_id.billing_order_line else '' # Nom de l'article lié au devis ou au CH
        object['OBJET'] = action_id.name if action_id.name else '' # Objet de la facturation
        object['QTY'] = round(action_id.time,2) # Temps en heures
        object['UNITE'] = "H" # Unité de temps
        object['NUM_BDC'] = action_id.billing_order.name if action_id.billing_order else '' # Numéro de la commande
        object['DATE_BDC'] = action_id.billing_order.date_order.strftime("%Y%m%d%H%M%S") if action_id.billing_order.date_order else ''  # Date de commande
        object['PRODUCT'] = action_id.sinergis_product_id.name if action_id.sinergis_product_id else ''
        object['SUBPRODUCT'] = action_id.sinergis_subproduct_id.name if action_id.sinergis_subproduct_id else ''
        object['XTYPE'] = action_id.sinergis_product_id.type if action_id.sinergis_product_id else ''
        object['START'] = action_id.start_time.strftime("%Y%m%d%H%M%S") if action_id.start_time else ''
        object['ENDDAT'] = action_id.end_time.strftime("%Y%m%d%H%M%S") if action_id.end_time else ''
        object['FACT'] = action_id.billing_type
        object['PROJET'] = int(action_id.has_project)
        object['WRITE_DATE'] = action_id.action_write_date.strftime("%Y%m%d%H%M%S") if action_id.action_write_date else ''
        return object

    # ACTIVITES DES CLIENT EN REQUETE SOAP
    def start_actions_x3_synchro (self):
        # Chargement du transcodage
        company_id_transcode = {settings_company_transcode.company_id.id: settings_company_transcode.code for settings_company_transcode in self.env['sinergis_x3.settings.company'].search([])}
        user_transcode = {settings_user_transcode.user_id.id: settings_user_transcode.code for settings_user_transcode in self.env["sinergis_x3.settings.commercial"].search([])}

        # Chargement des données d'authentification
        pool_alias = self.env['ir.config_parameter'].sudo().get_param('sinergis_x3.pool_alias')
        public_name = self.env['ir.config_parameter'].sudo().get_param('sinergis_x3.public_name_actions')

        #Chargement des clients
        partner_id = self.env['res.partner'].search([('name','=','ZORG DISTRIBUTION')])
        x3_datas  = self.load_x3_actions()
        
        #Pour chaque partner
        j = 0
        #action_ids = self.env["sinergis.myactions"].search([('client','=', partner_id.id)])
        action_ids = self.env["sinergis.myactions"].search([], limit=10000000)
        for action_id in action_ids:
            print(str(j))
            action_id_str = str(action_id.id)
            if action_id_str in x3_datas:
                if x3_datas[action_id_str] != action_id.action_write_date.strftime("%Y-%m-%d %H:%M:%S"):
                    #Update
                    print(f"Id: {action_id_str} exists and different write_date")
            else:
                #New
                print(f"New id : {action_id_str}")
                action_id_data = self.action_to_dict(action_id, company_id_transcode, user_transcode)
                data_soap = action_to_soap(action_id_data, pool_alias, public_name)
                print(data_soap)
                # === Envoie des données vers X3 ===
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
                public_name = self.env['ir.config_parameter'].sudo().get_param('sinergis_x3.public_name_actions')
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
                #Connection to X3
                base_url = self.env['ir.config_parameter'].sudo().get_param('sinergis_x3.base_url_x3')
                path_x3_actions = self.env['ir.config_parameter'].sudo().get_param('sinergis_x3.path_x3_orders')
                response = requests.post(base_url+path_x3_actions, data=data_soap.encode('utf-8'), headers=headers, verify=False).content
                j+=1
                try:
                    response_dict = xmltodict.parse(response)
                    status = response_dict["soapenv:Envelope"]["soapenv:Body"]["wss:saveResponse"]["saveReturn"]["status"]["#text"]
                    if status != "1":
                        print(f'Erreur pour ID : {action_id_str} : {response.content}')
                    else:
                        print("ID : {action_id_str} créé dans X3 !")
                except:
                    print(f"Erreur dans la lecture de l'ID : {action_id_str}. Erreur : {response}")
                
                # Si le status n'est pas à "1", il y a une erreur
                
                #print(headers)
                #print(base_url+path_x3_actions)
                #print(response)
        




