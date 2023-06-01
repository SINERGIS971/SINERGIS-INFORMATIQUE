from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = "res.company"

    x_sinergis_res_company_iban = fields.Char(string="IBAN")
    x_sinergis_res_company_bic = fields.Char(string="BIC")
    x_sinergis_forbid_task_creation = fields.Boolean(string="Interdire la création des tâches à la confirmation du devis", default=False)
