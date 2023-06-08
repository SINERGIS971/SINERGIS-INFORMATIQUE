from odoo import api, models, fields, _, SUPERUSER_ID
from odoo.exceptions import ValidationError

from datetime import datetime, timedelta

class SinergisMailchimpSettingsCompanyTag(models.Model):
    _name = "sinergis_mailchimp.settings.company.tag"
    _description = "Configuration des tags des sociétés"

    name = fields.Char(string="Nom du tag", required=True)
    company_id = fields.Many2one("res.company", string="Société", required=True)