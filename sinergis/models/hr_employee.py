from odoo import models, fields, api

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    cv_file = fields.Binary(string="CV")
    cv_filename = fields.Char(string="Nom du fichier CV")
    cover_letter_file = fields.Binary(string="Lettre de motivation")
    cover_letter_filename = fields.Char(string="Nom de la lettre de motivation")

    certification_ids = fields.One2many('hr.employee.certification', 'employee_id', string="Certifications")



class HrEmployeeCertification(models.Model):
    _name = "hr.employee.certification"
    _description = "Certification"
    
    employee_id = fields.Many2one('hr.employee')
    name = fields.Char(string="Nom du Certificat", required=True)
    file = fields.Binary(string="Fichier", required=True)
    filename = fields.Char(string="Nom du fichier")
