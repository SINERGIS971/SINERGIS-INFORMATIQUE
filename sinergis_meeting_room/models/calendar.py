from odoo import models, fields, api

class SinergisMeetingRoomCalendarEvent(models.Model):
    _inherit = "calendar.event"

    sinergis_meeting_room_id = fields.Many2one("sinergis_meeting_room.room",string="Salle de formation")

    @api.model_create_multi
    def create(self, list_value):
        for vals in list_value:
            if "sinergis_meeting_room_id" in vals:
                name = vals['name']
                start_date = vals['start']
                end_date = vals['stop']
                room_id = vals['sinergis_meeting_room_id']
                room_event = self.env['sinergis_meeting_room.event'].create({
                    'name': name,
                    'start_date': start_date,
                    'end_date': end_date,
                    'room_id': room_id
                })
                room_event.sinergis_meeting_room_id = room_event.id
        events = super(SinergisMeetingRoomCalendarEvent, self).create(list_value)
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



        user_id = self.user_id

        if not self.env.user.has_group('sinergis.group_helpdesk_admin'): #Si l'utilisateur n'est pas dans le groupe des administrateurs de tickets
            if user_id != self.env.user and self.stage_id.name == "Résolu":
                raise ValidationError("Vous ne pouvez pas modifier un ticket cloturé qui ne vous est pas assigné.")
            if self.x_sinergis_helpdesk_ticket_client_bloque :
                raise ValidationError("Vous ne pouvez pas modifier le ticket d'un client bloqué. Merci de contacter un commercial ou un administrateur des tickets.")