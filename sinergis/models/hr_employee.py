from odoo import models, fields, api

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    cv_file = fields.Binary(string="CV (PDF)")
    cv_filename = fields.Char(string="Nom du fichier CV")
    cover_letter_file = fields.Binary(string="Lettre de motivation")
    cover_letter_filename = fields.Char(string="Nom de la lettre de motivation")

    certification_ids = fields.One2many('hr.employee.certification', 'employee_id', string="Certifications")

    x_sinergis_note = fields.Text(string="Notes")

    def download_cv_certification(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return {
            "type": "ir.actions.act_url",
            "url": f"{str(base_url)}/sinergis/download_cv_certification",
            "target": "new",
        }



class HrEmployeeCertification(models.Model):
    _name = "hr.employee.certification"
    _description = "Certification"
    
    employee_id = fields.Many2one('hr.employee')
    name = fields.Char(string="Nom du Certificat", required=True)
    file = fields.Binary(string="Fichier (PDF)", required=True)
    filename = fields.Char(string="Nom du fichier")
