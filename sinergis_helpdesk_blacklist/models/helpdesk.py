from odoo import models, fields, api
from odoo.exceptions import ValidationError

class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    blacklisted = fields.Boolean(compute="_compute_blacklisted", store=True)

    @api.depends("blacklisted")
    def _compute_blacklisted(self):
        for rec in self:
            if self.env["helpdesk.ticket.blacklist"].search([("email", "=", rec.x_sinergis_helpdesk_ticket_contact_mail)]):
                rec.blacklisted = True
            else:
                rec.blacklisted = False

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
        tickets = super(HelpdeskTicketBlacklist, self).create(list_value)
        for vals in list_value:
            concerned_tickets = self.env['helpdesk.ticket'].search([('x_sinergis_helpdesk_ticket_contact_mail','=',vals['email'])])
            for concerned_ticket in concerned_tickets:
                concerned_ticket._compute_blacklisted()
        return tickets

    def unlink(self):
        email = self.email
        super(HelpdeskTicketBlacklist, self).unlink()
        concerned_tickets = self.env['helpdesk.ticket'].search([('x_sinergis_helpdesk_ticket_contact_mail','=',email)])
        for concerned_ticket in concerned_tickets:
            concerned_ticket._compute_blacklisted()
        return