from odoo import models, fields, api

class CalendarEvent(models.Model):
    _inherit = "calendar.event"

    is_visit = fields.Boolean(string="Est une visite ?",default=False)
    visit_type = fields.Selection([('on_site', 'Sur site'),('phone', 'Par téléphone')], string="Type de visite")
    

    @api.onchange("is_visit")
    def on_change_is_visit (self):
        if self.is_training == False:
            self.visit_type = False

    #@api.model
    #def create(self, values):
    #    event = super(CalendarEvent, self).create(values)
    #    if "is_visit" in values or "visit_type" in values:
    #        partner_id = event.x_sinergis_calendar_event_client
    #        if partner_id:
    #            partner_id._compute_partner_visits()
    #    return event

    #def write(self, values):
    #    event =  super(CalendarEvent, self).write(values)
    #    if "is_visit" in values or "visit_type" in values:
    #        partner_id = event.x_sinergis_calendar_event_client
    #        if partner_id:
    #            partner_id._compute_partner_visits()
    #    return event

