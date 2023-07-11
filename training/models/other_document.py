from odoo import models, fields, api
from odoo.exceptions import ValidationError

class TrainingOtherDocument(models.Model):
    _name = "training.other_document"
    _description = "Autre Document"
    name = fields.Char(string="Nom du document", required=True)
    file = fields.Binary(string="Fichier", required=True)