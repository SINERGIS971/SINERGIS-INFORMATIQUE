from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime


class CrmLead(models.Model):
    _inherit = "crm.lead"
    x_sinergis_crm_lead_contact = fields.Many2one("res.partner",string="Contact")

    @api.onchange("partner_id")
    def on_change_partner_id(self):
        self.x_sinergis_crm_lead_contact = False
