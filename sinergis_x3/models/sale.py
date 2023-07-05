from odoo import models, fields, api
from odoo.exceptions import ValidationError
from base64 import b64encode
from datetime import datetime

from odoo.addons.sinergis_x3.utils.soap import order_to_soap, order_line_text_to_soap

import base64
import requests
import urllib3
import xmltodict

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    is_hostable = fields.Boolean(related="product_id.is_hostable")
    is_ch = fields.Boolean(related="product_id.is_ch")
    hosted = fields.Boolean(string="Hébergé", default=False)
    ch_multi = fields.Boolean(string="CH MULTI", default=False)

class SaleOrder(models.Model):
    _inherit = "sale.order"

    sinergis_x3_company_id = fields.Many2one("sinergis_x3.settings.company", string="Site de vente X3")

    hostable_in_order_line = fields.Boolean(compute="_compute_hostable_in_order_line")
    ch_in_order_line = fields.Boolean(compute="_compute_ch_in_order_line") # Si il y a un contrat d'heures dans les lignes de commande
    sinergis_x3_transfered = fields.Boolean(default=False) # Permet de savoir si le devis a déjà été transféré vers X3
    sinergis_x3_id = fields.Char(string="Numéro X3")
    sinergis_x3_price_total = fields.Float(string="Total TTC dans X3 (€)", default=False)
    sinergis_x3_correct_price = fields.Boolean(compute="_compute_sinergis_x3_correct_price")
    sinergis_x3_log = fields.One2many(
        "sale.order.odoo_x3_log", "sale_id", string="Odoo-X3 log", readonly=True
    )

    sinergis_x3_partner_has_codex3 = fields.Boolean(compute="_compute_sinergis_x3_partner_has_codex3")

    @api.onchange("partner_id")
    def onchange_partner_id_sinergis_x3(self):
        if not self.sinergis_x3_company_id:
            self.sinergis_x3_company_id = self.env["sinergis_x3.settings.company"].search([("company_id","=",self.partner_id.company_id.id)], limit=1)

    @api.depends("sinergis_x3_partner_has_codex3")
    def _compute_sinergis_x3_partner_has_codex3(self):
        for rec in self:
            if rec.partner_id.sinergis_x3_code:
                rec.sinergis_x3_partner_has_codex3 = True
            else:
                rec.sinergis_x3_partner_has_codex3 = False

    @api.depends("sinergis_x3_correct_price")
    def _compute_sinergis_x3_correct_price (self):
        for rec in self:
            if rec.amount_total != rec.sinergis_x3_price_total and rec.sinergis_x3_transfered:
                rec.sinergis_x3_correct_price = False
            else:
                rec.sinergis_x3_correct_price = True 

    #Bouton qui informe que la commande est bien synchronisée su Odoo
    def sinegis_x3_header_connected (self):
        return True

    def sinegis_x3_header_disconnected(self):
        self.send_order_to_x3()
        return True

    def create_log(self, content, log_type):
        self.env["sale.order.odoo_x3_log"].create({
            "sale_id" : self.id,
            "name" : content,
            "type" : log_type
            })

    def send_order_to_x3(self):
        enable = self.env['ir.config_parameter'].sudo().get_param('sinergis_x3.enable')

        # Vérification si la synchronisation est activée ou non
        if not enable:
            return True
        
        # Vérification si tous les sous-produits sont bien définis
        for line in self.order_line:
            if line.product_id and not line.x_sinergis_sale_order_line_subproduct_id:
                if self.env["sinergis_x3.settings.product.template"].search([("product_template_id","=",line.product_id.id),("format","ilike","{subproduct}")]):
                    raise ValidationError(f"Veuillez indiquer un sous-produit pour : {line.product_id.name}")


        # Ne pas permettre deux transferts sur le même devis
        if self.sinergis_x3_transfered:
            self.create_log(content="Le devis est passé en bon de commande mais un transfert avait déjà été effectué sur celui-ci.", log_type="warning")
            return True

        missing_data = [] # Tableau qui comprend toutes les données manquantes

        commercial = self.env["sinergis_x3.settings.commercial"].search([("user_id","=",self.user_id.id)], limit=1).code
        if not self.sinergis_x3_company_id :
            missing_data.append(f"site de vente X3 ({self.sinergis_x3_company_id.name})")
        if not commercial :
            missing_data.append(f"transcodage du commercial ({self.user_id.name})")
        if not self.partner_id.sinergis_x3_code:
            missing_data.append(f"code X3 du client ({self.partner_id.name})")

        data = {"SALFCY" : self.sinergis_x3_company_id.code,
                "SOHTYP" : "NEW",
                "CUSORDREF " : self.x_sinergis_sale_order_objet,
                "X_DEVODOO" : self.name,
                "ORDDAT" : self.date_order.strftime("%Y%m%d") if self.date_order else datetime.now().strftime("%Y%m%d"),
                "BPCORD" : self.partner_id.sinergis_x3_code,
                "REP" : commercial,
                "REP(1)" : False,
                "DEMDLVDAT" : False}
        
        #Construction des données articles
        data_lines = []
        for line in self.order_line:
            if line.product_id:
                sinergis_product = self.env["sinergis_x3.settings.sinergis_product"].search([("sinergis_product_id","=",line.x_sinergis_sale_order_line_product_id.id)], limit=1).code
                sinergis_subproduct = self.env["sinergis_x3.settings.sinergis_subproduct"].search([("sinergis_subproduct_id","=",line.x_sinergis_sale_order_line_subproduct_id.id)], limit=1).code
                hosted = self.env["sinergis_x3.settings.hostable"].search([("hosted","=",line.hosted)], limit=1).code
                uom = self.env["sinergis_x3.settings.uom"].search([("uom_id","=",line.product_uom.id)], limit=1).code
                if not hosted:
                    missing_data.append(f"transcodage de l'état Hébergé")
                if not sinergis_product :
                    missing_data.append(f"transcodage du produit Sinergis ({self.x_sinergis_sale_order_product_new.name})")
                
                product_format = self.env["sinergis_x3.settings.product.template"].search([("product_template_id","=",line.product_id.id)], limit=1).format
                if product_format :
                    product_format = product_format.replace("{product}", sinergis_product)
                    # Load the subproduct
                    if "{subproduct}" in product_format:
                        if sinergis_subproduct:
                            product_format = product_format.replace("{subproduct}", sinergis_subproduct)
                        else :
                            product_format = product_format.replace("{subproduct}", "")
                    # Load the hosted code
                    product_format = product_format.replace("{hosted}", hosted)
                    # Load the UoM code
                    if uom:
                        product_format = product_format.replace("{uom}", uom)

                    # Check if multi-product CH
                    if line.ch_multi:
                        if " MGE" in line.product_id.name:
                            product_format = "CHMGE"
                        else:
                            product_format = "CHPME"

                    # Creating the line data
                    data_line={
                        "ITMREF" : product_format,
                        "ITMDES" : line.name.split("\n")[0],
                        "QTY" : str(line.product_uom_qty),
                        "SAU" : uom,
                        "GROPRI" : str(line.price_unit),
                        "DISCRGVAL1" : str(line.discount),
                        "CPRPRI" : str(line.purchase_price),
                        "TEXT": str(line.name) # Désignation de la ligne
                    }
                    data_lines.append(data_line)
                else:
                    missing_data.append(f"pas de format pour l'article ({line.product_id.name})")

        if len(missing_data) > 0:
            self.create_log(content=f"Echec du transfert ! Éléments manquants : {','.join(missing_data)} ", log_type="danger")
            return True


        data["lines"] = data_lines
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
        self.create_log(content=f"DEBUG : {data_soap}", log_type="warning")
        #Connection to X3
        base_url = self.env['ir.config_parameter'].sudo().get_param('sinergis_x3.base_url_x3')
        path_x3_orders = self.env['ir.config_parameter'].sudo().get_param('sinergis_x3.path_x3_orders')
        response = requests.post(base_url+path_x3_orders, data=data_soap.encode('utf-8'), headers=headers, verify=False).content
        try:
            response_dict = xmltodict.parse(response)
            status = response_dict["soapenv:Envelope"]["soapenv:Body"]["wss:saveResponse"]["saveReturn"]["status"]["#text"]
        except:
            self.create_log(content=f"La réponse obtenue par le serveur n'est pas correcte. Réponse : {response}", log_type="danger")
            return True
        
        # S'il y a une erreur dans la requête
        if status != "1":
            if "Erreur zone [M:SOH4]ITMREF" in str(response):
                code_list = []
                for line in data_lines:
                    code_list.append(line['ITMREF'])
                self.create_log(content=f"Erreur rencontrée sur X3, le code article n'est pas reconnu. Liste des codes articles : {','.join(code_list)}", log_type="danger")
            else:
                self.create_log(content=f"Erreur rencontrée sur X3! Réponse : {response}", log_type="danger")
            return True
        
        # On récupère le code X3 de la commande crée
        sinergis_x3_id = False
        try:
            result_xml = response_dict["soapenv:Envelope"]["soapenv:Body"]["wss:saveResponse"]["saveReturn"]["resultXml"]["#text"]
            result_xml = result_xml.replace("""'<?xml version="1.0" encoding="UTF-8"?>""","")
            result_dict = xmltodict.parse(result_xml)            
            sinergis_x3_price_total = False
            for grp in result_dict["RESULT"]["GRP"]:
                if grp["@ID"] == "SOH0_1":
                    for fld in grp["FLD"]:
                        if fld["@NAME"] == "SOHNUM":
                            sinergis_x3_id = fld["#text"]
                if grp["@ID"] == "SOH4_4":
                    for fld in grp["FLD"]:
                        if fld["@NAME"] == "ORDINVATI":
                            sinergis_x3_price_total = fld["#text"]
            self.sinergis_x3_id = sinergis_x3_id
            self.sinergis_x3_price_total = sinergis_x3_price_total
        except:
            self.create_log(content=f"Récupération du SOHNUM et du total TTC de la nouvelle commande impossible", log_type="warning")
                

        # On marque le devis comme transféré
        self.sinergis_x3_transfered = True

        # Création des lignes de texte dans X3
        i=1
        if sinergis_x3_id != False:
            for line in self.order_line:
                if line.product_id:
                    if line.product_id.transfer_description:
                        line_name_array = line.name.split("\n")
                        if len(line_name_array) > 1:
                            data_line_text_soap = order_line_text_to_soap(sinergis_x3_id,"".join(line_name_array[1:]),str(i),pool_alias=pool_alias, public_name="INSTEXLIG")
                            response = requests.post(base_url+path_x3_orders, data=data_line_text_soap.encode('utf-8'), headers=headers, verify=False).content
                    i+=1

        # On ajoute dans le log l'information de synchronisation
        self.create_log(content=f"Transféré avec succès vers X3", log_type="success")
        

    @api.depends("hostable_in_order_line", "order_line")
    def _compute_hostable_in_order_line(self):
        for rec in self:
            hostable_in_order_line = False
            for line in rec.order_line:
                if line.is_hostable :
                    hostable_in_order_line = True
            rec.hostable_in_order_line = hostable_in_order_line

    @api.depends("ch_in_order_line", "order_line")
    def _compute_ch_in_order_line(self):
        for rec in self:
            ch_in_order_line = False
            for line in rec.order_line:
                if line.is_ch:
                    ch_in_order_line = True
            rec.ch_in_order_line = ch_in_order_line


    # Envoyer la commande vers X3 lors de la confirmation du devis
    def write(self, values):
        sale_order = super(SaleOrder, self).write(values)
        if "state" in values :
            if values["state"] == "sale":
                self.send_order_to_x3()
        return sale_order
    
class SaleOrderOdooX3Log (models.Model):
    _name = "sale.order.odoo_x3_log"
    _description = "Informations sur la synchronisation Odoo-X3 du bon de commande"
    
    date = fields.Datetime("Date", default=lambda self: datetime.now().strftime("%Y-%m-%d %H:%M:%S"), readonly=True)
    sale_id = fields.Many2one("sale.order",string="Vente",required=True,ondelete="cascade")
    name = fields.Text(string="Information",required=True)
    type = fields.Selection([('success', 'success'),('danger', 'danger'),('warning', 'warning')], string="Type")