from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = "product.template"
    is_training = fields.Boolean(string="Est une formation ?",default=False)
