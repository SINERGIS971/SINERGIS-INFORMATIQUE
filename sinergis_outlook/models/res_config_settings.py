from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    outlook_client_id = fields.Char("Outlook Client_id", config_parameter='outlook_client_id', default='')
    outlook_client_secret = fields.Char("Outlook Client_key", config_parameter='outlook_client_secret', default='')
