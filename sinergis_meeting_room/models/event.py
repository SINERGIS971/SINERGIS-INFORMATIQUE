from odoo import api, models, fields, _, SUPERUSER_ID
from odoo.exceptions import ValidationError

from datetime import datetime, timedelta

class SinergisMeetingRoomEvent(models.Model):
    _name = "sinergis_meeting_room.event"
    _description = "Évènements en salle de réunion Sinergis"
    _rec_name = "display_name"

    display_name = fields.Char(compute="_compute_display_name")
    name = fields.Char(string='Reference', required=True)
    user_id = fields.Many2one("res.users",string="Organisateur", default=lambda self: self.env.user, required=True)
    room_id = fields.Many2one("sinergis_meeting_room.room",string="Salle", required=True)
    calendar_event_id = fields.Many2one("calendar.event",default=False,ondelete='cascade', readonly=True)
    start_date = fields.Datetime(string='Début', required=True)
    end_date = fields.Datetime(string='Fin', required=True)

    def download_meeting_room_sheet(self):
        data = {
            "month": "Novembre",
            "year": "2023",
            "data": "<tr><td></td><td></td><td>1<br>Esteban ANTONIO-MOTA, Magalie LEZEAU</td><td>2<br>Esteban ANTONIO-MOTA, Magalie LEZEAU</td><td>3<br>Esteban ANTONIO-MOTA, Magalie LEZEAU</td></tr><tr><td>6<br>Esteban ANTONIO-MOTA, Magalie LEZEAU</td><td>7<br>Esteban ANTONIO-MOTA, Magalie LEZEAU</td><td>8<br></td><td>9<br></td><td>10<br></td></tr><tr><td>13<br></td><td>14<br></td><td>15<br></td><td>16<br></td><td>17<br></td></tr><tr><td>20<br></td><td>21<br></td><td>22<br></td><td>23<br></td><td>24<br></td></tr><tr><td>27<br></td><td>28<br></td><td>29<br></td><td>30<br></td></tr><tr></tr>",
        }
        return self.env.ref('sinergis_hotline_planning.sinergis_hotline_planning_event_sheet_report').report_action(self, data=data)

    def open_calendar_event(self):
        return {
            "name": "Évènement",
            "type": "ir.actions.act_window",
            "res_model": "calendar.event",
            "view_mode": "form",
            "res_id": self.calendar_event_id.id,
            "target": "new",
            }

    @api.depends("display_name")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = rec.user_id.name + " - " + rec.name

    @api.model_create_multi
    def create(self, list_value):
        for vals in list_value:
            start_date = vals['start_date']
            end_date = vals['end_date']
            room_id = vals["room_id"]
            confront_events = self.env['sinergis_meeting_room.event'].search(['|','|','&',('room_id','=',room_id),'&',('start_date','<',start_date),('end_date','>',start_date),'&',('start_date','<',end_date),('end_date','>',end_date),'&',('start_date','>',start_date),('end_date','<',end_date)])
            if confront_events:
                raise ValidationError('La salle de réunion est déjà réservée sur ce créneau.')
        events = super(SinergisMeetingRoomEvent, self).create(list_value)
        return events
    
    def unlink(self):
        ids = []
        for rec in self:
            if rec.calendar_event_id:
                ids.append(rec.calendar_event_id.id)
        super(SinergisMeetingRoomEvent, self).unlink()
        for id in ids:
            self.env['calendar.event'].search([('id','in',ids)]).sinergis_meeting_room_id = False
        return