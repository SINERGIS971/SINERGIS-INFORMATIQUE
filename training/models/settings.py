from odoo import models, fields, api

class TrainingSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    training_cgv = fields.Binary(string="CGV")
    training_booklet = fields.Binary(string="Livret de formation")

    @api.model
    def get_values(self):
        res = super(TrainingSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        training_cgvs = ICPSudo.get_param('training.training_cgv')
        training_booklets = ICPSudo.get_param('training.training_booklet')
        res.update(
            training_cgv = training_cgvs,
            training_booklet = training_booklets,
        )
        return res

    def set_values(self):
        res = super(TrainingSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('training.training_cgv', self.training_cgv)
        self.env['ir.config_parameter'].set_param('training.training_booklet', self.training_booklet)
        return res
