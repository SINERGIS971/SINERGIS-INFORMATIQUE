from odoo import models, fields, api
from odoo.exceptions import ValidationError


class HelpdeskTicketBlacklist(models.Model):
    _name = "helpdesk.ticket.blacklist"
    _description = "Ticket blacklist"

    email = fields.Char(string="email", required=True)
