from odoo import api, models, fields, _, SUPERUSER_ID
from odoo.exceptions import ValidationError

from datetime import datetime, timedelta

class SinergisMeetingRoomEvent(models.Model):
    _name = "sinergis_meeting_room.event"
    _description = "Évènements en salle de réunion Sinergis"

    name = fields.Char(string='Reference', required=True)
    room_id = fields.Many2one("sinergis_meeting_room.room",string="Salle")
    start_date = fields.Datetime(string='Début')
    end_date = fields.Datetime(string='Fin')