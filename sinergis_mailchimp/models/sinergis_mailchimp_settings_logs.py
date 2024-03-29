from odoo import models, fields, api
from datetime import datetime

class SinergisMailchimpSettingdsLogs (models.Model):
    _name = "sinergis_mailchimp.settings.logs"
    _description = "Informations sur la synchronisation avec Mailchimp"
    
    date = fields.Datetime("Date", default=lambda self: datetime.now().strftime("%Y-%m-%d %H:%M:%S"), readonly=True)
    name = fields.Text(string="Information",required=True)
    type = fields.Selection([('success', 'success'),('danger', 'danger'),('warning', 'warning')], string="Type")