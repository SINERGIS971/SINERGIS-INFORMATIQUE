from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"
    x_sinergis_account_analytic_line_start_time = fields.Datetime(string="Début")
    x_sinergis_account_analytic_line_end_time = fields.Datetime(string="Fin")
    x_sinergis_account_analytic_line_user_id = fields.Many2one('res.users', string="Employé")
    x_sinergis_account_analytic_line_ticket_id = fields.Many2one('helpdesk.ticket', string="Ticket", readonly=True)
    x_sinergis_account_analytic_line_event_id = fields.Many2one('calendar.event', string="Evenement", readonly=True)

    # Ajouter au calendrier le traitement des tickets
    @api.model_create_multi
    def create(self, list_value):
        for vals in list_value:
            if "x_sinergis_account_analytic_line_user_id" in vals and "x_sinergis_account_analytic_line_ticket_id" in vals and "x_sinergis_account_analytic_line_start_time" in vals and "x_sinergis_account_analytic_line_end_time" in vals :
                #user_id = self.env['res.users'].search([('id','=',vals["x_sinergis_account_analytic_line_user_id"])])
                #ticket = self.env['helpdesk.ticket'].search([('id','=',vals["x_sinergis_account_analytic_line_ticket_id"])])
                context = {
                    "name" : "ASSISTANCE",
                    "user_id" : vals["x_sinergis_account_analytic_line_user_id"],
                    "start" : vals["x_sinergis_account_analytic_line_start_time"],
                    "stop" : vals["x_sinergis_account_analytic_line_end_time"],
                    "x_sinergis_calendar_event_account_analytic_line_id" : vals["x_sinergis_account_analytic_line_ticket_id"]
                }
                self.env["calendar.event"].create(context)
        account_analytic_line = super(AccountAnalyticLine, self).create(list_value)
        return account_analytic_line