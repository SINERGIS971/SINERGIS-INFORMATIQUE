from odoo import api, models, fields, _, SUPERUSER_ID
from odoo.exceptions import ValidationError

from datetime import datetime, timedelta

class SinergisMeetingRoomEvent(models.Model):
    _name = "sinergis_meeting_room.event"
    _description = "Salle de réunion Sinergis"

    name = fields.Char(string='Reference', required=True)
    start_date = fields.Datetime(string='Début')
    end_date = fields.Datetime(string='Fin')