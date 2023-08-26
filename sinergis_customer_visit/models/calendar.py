from odoo import models, fields, api

class CalendarEvent(models.Model):
    _inherit = "calendar.event"

    is_visit = fields.Boolean(string="Est une visite ?",default=False)
    visit_type = fields.Selection([('on_site', 'Sur site'),('phone', 'Par téléphone')], string="Type de visite")
    

    @api.onchange("is_visit")
    def on_change_is_visit (self):
        if self.is_training == False:
            self.visit_type = False

