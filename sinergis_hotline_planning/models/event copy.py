from odoo import api, models, fields, _, SUPERUSER_ID
from odoo.exceptions import ValidationError
from odoo.addons.sinergis_hotline_planning.utils.calendar_html import generate_calendar

from datetime import datetime, timedelta

import calendar

class SinergisHotlinePlanningCalendarEvent(models.Model):
    _inherit = "calendar.event"

    sinergis_hotline_event_id = fields.Many2one("sinergis_hotline_planning.event",string="Salle de réunion")


class SinergisHotlinePlanningEvent(models.Model):
    _name = "sinergis_hotline_planning.event"
    _description = "Évènement du planning de la hotline"
    _rec_name = 'display_name'
    _inherit = ["mail.thread"]

    display_name = fields.Char(string="Nom", compute="_compute_display_name")
    date = fields.Date(string="Jour", required=True, tracking=True)
    user_ids = fields.Many2many('res.users','hotline_planning', string="Consultants", tracking=True)
    
    moorning_or_afternoon = fields.Boolean(string="Consultants différents matin / après-midi", tracking=True)
    morning_user_ids = fields.Many2many('res.users','moorning_hotline_planning', string="Matin", tracking=True)
    afternoon_user_ids = fields.Many2many('res.users','afternoon_hotline_planning', string="Après-midi", tracking=True)

    def print_calendar(self):
        # Préparation des données
        first_date = self.date.replace(day=1)
        _, last_day = calendar.monthrange(self.date.year, self.date.month)
        last_date = self.date.replace(day=last_day)
        events = self.env['sinergis_hotline_planning.event'].search([('date','>=',first_date),('date','<=',last_date)])
        planning = []
        for event in events:
            planning_day = {
                "date": event.date.strftime("%Y-%m-%d"),
                "users": [],
            }
            if event.moorning_or_afternoon:
                morning = []
                for user_id in event.morning_user_ids:
                    if user_id in event.afternoon_user_ids:
                        planning_day['users'].append(user_id.name)
                    else:
                        morning.append(user_id.name)
                for user in morning:
                    planning_day['users'].append("<span style='color:#3DB2EC'>MATIN : </span>"+user)
                for user_id in event.afternoon_user_ids:
                    if user_id not in event.morning_user_ids:
                        planning_day['users'].append("<span style='color:#3DB2EC'>APREM : </span>"+user_id.name)
            else:
                for user_id in event.user_ids:
                    planning_day['users'].append(user_id.name)
            planning.append(planning_day)


        data = generate_calendar(planning)
        
        return self.env.ref('sinergis_hotline_planning.sinergis_hotline_planning_event_sheet_report').report_action(self, data=data)

    @api.onchange('moorning_or_afternoon')
    def onchange_moorning_or_afternoon(self):
        if self.moorning_or_afternoon:
            self.user_ids = [(5, 0, 0)]
        else:
            self.morning_user_ids = [(5, 0, 0)]
            self.afternoon_user_ids = [(5, 0, 0)]

    @api.onchange('user_ids')
    def onchange_user_ids(self):
        self.morning_user_ids = self.user_ids
        self.afternoon_user_ids = self.user_ids

    @api.depends('display_name')
    def _compute_display_name (self):
        for rec in self:
            user_name = []
            if rec.moorning_or_afternoon:
                for user_id in rec.morning_user_ids:
                    user_name.append(user_id.name)
                for user_id in rec.afternoon_user_ids:
                    user_name.append(user_id.name)
            else:
                for user_id in rec.user_ids:
                    user_name.append(user_id.name)
            display_name = ', '.join(user_name)
            rec.display_name = display_name

    @api.model_create_multi
    def create(self, list_value):
        for vals in list_value:
            date = vals['date']
            confront_events = self.env['sinergis_hotline_planning.event'].search([('date','=',date)])
            if confront_events:
                raise ValidationError('Il y a déjà un évènement à cette date.')
        event_ids = super(SinergisHotlinePlanningEvent, self).create(list_value)
        # Ajout des événements aux consultants quand ils ont utilisés sur le planning
        for event_id in event_ids:
            user_ids = event_id.user_ids + event_id.morning_user_ids + event_id.afternoon_user_ids
            for user_id in user_ids:
                calendar_event_id = self.env['calendar.event'].search([('sinergis_hotline_event_id','=',event_id.id),('user_id','=',user_id.id)])
                if not calendar_event_id :
                    user_tz = user_id.tz
                    vals = {
                        'name': "HOTLINE",
                        'user_id': user_id.id,
                        'sinergis_hotline_event_id': event_id.id,
                        'partner_ids': [(4,user_id.partner_id.id)],
                        'need_sync_m': True
                    }
                    if event_id.moorning_or_afternoon:
                        if user_id in event_id.afternoon_user_ids and user_id not in event_id.morning_user_ids :
                            vals['start'] = datetime(event_id.date.year, event_id.date.month, event_id.date.day, 12, 0, 0)
                            vals['stop'] = datetime(event_id.date.year, event_id.date.month, event_id.date.day, 22, 0, 0)
                        elif user_id in event_id.morning_user_ids and user_id not in event_id.afternoon_user_ids :
                            vals['start'] = datetime(event_id.date.year, event_id.date.month, event_id.date.day, 12, 0, 0)
                            vals['stop'] = datetime(event_id.date.year, event_id.date.month, event_id.date.day, 16, 0, 0)
                    else:
                        vals['start'] = datetime(event_id.date.year, event_id.date.month, event_id.date.day, 12, 0, 0)
                        vals['stop'] = datetime(event_id.date.year, event_id.date.month, event_id.date.day, 22, 0, 0)
                    calendar_event_id = self.env['calendar.event'].create(vals)
        return event_ids
    
    def write(self, values):
        date = values.get('date',self.date)
        confront_events = self.env['sinergis_hotline_planning.event'].search([('id','!=',self.id),('date','=',date)])
        if confront_events:
            raise ValidationError('Il y a déjà un évènement à cette date.')
        event_user_ids = values.get("user_ids", self.user_ids)
        event_morning_user_ids = values.get("morning_user_ids", self.morning_user_ids)
        event_afternoon_user_ids = values.get("afternoon_user_ids", self.afternoon_user_ids)
        user_ids = event_user_ids + event_morning_user_ids + event_afternoon_user_ids
        for user_id in user_ids:
            calendar_event_id = self.env['calendar.event'].search([('sinergis_hotline_event_id','=',self.id),('user_id','=',user_id.id)])
            if not calendar_event_id :
                user_tz = user_id.tz
                vals = {
                    'name': "HOTLINE",
                    'user_id': user_id.id,
                    'sinergis_hotline_event_id': self.id,
                    'partner_ids': [(4,user_id.partner_id.id)],
                    'need_sync_m': True
                }
                event_date = values.get("date", self.date)
                if self.moorning_or_afternoon:
                    if user_id in event_afternoon_user_ids and user_id not in event_morning_user_ids :
                        vals['start'] = datetime(event_date.year, event_date.month, event_date.day, 12, 0, 0)
                        vals['stop'] = datetime(event_date.year, event_date.month, event_date.day, 22, 0, 0)
                    elif user_id in event_morning_user_ids and user_id not in event_afternoon_user_ids :
                        vals['start'] = datetime(event_date.year, event_date.month, event_date.day, 12, 0, 0)
                        vals['stop'] = datetime(event_date.year, event_date.month, event_date.day, 16, 0, 0)
                else:
                    vals['start'] = datetime(event_date.year, event_date.month, event_date.day, 12, 0, 0)
                    vals['stop'] = datetime(event_date.year, event_date.month, event_date.day, 22, 0, 0)
                calendar_event_id = self.env['calendar.event'].create(vals)
        return super(SinergisHotlinePlanningEvent, self).write(values)