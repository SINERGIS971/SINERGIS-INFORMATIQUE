from odoo import models, fields, api
from odoo.exceptions import ValidationError

class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    blacklisted = fields.Boolean(compute="_compute_blacklisted")

    @api.depends("blacklisted")
    def _compute_blacklisted(self):
        if self.env["helpdesk.ticket.blacklist"].search([("email", "=", self.x_sinergis_helpdesk_ticket_contact_mail)]):
            self.blacklisted = True
        else:
            self.blacklisted = False

    def action_register_blacklist(self):
        self.env["helpdesk.ticket.blacklist"].create({"email" : self.x_sinergis_helpdesk_ticket_contact_mail})

    def action_unregister_blacklist(self):
        self.env["helpdesk.ticket.blacklist"].search([("email", "=", self.x_sinergis_helpdesk_ticket_contact_mail)]).unlink()


class HelpdeskTicketBlacklist(models.Model):
    _name = "helpdesk.ticket.blacklist"
    _description = "Ticket blacklist"
    _rec_name = "email"
    email = fields.Char(string="Email", required=True)
