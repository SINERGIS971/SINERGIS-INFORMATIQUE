from odoo import api, models, fields, _

class ExtensionAllowed(models.Model):
    _name = "sinergis_helpdesk_form.extension_allowed"
    _description = "Extensions autorisées dans le formulaire en ligne"
    _rec_name="extension"

    name = fields.Char(string="Extension")
   