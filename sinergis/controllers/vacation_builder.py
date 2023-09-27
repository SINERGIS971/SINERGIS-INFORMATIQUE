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

        start_date,end_date,daily_hours = operator.itemgetter('start_date','end_date','daily_hours')({f['name']: f['value'] for f in fields})
        start_mid_day = False
        end_mid_day = False
        for f in fields:
            if f['name'] == "start_mid_day":
                start_mid_day = True
            if f['name'] == "end_mid_day":
                end_mid_day = True

        if not (start_date.strip() and end_date.strip()):
            return {'error': 'Veuillez renseigner correctement les dates.'}

        if not daily_hours.isnumeric():
            return {'error': "Veuillez saisir correctement votre nombre d'heures par jour."}
        daily_hours = int(daily_hours)

        if daily_hours <= 0 or daily_hours >= 10 :
            return {'error': "Votre nombre d'heures par jour n'est pas entre 1 et 9 heures."}

        return {'error': "Tout est OK ! " + str(start_mid_day) + " | " + str(end_mid_day)}