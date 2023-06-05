from odoo import models, fields, api
from odoo.exceptions import ValidationError

import requests

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    is_hostable = fields.Boolean(related="product_id.is_hostable")
    hosted = fields.Boolean(string="Hébergé", default=False)

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def send_order_to_x3(self, url):
        requests.get(url)