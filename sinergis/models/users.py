from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ResUsers(models.Model):
    _inherit = "res.users"

    x_sinergis_res_users_initials = fields.Char(string="Initiales")
    x_sinergis_res_users_tampon_signature = fields.Image(string="Signature document")
    x_sinergis_res_users_job = fields.Selection([('CONSULTANT', 'CONSULTANT'), ('COMMERCIAL', 'COMMERCIAL')], string="Profil")
