import operator

import odoo

from datetime import datetime
from odoo import http
from odoo.http import request
from odoo.exceptions import AccessError, UserError, AccessDenied

class SinergisPasswordChange(http.Controller):
    @http.route('/web/session/change_sinergis_password', type='json', auth="user")
    def confirm_partner_reminder(self, fields):
        datetime_reminder = operator.itemgetter('datetime_reminder')({f['name']: f['value'] for f in fields})
        if not (datetime_reminder.strip()):
            return {'error': 'Vous devez renseigner une date'}