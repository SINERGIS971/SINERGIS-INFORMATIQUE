# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError

from datetime import datetime

class ResPartner(models.Model):
    _inherit = "res.partner"

    x_sinergis_claims_ids = fields.One2many('res.partner.claims','partner_id',string='Réclamations')


class ResPartnerClaims (models.Model):
    _name = "res.partner.claims"
    _description = "Réclamations clients"
    
    name = fields.Char(string="Sujet", required=True)
    partner_id = fields.Many2one("res.partner",string="Client", required=True)
    date = fields.Datetime("Date de réclamation", default=lambda self: datetime.now().strftime("%Y-%m-%d %H:%M:%S"), required=True)
    contact_id = fields.Many2one("res.partner",string="Contact", required=True)
    user_id = fields.Many2one("res.users",string="Utilisateur", default=lambda self: self.env.user, required=True)
    description = fields.Html(string="Description")
    commercial_ids = fields.Many2many("res.users", string="Commerciaux à contacter")

    @api.onchange("partner_id")
    def onchange_partner_id (self):
        self.contact_id = False

    @api.model_create_multi
    def create(self, list_value):
        claims = super(ResPartnerClaims, self).create(list_value)
        partner_name = claims.partner_id.name
        for commercial_id in claims.commercial_ids:
            mail_vals = {
                'email_to': commercial_id.login,
                'subject': f"{partner_name} - Réclamation",
                'body_html': f"{claims.name}<br/><br/>{claims.description}",
            }
            self.env['mail.mail'].create(mail_vals).send()
        return claims
