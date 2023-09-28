import operator

import odoo

from datetime import datetime, timedelta
from odoo import http
from odoo.http import request
from odoo.exceptions import AccessError, UserError, AccessDenied
from odoo.tools import pytz

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

        # Vérification si les dates sont dans le bon ordre
        if start_date > end_date:
            return {'error': "La date de fin est antérieure à celle de début."}

        if start_date == end_date and start_mid_day and end_mid_day:
            return {'error': "Vous ne pouvez pas partir et revenir le midi le même jour."}
        
        total_days = (end_date - start_date).days + 1

        if total_days > 60:
            return {'error': "Vous ne pouvez pas planifier des congés de plus de 60 jours avec cet outil. Veuillez vous rapprocher d'un administrateur."}

        # Vérification de la non présence de congés
        event_ids = request.env['calendar.event'].search([('start','>=',start_date.strftime("%Y-%m-%d 00:00:01")),('stop','<=',end_date.strftime("%Y-%m-%d 23:59:59")),('x_sinergis_calendar_event_is_vacation','=',True)])
        if len(event_ids) > 0:
            return {'error': "Il y a déjà des congés sur cette plage de dates. Veuillez les supprimer avant d'en générer de nouveaux."}

        # Chargement timezone

        user_timezone = request.env.user.tz or "UTC"
        user_tz = pytz.timezone(user_timezone)

        utc_tz = pytz.timezone("UTC")

        # Création  des évènements
        pointed_date = start_date

        for i in range(0, total_days):
            if pointed_date.weekday() == 5 or pointed_date.weekday() == 6:
                pointed_date = pointed_date + timedelta(days=1)
                continue
            if start_mid_day and i == 0:
                duration = daily_hours/2.0
                duration_hours = int(daily_hours/2.0)
                duration_minutes = int((daily_hours/2.0 - duration_hours)*60)
                event_start = user_tz.localize(pointed_date.replace(hour=13, minute=0, second=0, microsecond=0)).astimezone(utc_tz).strftime("%Y-%m-%d %H:%M:%S")
                event_stop = user_tz.localize(pointed_date.replace(hour=13+duration_hours, minute=duration_minutes, second=0, microsecond=0)).astimezone(utc_tz).strftime("%Y-%m-%d %H:%M:%S")
            elif end_mid_day and i == total_days-1:
                duration = daily_hours/2.0
                duration_hours = int(daily_hours/2.0)
                duration_minutes = int((daily_hours/2.0 - duration_hours)*60)
                event_start = user_tz.localize(pointed_date.replace(hour=8, minute=0, second=0, microsecond=0)).astimezone(utc_tz).strftime("%Y-%m-%d %H:%M:%S")
                event_stop = user_tz.localize(pointed_date.replace(hour=8+duration_hours, minute=duration_minutes, second=0, microsecond=0)).astimezone(utc_tz).strftime("%Y-%m-%d %H:%M:%S")
            else :
                duration = daily_hours
                event_start = user_tz.localize(pointed_date.replace(hour=8, minute=0, second=0, microsecond=0)).astimezone(utc_tz).strftime("%Y-%m-%d %H:%M:%S")
                event_stop = user_tz.localize(pointed_date.replace(hour=8+duration, minute=0, second=0, microsecond=0)).astimezone(utc_tz).strftime("%Y-%m-%d %H:%M:%S")
            context = {
                        "name" : f"Congés",
                        "user_id" : request.env.user.id,
                        "start" : event_start,
                        "stop" : event_stop,
                        "x_sinergis_calendar_event_is_vacation": True,
                        "x_sinergis_calendar_event_facturation" : "Congés",
                        "x_sinergis_calendar_duree_facturee" : duration,
                        'need_sync_m': True
                    }
            event = request.env["calendar.event"].create(context)

            # Increment pointer
            pointed_date = pointed_date + timedelta(days=1)
        return True
        

