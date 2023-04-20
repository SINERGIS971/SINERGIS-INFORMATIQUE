from odoo import models, fields, api
from odoo.exceptions import ValidationError

class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"


class HelpdeskTicketBlacklist(models.Model):
    _name = "helpdesk.ticket.blacklist"
    _description = "Ticket blacklist"
    _rec_name = "email"
    email = fields.Char(string="Email", required=True)
