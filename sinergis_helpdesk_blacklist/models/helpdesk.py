from odoo import models, fields, api
from odoo.exceptions import ValidationError

class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    blacklisted = fields.Boolean(compute="_compute_blacklisted", store=True)

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

    @api.model_create_multi
    def create(self, list_value):
        for vals in list_value:
            tickets = self.env['helpdesk.ticket'].search([('x_sinergis_helpdesk_ticket_contact_mail','=',vals['email'])])
            for ticket in tickets:
                ticket._compute_blacklisted()
        tickets = super(HelpdeskTicket, self).create(list_value)
        return tickets
