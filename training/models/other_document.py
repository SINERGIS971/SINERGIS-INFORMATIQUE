from odoo import models, fields, api
from odoo.exceptions import ValidationError

class TrainingOtherDocument(models.Model):
    _name = "training.other_document"
    _description = "Document"
    name = fields.Char(string="Nom du document", required=True)
    file = fields.Binary(string="Fichier", required=True)
    type = fields.Selection([('Autre', 'Autre'),('CGV', 'CGV'),('Livret de formation', 'Livret de formation'),('Diagnostic initial', 'Diagnostic initial')], string="Type", default="Autre")

    @api.onchange("type")
    def on_change_type(self):
        if self.env['training.other_document'].search_count([('type', '=', 'CGV')]) >= 1:
                raise ValidationError("Le document 'CGV' existe déjà")
        if self.env['training.other_document'].search_count([('type', '=', 'Livret de formation')]) >= 1:
                raise ValidationError("Le document 'Livret de formation' existe déjà")
        if self.env['training.other_document'].search_count([('type', '=', 'Diagnostic initial')]) >= 1:
                raise ValidationError("Le document 'Diagnostic initial' existe déjà")
        