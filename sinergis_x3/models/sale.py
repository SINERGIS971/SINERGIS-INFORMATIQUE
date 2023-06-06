from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime

import requests

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    is_hostable = fields.Boolean(related="product_id.is_hostable")
    hosted = fields.Boolean(string="Hébergé", default=False)

class SaleOrder(models.Model):
    _inherit = "sale.order"

    hostable_in_order_line = fields.Boolean(compute="_compute_hostable_in_order_line")
    sinergis_x3_transfered = fields.Boolean(default=False) # Permet de savoir si le devis a déjà été transféré vers X3
    sinergis_x3_log = fields.One2many(
        "sale.order.odoo_x3_log", "sale_id", string="Odoo-X3 log", readonly=True
    )


    #Bouton qui informe que la commande est bien synchronisée su Odoo
    def sinegis_x3_header_connected (self):
        return True

    def sinegis_x3_header_disconnected(self):
        return True

    def send_order_to_x3(self):
        missing_data = []

        sale_location = self.env["sinergis_x3.settings.company"].search([("company_id","=",self.company_id.id)], limit=1).code
        sinergis_product = self.env["sinergis_x3.settings.sinergis_product"].search([("sinergis_product_id","=",self.x_sinergis_sale_order_product_new.id)], limit=1).code
        commercial = self.env["sinergis_x3.settings.commercial"].search([("user_id","=",self.user_id.id)], limit=1).code
        if not sale_location :
            missing_data.append(f"Transcodage de l'agence Sinergis ({self.company_id.name})")
        if not commercial :
            missing_data.append(f"Transcodage du commercial ({self.user_id.name})")
        if not sinergis_product :
            missing_data.append(f"Transcodage du produit Sinergis ({self.x_sinergis_sale_order_product_new.name})")
        if not self.partner_id.x_sinergis_societe_ancien_code_x3:
            missing_data.append(f"Code X3 du client ({self.partner_id.name})")
        
        data = {"SALFCY" : sale_location,
                "SOHTYP" : "NEW",
                "CUSORDREF " : self.x_sinergis_sale_order_objet,
                "X_DEVODOO" : self.name,
                "ORDDAT" : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "BPCORD" : self.partner_id.x_sinergis_societe_ancien_code_x3,
                "REP" : commercial,
                "REP(1)" : False,
                "DEMDLVDAT" : False}
        
        #Construction des données articles
        data_lines = []
        for line in self.order_line:
            sinergis_subproduct = self.env["sinergis_x3.settings.sinergis_subproduct"].search([("sinergis_subproduct_id","=",line.x_sinergis_sale_order_line_subproduct_id.id)], limit=1).code
            hosted = self.env["sinergis_x3.settings.hostable"].search([("hosted","=",line.hosted)], limit=1).code
            uom = self.env["sinergis_x3.settings.uom"].search([("uom_id","=",line.product_uom.id)], limit=1).code
            if not hosted:
                missing_data.append(f"Transcodage de l'état Hébergé")
            if not uom:
                missing_data.append(f"Transcodage de l'unité de temps ({line.product_uom.name})")
            
            product_format = self.env["sinergis_x3.settings.product.template"].search([("id","=",line.product_id.id)], limit=1).format
            if product_format :
                product_format = product_format.replace("{product}", sinergis_product)
                # Load the subproduct
                if "{subproduct}" in product_format:
                    if sinergis_subproduct:
                        product_format = product_format.replace("{subproduct}", sinergis_subproduct)
                # Load the hosted code
                product_format = product_format.replace("{hosted}", hosted)
                # Load the UoM code
                product_format = product_format.replace("{uom}", uom)
                # Creating the line data
                data_line={
                    "ARTICLE" : product_format,
                    "ITMDES" : line.name,
                    "SAU" : uom,
                    "GROPRI" : line.price_subtotal,
                    "DISCRGVAL1" : line.discount,
                    "CPRPRI" : line.margin,
                }
                data_lines.append(data_line)
            else:
                missing_data.append(f"Pas de format pour l'article ({line.product_id.name})")

        if len(missing_data) > 0:
            self.env["sale.order.odoo_x3_log"].create({
                "sale_id" : self.id,
                "name" : f"Echec du transfert ! Éléments manquants : {','.join(missing_data)} ",
                "type" : "danger"
            })
            return True


        data["lines"] = data_lines

        #Connection to X3
        base_url = self.env['ir.config_parameter'].sudo().get_param('sinergis_x3.base_url_x3')
        path_x3_orders = self.env['ir.config_parameter'].sudo().get_param('sinergis_x3.path_x3_orders')
        requests.post(base_url+path_x3_orders, json=data)

        # On marque le devis comme transféré
        self.sinergis_x3_transfered = True
        
        # On ajoute dans le log l'information de synchronisation
        self.env["sale.order.odoo_x3_log"].create({
            "sale_id" : self.id,
            "name" : "Transféré avec succès vers X3",
            "type" : "success"
        })

    @api.depends("hostable_in_order_line", "order_line")
    def _compute_hostable_in_order_line(self):
        for rec in self:
            hostable_in_order_line = False
            for line in rec.order_line:
                if line.is_hostable :
                    hostable_in_order_line = True
            rec.hostable_in_order_line = hostable_in_order_line

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
    sale_id = fields.Many2one("sale.order",string="Vente",required=True)
    name = fields.Text(string="Information",required=True)
    type = fields.Selection([('success', 'success'),('danger', 'danger')], string="Type")