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

    def send_order_to_x3(self, url):
        requests.get(url)

    @api.depends("hostable_in_order_line", "order_line")
    def _compute_hostable_in_order_line(self):
        for rec in self:
            hostable_in_order_line = False
            for line in rec.order_line:
                if line.is_hostable :
                    hostable_in_order_line = True
            rec.hostable_in_order_line = hostable_in_order_line

