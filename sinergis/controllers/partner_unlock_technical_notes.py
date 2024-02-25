import operator

import odoo

from odoo import http
from odoo.http import request
from odoo.exceptions import AccessError, UserError, AccessDenied

from datetime import datetime
from dateutil.relativedelta import relativedelta

# Permet d'autoriser à un utilisateur l'accès aux notes techniques des clients
class SinergisUnlockTechnicalNotes(http.Controller):
    @http.route('/web/session/unlock_technical_notes', type='json', auth="user")
    def confirm_partner_reminder(self, fields):
        password = operator.itemgetter('pass')({f['name']: f['value'] for f in fields})
        if not (password.strip()):
            return {'error': 'Mot de passe non renseigné'}
        correct_password = request.env['ir.config_parameter'].sudo().get_param('sinergis.technical_notes_password')
        if password == correct_password:
            request.env.user.x_sinergis_res_users_partner_technical_notes_limit = datetime.now() + relativedelta(minutes=10)
            return {}
        else:
            return {'error': f"Mot de passe incorrect"}