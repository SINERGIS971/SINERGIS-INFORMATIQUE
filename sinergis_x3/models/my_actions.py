# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class MyActions(models.Model):
    _inherit = "sinergis.myactions"

    # Transfert Odoo - X3

    is_transfered_x3 = fields.Boolean(string="")


class MyActionsReinvoiced(models.Model):
    _name = "sinergis_x3.myactions.transfer"
    _description = "Detail du transfert au temps passé vers X3"

    model_type = fields.Selection([('helpdesk', 'Assistance'),('calendar', 'Intervention calendrier')])
    model_id = fields.Integer(string="")

    sinergis_x3_id = fields.Char(string="Numéro X3")