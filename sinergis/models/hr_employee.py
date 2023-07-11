from odoo import models, fields, api

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    cv_file = fields.Binary(string="CV")
    cv_filename = fields.Char(string="Nom du fichier CV")
    cover_letter_file = fields.Binary(string="Lettre de motivation")
    cover_letter_filename = fields.Char(string="Nom de la lettre de motivation")
    
