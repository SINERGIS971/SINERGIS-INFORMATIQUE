from odoo import api, models, fields, _, SUPERUSER_ID
from odoo.exceptions import ValidationError

from datetime import datetime, timedelta

class SinergisMeetingRoomRoom(models.Model):
    _name = "sinergis_meeting_room.room"
    _description = "Salle de réunion"

    name = fields.Char(string='Reference', required=True)