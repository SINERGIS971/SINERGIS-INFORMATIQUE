from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ResUsers(models.Model):
    _inherit = "res.users"

    x_sinergis_res_users_initials = fields.Char(string="Initiales")
    x_sinergis_res_users_tampon_signature = fields.Image(string="Signature document")
    x_sinergis_res_users_job = fields.Selection([('CONSULTANT', 'CONSULTANT'), ('COMMERCIAL', 'COMMERCIAL')], string="Profil")
    x_sinergis_res_users_is_employee = fields.Boolean(string="Est employé", compute="_compute_x_sinergis_res_users_is_employee")

    @api.depends('x_sinergis_res_users_is_employee')
    def _compute_x_sinergis_res_users_is_employee (self):
        for rec in self:
            rec.x_sinergis_res_users_is_employee = rec.has_group('base.group_user')