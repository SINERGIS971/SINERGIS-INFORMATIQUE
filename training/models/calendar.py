from odoo import models, fields, api

class CalendarEvent(models.Model):
    _inherit = "calendar.event"

    is_training = fields.Boolean(string="Est une formation ?",default=False)
    training_id = fields.Many2one("training",string="Formation",default=False)

    @api.onchange("is_training")
    def on_change_is_training (self):
        if self.is_training == False:
            self.training_id = False
