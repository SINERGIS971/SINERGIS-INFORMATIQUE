from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"
    x_sinergis_account_analytic_line_user_id = fields.Many2one('res.users', string="Employé")
    x_sinergis_account_analytic_line_task_id = fields.Many2one('project.task', string="Tâche")
