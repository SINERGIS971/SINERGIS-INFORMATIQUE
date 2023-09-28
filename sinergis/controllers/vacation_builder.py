import operator

import odoo

from datetime import datetime, timedelta
from odoo import http
from odoo.http import request
from odoo.exceptions import AccessError, UserError, AccessDenied

class SinergisVacationBuilder(http.Controller):
    @http.route('/web/session/sinergis_vacation_builder', type='json', auth="user")
    def change_password(self, fields):
        if request.env.user.has_group('base.group_user') == False:
            return

        # Vérification des champs en entrée
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

        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')

        # Vérification de la non présence de congés
        event_ids = request.env['calendar.event'].search([('start','>=',start_date.strftime("%Y-%m-%d 00:00:01")),('stop','<=',end_date.strftime("%Y-%m-%d 23:59:59")),('x_sinergis_calendar_event_is_vacation','=',True)])
        if len(event_ids) > 0:
            return {'error': "Il y a déjà des congés sur cette plage de dates. Veuillez les supprimer avant d'en générer de nouveaux."}

        # Création  des évènements
        pointed_date = start_date
        total_days = (end_date - start_date).days + 1
        for i in range(0, total_days):
            if pointed_date.weekday() == 5 or pointed_date.weekday() == 6:
                pointed_date = pointed_date + timedelta(days=1)
                continue
            context = {
                        "name" : f"Congés - {self.env.user.name}",
                        "user_id" : self.env.user.id,
                        "start" : pointed_date.strftime("%Y-%m-%d 08:00:00"),
                        "stop" : pointed_date.strftime("%Y-%m-%d 17:00:00"),
                        "x_sinergis_calendar_event_is_vacation": True,
                        'need_sync_m': True
                    }
            self.env["calendar.event"].create(context)
            pointed_date = pointed_date + timedelta(days=1)
        return {'error': "Tout est OK ! " + str(start_mid_day) + " | " + str(end_mid_day)}