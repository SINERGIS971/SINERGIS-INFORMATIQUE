from odoo import models, fields, api

class TrainingSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    training_cgv = fields.Binary(string="CGV", invisible=True)
    training_booklet = fields.Binary(string="Livret de formation", invisible=True)
    diagnostic_initial = fields.Binary(string="Diagnostic initial", invisible=True)

    @api.model
    def get_values(self):
        res = super(TrainingSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        training_booklets = ICPSudo.get_param('training.training_booklet')
        diagnostic_initial = ICPSudo.get_param('training.diagnostic_initial')
        res.update(
            training_booklet = training_booklets,
            diagnostic_initial = diagnostic_initial,
        )
        return res

    def set_values(self):
        res = super(TrainingSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('training.training_booklet', self.training_booklet)
        self.env['ir.config_parameter'].set_param('training.diagnostic_initial', self.diagnostic_initial)
        return res
