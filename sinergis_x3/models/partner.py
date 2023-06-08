# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = "res.partner"

    sinergis_x3_code = fields.Char(string='Code X3')