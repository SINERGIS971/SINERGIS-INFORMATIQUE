from odoo import api, models, fields, _, SUPERUSER_ID
from odoo.exceptions import ValidationError

from datetime import datetime, timedelta

class SinergisHotlinePlanningEvent(models.Model):
    _name = "sinergis_hotline_planning.event"
    _description = "Évènement du planning de la hotline"

    date = fields.Date(string="Jour", required=True)
    user_ids = fields.Many2many('res.users', string="Consultants")