from odoo import api, models, fields, _

class ExtensionAllowed(models.Model):
    _name = "sinergis_helpdesk_form.extension"
    _description = "Extensions autorisées dans le formulaire en ligne"
    _rec_name="extension"

    extension = fields.Char(string="Extension")
   