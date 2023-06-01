# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = "res.partner"

    x_sinergis_rgpd_sensitive_data_ids = fields.One2many('sinergis_rgpd.sensitive_data', 'partner_id', string='Données sensibles')