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

    # Transfert Odoo - X3

    def _send_order_for_x3 (self):
        product_code = self.env["sinergis_x3.settings.sinergis_product"].search([("sinergis_product_id","=",self.sinergis_product_id.id)], limit=1).code
        subproduct_code = self.env["sinergis_x3.settings.sinergis_subproduct"].search([("sinergis_subproduct_id","=",self.sinergis_subproduct_id.id)], limit=1).code
        if not product_code:
            return [False, f"Le produit {self.sinergis_product_id} n'est pas transcodé."]
        if not subproduct_code:
            return [False, f"Le sous-produit {self.sinergis_subproduct_id} n'est pas transcodé."]
        
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

        data = {"SALFCY" : sinergis_x3_company_id.code,
                "SOHTYP" : "NEW",
                "CUSORDREF " : self.name,
                "X_DEVODOO" : "",
                "ORDDAT" : datetime.now().strftime("%Y%m%d"),
                "BPCORD" : partner_id_x3_code,
                "REP" : commercial,
                "REP(1)" : False,
                "DEMDLVDAT" : False}
        
        line_product_format = f"I{product_code}{subproduct_code}PH"
        if self.date:
            line_description = f"Intervention le {self.date.strftime('%d/%m/%Y %H:%M:%S')}"
        else :
            line_description = "Intervention"
        line_qty = self.time
        line_text = f"Intervention par {self.consultant.name}"
        
        #DEBUG
        line_price_unit = 10

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
        #Connection to X3
        base_url = self.env['ir.config_parameter'].sudo().get_param('sinergis_x3.base_url_x3')
        path_x3_orders = self.env['ir.config_parameter'].sudo().get_param('sinergis_x3.path_x3_orders')
        response = requests.post(base_url+path_x3_orders, data=data_soap.encode('utf-8'), headers=headers, verify=False).content
        
        raise ValidationError(response.content)
        try:
            response_dict = xmltodict.parse(response)
            status = response_dict["soapenv:Envelope"]["soapenv:Body"]["wss:saveResponse"]["saveReturn"]["status"]["#text"]
        except:
            return True

        return True