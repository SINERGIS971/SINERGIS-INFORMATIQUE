from odoo import api, models, fields, _, SUPERUSER_ID
from odoo.exceptions import ValidationError

from datetime import datetime, timedelta

class SinergisHotlinePlanningEvent(models.Model):
    _name = "sinergis_hotline_planning.event"
    _description = "Évènement du planning de la hotline"
    _rec_name = 'display_name'


    display_name = fields.Char(string="Nom", compute="_compute_display_name")
    date = fields.Date(string="Jour", required=True)
    user_ids = fields.Many2many('res.users', string="Consultants")

    def print_calendar(self):
        data = {
            "month": "Novembre",
            "year": "2023",
            "data": "<tr><td></td><td></td><td>1<br>Esteban ANTONIO-MOTA, Magalie LEZEAU</td><td>2<br>Esteban ANTONIO-MOTA, Magalie LEZEAU</td><td>3<br>Esteban ANTONIO-MOTA, Magalie LEZEAU</td></tr><tr><td>6<br>Esteban ANTONIO-MOTA, Magalie LEZEAU</td><td>7<br>Esteban ANTONIO-MOTA, Magalie LEZEAU</td><td>8<br></td><td>9<br></td><td>10<br></td></tr><tr><td>13<br></td><td>14<br></td><td>15<br></td><td>16<br></td><td>17<br></td></tr><tr><td>20<br></td><td>21<br></td><td>22<br></td><td>23<br></td><td>24<br></td></tr><tr><td>27<br></td><td>28<br></td><td>29<br></td><td>30<br></td></tr><tr></tr>",
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