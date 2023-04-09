from datetime import datetime

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ResUsers(models.Model):
    _inherit = "res.users"

    x_sinergis_res_users_password_last_update = fields.Datetime(string="Date du dernier changement de mot de passe", readonly=True)

    @api.model
    def sinergis_action_get(self):
        if self.env.user.employee_id:
            return self.env['ir.actions.act_window']._for_xml_id('sinergis.res_users_action_my')
        return super(ResUsers, self).action_get()