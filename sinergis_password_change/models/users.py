from odoo import api, models, fields, _, SUPERUSER_ID
from odoo.exceptions import ValidationError

from datetime import datetime, timedelta

class ResUsers(models.Model):
    _inherit = "res.users"

    x_sinergis_res_users_password_last_update = fields.Datetime(string="Date du dernier changement de mot de passe", readonly=True, default=lambda self: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def x_sinergis_res_users_password_change_password(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'sinergis_change_password',
            'target': 'new',
        }
    
    @api.model
    def sinergis_get_last_update(self):
        return self.env.user.x_sinergis_res_users_password_last_update
    
    @api.model
    def sinergis_action_get(self):
        if self.env.user.employee_id:
            return self.env['ir.actions.act_window']._for_xml_id('sinergis_password_change.res_users_action_my')
        return self.sudo().env.ref('sinergis_password_change.res_users_action_my').read()[0]