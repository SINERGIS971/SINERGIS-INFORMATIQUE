from odoo import api, models, fields, _, SUPERUSER_ID
from odoo.exceptions import ValidationError
from odoo.addons.sinergis_hotline_planning.utils.calendar_html import generate_calendar

from datetime import datetime, timedelta

import calendar

class SinergisCustomerVisit(models.Model):
    _name = "sinergis_customer_visit.visit"
    _description = "Visite du client"

    _rec_name = "partner_id"

    event_id = fields.Many2one("calendar.event",string="Évènement", readonly=True)
    user_id = fields.Many2one("res.users",string="Commercial", readonly=True)
    date = fields.Date(string="Date de la visite",default=lambda self: datetime.now().strftime("%Y-%m-%d"))
    partner_id = fields.Many2one("res.partner",string="Client")
    type = fields.Selection([('on_site', 'Sur site'),('phone', 'Par téléphone')], string="Type")
