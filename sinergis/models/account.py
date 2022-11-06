from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"
    x_sinergis_account_analytic_line_start_time = fields.Datetime(string="Début")
    x_sinergis_account_analytic_line_end_time = fields.Datetime(string="Fin")
    x_sinergis_account_analytic_line_user_id = fields.Many2one('res.users', string="Employé")
    x_sinergis_account_analytic_line_ticket_id = fields.Many2one('helpdesk.ticket', string="Ticket", readonly=True)
    x_sinergis_account_analytic_line_event_id = fields.Many2one('calendar.event', string="Evenement", readonly=True)
