import operator

import odoo

from odoo.http import request
from odoo.exceptions import AccessError, UserError, AccessDenied

class SinergisPasswordChange(http.Controller):
    @http.route('/web/session/change_sinergis_password', type='json', auth="user")
    def change_password(self, fields):
        old_password, new_password,confirm_password = operator.itemgetter('old_pwd', 'new_password','confirm_pwd')(
            {f['name']: f['value'] for f in fields})
        if not (old_password.strip() and new_password.strip() and confirm_password.strip()):
            return {'error': 'You cannot leave any password empty.'}
        if new_password != confirm_password:
            return {'error': 'The new password and its confirmation must be identical.'}

        msg = _("Error, password not changed !")
        try:
            if request.env['res.users'].change_password(old_password, new_password):
                return {'new_password': new_password}
        except AccessDenied as e:
            msg = e.args[0]
            if msg == AccessDenied().args[0]:
                msg = 'The old password you provided is incorrect, your password was not changed.'
        except UserError as e:
            msg = e.args[0]
        return {'error': msg}