from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    technical_notes_security_enabled = fields.Boolean(string="Sécurité des notes techniques activée",
                                                      config_parameter='sinergis.technical_notes_security_enabled')
    technical_notes_password = fields.Char(string="Mot de passe des notes techniques",
                              config_parameter='sinergis.technical_notes_password')