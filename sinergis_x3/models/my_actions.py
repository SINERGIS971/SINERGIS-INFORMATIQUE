# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class MyActions(models.Model):
    _inherit = "sinergis.myactions"

    # Transfert Odoo - X3