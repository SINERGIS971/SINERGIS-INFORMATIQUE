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

    def write(self, vals):
        if "stage_id" in vals :
            stage_id = self.env['crm.stage'].search([('id','=',vals['stage_id'])])
            if stage_id.name == "% - PERDU":
                id = vals.get("id", self.id)
                sale_ids = self.env['sale.order'].search([('opportunity_id','=',id)])
                for sale_id in sale_ids:
                    sale_id.active = False
        lead = super(CrmLead, self).write(vals)
        return lead
