from odoo import api, models, fields, _, SUPERUSER_ID
from odoo.exceptions import ValidationError

from datetime import datetime, timedelta

class SinergisSensitiveData(models.Model):
    _name = "sinergis_rgpd.sensitive_data"
    _description = "Données sensibles Sinergis"

    partner_id = fields.Many2one("res.partner", string="Société", required=True)
    user_id = fields.Many2one("res.users", string="Utilisateur",default=lambda self: self.env.user)
    name = fields.Char(string='Reference', required=True)
    deletion_date = fields.Datetime(string="Date de suppression",default=lambda self: fields.Datetime.now() + timedelta(days=30), required=True)