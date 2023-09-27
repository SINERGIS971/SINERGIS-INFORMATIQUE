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
                    'room_id': room_id.id,
                    'calendar_event_id': event.id
                })
        return events
    
    def write(self, values):
        for rec in self:
            name = values.get('name', rec.name)
            start_date = values.get('start', rec.start)
            end_date =values.get('stop', rec.stop)
            if "sinergis_meeting_room_id" in values:
                self.env['sinergis_meeting_room.event'].search([('calendar_event_id','=',rec.id)]).unlink()
                room_id = values['sinergis_meeting_room_id']
                if room_id:
                    self.env['sinergis_meeting_room.event'].create({
                        'name': name,
                        'start_date': start_date,
                        'end_date': end_date,
                        'room_id': room_id,
                        'calendar_event_id': rec.id
                    })
            else:
                room_event = self.env['sinergis_meeting_room.event'].search([('calendar_event_id','=',rec.id)])
                if room_event:
                    room_event.write({
                        'name': name,
                        'start_date': start_date,
                        'end_date': end_date,
                    })
        return super(SinergisMeetingRoomCalendarEvent, self).write(values)
    
    def unlink(self):
        for rec in self:
            self.env['sinergis_meeting_room.event'].search([('calendar_event_id', '=', rec.id)]).unlink()
        return super(SinergisMeetingRoomCalendarEvent, self).unlink()