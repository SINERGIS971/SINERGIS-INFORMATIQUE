from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = "res.company"

    nda_number = fields.Char(string="Numéro NDA")
