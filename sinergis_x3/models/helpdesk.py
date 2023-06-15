from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    x_sinergis_x3_annual_contracts = fields.One2many('sinergis_x3.annual_contract',readonly=True,string="Contrats annuels du client :")