from odoo import api, models, fields, _, SUPERUSER_ID
from odoo.exceptions import ValidationError
from odoo.addons.sinergis_hotline_planning.utils.calendar_html import generate_calendar

from datetime import datetime, timedelta

import calendar

class SinergisCustomerVisit(models.Model):
    _name = "sinergis_customer_visit.visit"
    _description = "Visite du client"

    _rec_name = "partner_id"

    #name = fields.Char(string="Name")
    partner_id = fields.Many2one("res.partner",string="Client")

    date = fields.Date(string="Date de la visite",default=lambda self: datetime.now().strftime("%Y-%m-%d"))

    type = fields.Selection([('on_site', 'Sur Site'),('phone', 'Téléphone')], string="Type")
