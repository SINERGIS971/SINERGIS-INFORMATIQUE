import operator

import odoo

from datetime import datetime
from odoo import http
from odoo.http import request
from odoo.exceptions import AccessError, UserError, AccessDenied

class SinergisVacationBuilder(http.Controller):
    @http.route('/web/session/sinergis_vacation_builder', type='json', auth="user")
    def change_password(self, fields):
        if request.env.user.has_group('base.group_user') == False:
            return

        start_date,start_mid_day,end_date,end_mid_day,daily_hours = operator.itemgetter('start_date', 'start_mid_day','end_date','end_mid_day','daily_hours')({f['name']: f['value'] for f in fields})
        if not (start_date.strip() and end_date.strip()):
            return {'error': 'Veuillez renseigner correctement les dates.'}

        if not isinstance(daily_hours, int):
            return {'error': "Veuillez saisir correctement votre nombre d'heures par jour."}

        if daily_hours <= 0 or daily_hours >= 10 :
            return {'error': "Votre nombre d'heures par jour n'est pas entre 1 et 9 heures."}

        return {'error': "Tout est OK !"}