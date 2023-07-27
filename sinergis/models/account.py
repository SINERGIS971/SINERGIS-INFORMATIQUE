from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"
    x_sinergis_account_analytic_line_start_time = fields.Datetime(string="Début")
    x_sinergis_account_analytic_line_end_time = fields.Datetime(string="Fin")
    x_sinergis_account_analytic_line_user_id = fields.Many2one('res.users', string="Employé")
    x_sinergis_account_analytic_line_ticket_id = fields.Many2one('helpdesk.ticket', string="Ticket", readonly=True)
    x_sinergis_account_analytic_line_event_id = fields.Many2one('calendar.event', string="Evenement", readonly=True)

    @api.model_create_multi
    def create(self, list_value):
        for vals in list_value:
            if "task_id" in vals and "unit_amount" in vals:
                task_id = self.env['project.task'].search([('id','=',vals['task_id'])])
                if task_id.project_id and task_id.project_id.company_id:
                    email_ids = self.env['project.task.ch_email'].search([('company_id','=',task_id.project_id.company_id.id)])
                    if email_ids and task_id.project_id.x_sinergis_project_project_is_ch:
                        unit_amount = vals['unit_amount']
                        for email_id in email_ids:
                            if email_id.limit_type == "percentage":
                                limit = email_id.limit/100 * task_id.planned_hours
                                limit_text = f"{str(email_id.limit)} %"
                            else:
                                limit = email_id.limit
                                limit_text = f"{str(email_id.limit)} h"
                            if task_id.remaining_hour > limit and task_id.remaining_hour - unit_amount < limit:
                                partner_name = task_id.sale_line_id.order_id.partner_id.name
                                mail_vals = {
                                    'email_to': email_id.email,
                                    'subject': f"Odoo - ALERTE CONTRAT D'HEURES - {partner_name}",
                                    'body_html': f"""
                                                    Bonjour,

                                                    Nous vous informons qu’il ne reste que {limit_text} sur le contrat d’heures {task_id.sale_line_id.order_id.name} de la société {partner_name}.

                                                    Heures prévues : {str(task_id.planned_hours)} h
                                                    Heures réalisées : {str(task_id.effective_hours)} h
                                                    Heures restantes : {str(task_id.remaining_hours)} h

                                                    - Odoo -
                                    """
                                }
                                self.env['mail.mail'].sudo().create(mail_vals).send()
        analytic_lines = super(AccountAnalyticLine, self).create(list_value)
        return analytic_lines