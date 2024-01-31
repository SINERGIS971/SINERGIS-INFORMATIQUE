from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime


class CrmLead(models.Model):
    _inherit = "crm.lead"
    x_sinergis_crm_lead_contact = fields.Many2one("res.partner",string="Contact")
    x_sinergis_crm_lead_contact_email = fields.Char(string="Email du contact", related="x_sinergis_crm_lead_contact.email")
    x_sinergis_crm_lead_contact_phone = fields.Char(string="Tel. du contact", related="x_sinergis_crm_lead_contact.phone")

    @api.onchange("partner_id")
    def on_change_partner_id(self):
        self.x_sinergis_crm_lead_contact = False
