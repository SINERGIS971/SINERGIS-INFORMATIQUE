from odoo import models, fields, api
from odoo.exceptions import ValidationError

import requests

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    is_hostable = fields.Boolean(related="product_id.is_hostable")
    hosted = fields.Boolean(string="Hébergé", default=False)

class SaleOrder(models.Model):
    _inherit = "sale.order"

    hostable_in_order_line = fields.Boolean(compute="_compute_hostable_in_order_line")

    def send_order_to_x3(self):
        sale_location = self.env["sinergis_x3.settings.company"].search([("company_id","=",self.company_id.id)], limit=1).code
        if not sale_location :
            print("LOCATION")
            return
        sinergis_product = self.env["sinergis_x3.settings.sinergis_product"].search([("sinergis_product_id","=",self.x_sinergis_sale_order_product_new.id)], limit=1).code
        #if not sinergis_product :
        #    return
        commercial = self.env["sinergis_x3.settings.commercial"].search([("user_id","=",self.user_id.id)], limit=1).code
        if not commercial :
            print("COMMERCIAL")
            return
        if not sinergis_product :
            print("PRODUCT")
            return
        for line in self.order_line:
            sinergis_subproduct = self.env["sinergis_x3.settings.sinergis_subproduct"].search([("sinergis_subproduct_id","=",line.x_sinergis_sale_order_line_subproduct_id.id)], limit=1).code
            hosted = self.env["sinergis_x3.settings.hostable"].search([("hosted","=",line.hosted)], limit=1).code
            uom = self.env["sinergis_x3.settings.uom"].search([("uom_id","=",line.product_uom.id)], limit=1).code
        data = {"SALFCY" : sale_location,
                "Type" : "NEW",
                ""}
        requests.post('https://eow1b86drs2nu4d.m.pipedream.net/', json=data)

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