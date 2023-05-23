from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = "product.template"
    deposit_percentage = fields.Float(string="Pourcentage d'acompte",default=0.5,required=True)
