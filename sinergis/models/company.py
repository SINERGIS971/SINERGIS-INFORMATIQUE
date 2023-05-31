from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = "res.company"

    x_sinergis_res_company_iban = fields.Char(string="IBAN")
    x_sinergis_res_company_bic = fields.Char(string="BIC")
    x_sinergis_allow_task_creation = fields.Boolean(string="Créer des tâches à la confirmation du devis", default=True)
