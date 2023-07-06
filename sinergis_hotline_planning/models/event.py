from odoo import api, models, fields, _, SUPERUSER_ID
from odoo.exceptions import ValidationError
from odoo.addons.sinergis_hotline_planning.utils.calendar_html import generate_calendar

from datetime import datetime, timedelta

import calendar

class SinergisHotlinePlanningEvent(models.Model):
    _name = "sinergis_hotline_planning.event"
    _description = "Évènement du planning de la hotline"
    _rec_name = 'display_name'

    display_name = fields.Char(string="Nom", compute="_compute_display_name")
    date = fields.Date(string="Jour", required=True)
    user_ids = fields.Many2many('res.users', string="Consultants")
    
    moorning_or_afternoon = fields.Boolean(string="Consultants différents matin / après-midi")
    morning_user_ids = fields.Many2many('res.users', string="Matin")
    afternoon_user_ids = fields.Many2many('res.users', string="Après-midi")

    def print_calendar(self):
        # Préparation des données
        first_date = self.date.replace(day=1)
        _, last_day = calendar.monthrange(self.date.year, self.date.month)
        last_date = self.date.replace(day=last_day)
        events = self.env['sinergis_hotline_planning.event'].search([('date','>',first_date),('date','<',last_date)])
        planning = []
        for event in events:
            planning_day = {
                "date": event.date.strftime("%Y-%m-%d"),
                "users": [],
            }
            if event.moorning_or_afternoon:
                morning = []
                for user_id in self.morning_user_ids:
                    if user_id in self.afternoon_user_ids:
                        planning_day['users'].append(user_id.name)
                    else:
                        morning.append(user_id.name)
                for user in morning:
                    planning_day['users'].append("MATIN : "+user)
                for user_id in self.afternoon_user_ids:
                    if user_id not in self.morning_user_ids:
                        planning_day['users'].append("APREM : "+user_id.name)
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
        events = super(SinergisHotlinePlanningEvent, self).create(list_value)
        return events
    
    def write(self, values):
        date = values.get('date',self.date)
        confront_events = self.env['sinergis_hotline_planning.event'].search([('id','!=',self.id),('date','=',date)])
        if confront_events:
            raise ValidationError('Il y a déjà un évènement à cette date.')
        return super(SinergisHotlinePlanningEvent, self).write(values)