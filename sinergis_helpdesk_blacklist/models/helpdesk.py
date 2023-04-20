from odoo import models, fields, api
from odoo.exceptions import ValidationError

class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    def create (self, values):
        email = self.email
        if email in values:
            if self.env['helpdesk.ticket.blacklist'].search(('email', '=', email)):  # If email in blacklist
                return
        return super(HelpdeskTicket, self).write(values)



class HelpdeskTicketBlacklist(models.Model):
    _name = "helpdesk.ticket.blacklist"
    _description = "Ticket blacklist"
    _rec_name = "email"
    email = fields.Char(string="Email", required=True)
