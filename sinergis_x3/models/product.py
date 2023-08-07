from odoo import api, models, fields, _, SUPERUSER_ID
from odoo.exceptions import ValidationError

from datetime import datetime, timedelta

class ProductTemplate(models.Model):
    _inherit = "product.template"
    is_hostable = fields.Boolean(string="Est hébergeable ?",default=False)
    is_ch = fields.Boolean(string="Est un contrat d'heures ?",default=False)
    is_service = fields.Boolean(string="Est une prestation ?", default=False)
    transfer_description = fields.Boolean(string="Transférer la description sur X3 ?", default=True)