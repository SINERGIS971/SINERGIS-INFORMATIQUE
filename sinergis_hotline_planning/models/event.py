from odoo import api, models, fields, _, SUPERUSER_ID
from odoo.exceptions import ValidationError

from datetime import datetime, timedelta

class SinergisHotlinePlanningEvent(models.Model):
    _name = "sinergis_hotline_planning.event"
    _description = "Évènement du planning de la hotline"
    _rec_name = 'display_name'


    display_name = fields.Char(string="Nom", compute="_compute_display_name")
    date = fields.Date(string="Jour", required=True)
    user_ids = fields.Many2many('res.users', string="Consultants")

    @api.depends('display_name')
    def _compute_display_name (self):
        for rec in self:
            user_name = []
            for user_id in rec.user_ids:
                user_name.append(user_id.name)
            display_name = user_name.join(', ')
            rec.display_name = display_name
