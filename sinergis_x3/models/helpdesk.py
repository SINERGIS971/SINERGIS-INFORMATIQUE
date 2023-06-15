from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    x_sinergis_x3_annual_contracts = fields.One2many('sinergis_x3.annual_contract',compute="_compute_x_sinergis_x3_annual_contracts",readonly=True,string="Contrats annuels du client :")

    @api.depends("x_sinergis_x3_annual_contracts")
    def _compute_x_sinergis_x3_annual_contracts(self):
        for rec in self:
            domain = []
            domain.append(('partner_id', '=', rec.partner_id.id))
            rec.x_sinergis_x3_annual_contracts = self.env["sinergis_x3.annual_contract"].search(domain)