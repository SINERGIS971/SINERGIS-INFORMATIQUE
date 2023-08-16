# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = "res.partner"

    sinergis_x3_code = fields.Char(string='Code X3')

    @api.onchange("sinergis_x3_code")
    def on_change_sinergis_x3_code(self):
        # Vérification si un autre client avec le même code X3 existe
        partner = self.env['res.partner'].search([('sinergis_x3_code','=',self.sinergis_x3_code)], limit=1)
        if partner and self.sinergis_x3_code:
            code_x3 = partner.sinergis_x3_code
            raise ValidationError(f'Ce code X3 ({code_x3}) est déjà renseigné pour une autre société : {partner.name}')
        
