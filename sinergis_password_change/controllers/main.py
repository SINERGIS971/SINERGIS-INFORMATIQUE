import operator

import odoo

from datetime import datetime
from odoo import http
from odoo.http import request
from odoo.exceptions import AccessError, UserError, AccessDenied

class SinergisPasswordChange(http.Controller):
    @http.route('/web/session/change_sinergis_password', type='json', auth="user")
    def change_password(self, fields):
        old_password,new_password,confirm_password = operator.itemgetter('old_pwd', 'new_password','confirm_pwd')({f['name']: f['value'] for f in fields})
        if not (old_password.strip() and new_password.strip() and confirm_password.strip()):
            return {'error': 'You cannot leave any password empty.'}
        if new_password != confirm_password:
            return {'error': 'The new password and its confirmation must be identical.'}

        msg = "Error, password not changed !"
        try:
            if request.env['res.users'].change_password(old_password, new_password):
                # Change last date update password
                request.env.user.write({'x_sinergis_res_users_password_last_update': datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
                return {'new_password': new_password}
        except AccessDenied as e:
            msg = e.args[0]
            if msg == AccessDenied().args[0]:
                msg = 'The old password you provided is incorrect, your password was not changed.'
        except UserError as e:
            msg = e.args[0]
        return {'error': msg}