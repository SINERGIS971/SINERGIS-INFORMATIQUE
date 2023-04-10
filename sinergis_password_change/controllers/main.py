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
            return {'error': 'Vous ne pouvez laisser aucun mot de passe vide.'}
        if new_password != confirm_password:
            return {'error': 'Le nouveau mot de passe et sa confirmation doivent être identiques.'}

        msg = "Erreur, mot de passe non changé !"
        try:
            if request.env['res.users'].change_password(old_password, new_password):
                # Change last date update password
                if old_password != new_password :
                    request.env.user.write({'x_sinergis_res_users_password_last_update': datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
                    return {'new_password': new_password}
                else:
                    msg = "Votre nouveau mot de passe est identique à l'ancien."
        except AccessDenied as e:
            msg = e.args[0]
            if msg == AccessDenied().args[0]:
                msg = "L'ancien mot de passe que vous avez fourni est incorrect, votre mot de passe n'a pas été modifié."
        except UserError as e:
            msg = e.args[0]
        return {'error': msg}