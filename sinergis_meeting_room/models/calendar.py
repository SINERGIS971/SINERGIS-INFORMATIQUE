from odoo import models, fields, api

class SinergisMeetingRoomCalendarEvent(models.Model):
    _inherit = "calendar.event"

    sinergis_meeting_room_id = fields.Many2one("sinergis_meeting_room.room",string="Salle de réunion")

    @api.model_create_multi
    def create(self, list_value):
        events = super(SinergisMeetingRoomCalendarEvent, self).create(list_value)
        for event in events:
            if event.sinergis_meeting_room_id:
                name = event.name
                start_date = event.start
                end_date = event.stop
                room_id = event.sinergis_meeting_room_id
                self.env['sinergis_meeting_room.event'].create({
                    'name': name,
                    'start_date': start_date,
                    'end_date': end_date,
                    'room_id': room_id,
                    'calendar_event_id': event.id
                })
        return events
    
    def write(self, values):
        name = values.get('name', self.name)
        start_date = values.get('start', self.start)
        end_date =values.get('stop', self.stop)
        if "sinergis_meeting_room_id" in values:
            self.env['sinergis_meeting_room.event'].search([('calendar_event_id','=',self.id)]).unlink()
            room_id = values['sinergis_meeting_room_id']
            self.env['sinergis_meeting_room.event'].create({
                'name': name,
                'start_date': start_date,
                'end_date': end_date,
                'room_id': room_id,
                'sinergis_meeting_room_id': self.id
            })
        else:
            room_event = self.env['sinergis_meeting_room.event'].search([('calendar_event_id','=',self.id)])
            if room_event:
                room_event.write({
                    'name': name,
                    'start_date': start_date,
                    'end_date': end_date,
                })