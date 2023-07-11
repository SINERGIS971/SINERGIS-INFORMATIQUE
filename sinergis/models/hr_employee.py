from odoo import models, fields, api

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    cv_file = fields.Binary(string="CV")
    cv_filename = fields.Char(string="Nom du fichier CV")
    
