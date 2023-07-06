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

    def print_calendar(self):
        # Préparation des données
        first_date = self.date.replace(day=1)
        _, last_day = calendar.monthrange(self.date.year, self.date.month)
        last_date = self.date.replace(day=last_day)
        events = self.env['sinergis_hotline_planning.event'].search([('date','>',first_date),('date','<',last_date)])
        planning = []
        for event in events:
            planning_day = {
                "date": "2023-11-01",
                "users": [],
            }
            for user_id in event.user_ids:
                planning_day['users'].append(user_id.name)
            planning.append(planning_day)


        data = {
            "month": "Novembre",
            "year": "2023",
            "data": generate_calendar(planning),
        }
        return self.env.ref('sinergis_hotline_planning.sinergis_hotline_planning_event_sheet_report').report_action(self, data=data)

    @api.depends('display_name')
    def _compute_display_name (self):
        for rec in self:
            user_name = []
            for user_id in rec.user_ids:
                user_name.append(user_id.name)
            display_name = ', '.join(user_name)
            rec.display_name = display_name