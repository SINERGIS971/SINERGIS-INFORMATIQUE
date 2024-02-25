from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    technical_notes_password = fields.Char(string="Mot de passe des notes techniques",
                              config_parameter='sinergis.technical_notes_password')