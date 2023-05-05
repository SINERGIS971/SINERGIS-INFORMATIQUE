# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    api_key = fields.Char(string="API KEY",
                              config_parameter='sinergis_mailchimp.api_key')
    list_id = fields.Char(string="AUDIENCE ID",
                              config_parameter='sinergis_mailchimp.list_id')
    