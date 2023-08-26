from odoo import models, fields, api

class CalendarEvent(models.Model):
    _inherit = "calendar.event"

    is_visit = fields.Boolean(string="Est une visite ?",default=False)
    visit_type = fields.Many2one("training",string="Type de visite",default=False)

    @api.onchange("is_visit")
    def on_change_is_visit (self):
        if self.is_training == False:
            self.visit_type = False

    