from datetime import datetime

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ResUsers(models.Model):
    _inherit = "res.users"

    x_sinergis_res_users_initials = fields.Char(string="Initiales")
    x_sinergis_res_users_tampon_signature = fields.Image(string="Signature document")
    x_sinergis_res_users_job = fields.Selection([('CONSULTANT', 'CONSULTANT'), ('COMMERCIAL', 'COMMERCIAL')], string="Profil")
    #2 Mars 2023 : Pour utiliser directement dans les "domain" la condition de "utilisateur est employé"
    x_sinergis_res_users_is_employee = fields.Boolean(string="Est employé", compute="_compute_x_sinergis_res_users_is_employee", store=True)

    # 9 Avril 2023 : Date du dernier changement du mot de passe pour la fonctionnalité "Changement de mot de passe tous les 90 jours"
    x_sinergis_res_users_password_last_update = fields.Datetime(string="Date du dernier changement de mot de passe", readonly=True)

    @api.depends('x_sinergis_res_users_is_employee')
    def _compute_x_sinergis_res_users_is_employee (self):
        for rec in self:
            rec.x_sinergis_res_users_is_employee = rec.has_group('base.group_user')

    @api.onchange('password')
    def onchange_password(self):
        self.x_sinergis_res_users_password_last_update = datetime.now()
