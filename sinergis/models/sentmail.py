from odoo import models, fields, api

class SinergisMovementCountry(models.Model):
    _name = "sinergis.sentmail"
    _description = "Mails envoyés"
    x_sinergis_sent_email_email = fields.One2many('mail.mail',compute="_compute_email",readonly=True)

    @api.depends('x_sinergis_sent_email_email')
    def _compute_x_sinergis_sent_email_email (self):
        for event in self:
            self.x_sinergis_helpdesk_ticket_taches = self.env["mail.mail"]
