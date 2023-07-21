from odoo import api, models, fields, _, SUPERUSER_ID
from odoo.exceptions import ValidationError

from datetime import datetime, timedelta

class SinergisX3SettingsProductTemplate(models.Model):
    _name = "sinergis_x3.settings.product.template"
    _description = "Transcodage des articles"
    _rec_name = 'product_template_id'

    product_template_id = fields.Many2one("product.template", string="Article", required=True)
    format = fields.Char(string="Format de l'article X3", required=True)

class SinergisX3SettingsSinergisProduct(models.Model):
    _name = "sinergis_x3.settings.sinergis_product"
    _description = "Transcodage des produits Sinergis"
    _rec_name = 'sinergis_product_id'

    sinergis_product_id = fields.Many2one("sale.products", string="Produit Sinergis", required=True)
    code = fields.Char(string="Code X3")

class SinergisX3SettingsSinergisSubProduct(models.Model):
    _name = "sinergis_x3.settings.sinergis_subproduct"
    _description = "Transcodage des sous-produits Sinergis"
    _rec_name = 'sinergis_subproduct_id'

    sinergis_product_id = fields.Many2one("sale.products", string="Produit Sinergis", required=True)
    sinergis_subproduct_id = fields.Many2one("sale.products.subproducts", string="Sous-produit Sinergis", required=True)
    code = fields.Char(string="Code X3")

    @api.onchange ("sinergis_product_id")
    def onchange_sinergis_product_id(self):
        self.sinergis_subproduct_id = False

class SinergisX3SettingsHostable(models.Model):
    _name = "sinergis_x3.settings.hostable"
    _description = "Codes hébergement"
    _rec_name = 'hosted'

    hosted = fields.Boolean(string="Est hébergé ?",default=False)
    code = fields.Char(string="Code X3", required=True)

class SinergisX3SettingsUom(models.Model):
    _name = "sinergis_x3.settings.uom"
    _description = "Transcodage des unités"
    _rec_name = 'uom_id'

    uom_id = fields.Many2one("uom.uom", string="Unité", required=True)
    code = fields.Char(string="Code X3", required=True)

class SinergisX3SettingsCommercial(models.Model):
    _name = "sinergis_x3.settings.commercial"
    _description = "Transcodage des commerciaux"
    _rec_name = 'user_id'

    user_id = fields.Many2one("res.users", string="Commercial", required=True)
    code = fields.Char(string="Code X3", required=True)

class SinergisX3SettingsCompany(models.Model):
    _name = "sinergis_x3.settings.company"
    _description = "Transcodage des agences"
    _rec_name = 'company_id'

    company_id = fields.Many2one("res.company", string="Agence", required=True)
    code = fields.Char(string="Code X3", required=True)

class SinergisX3SettingsCompany(models.Model):
    _name = "sinergis_x3.settings.company"
    _description = "Transcodage des agences"
    _rec_name = 'name'

    name = fields.Char(string="Code X3", compute="_compute_name")    

    company_id = fields.Many2one("res.company", string="Agence", required=True)
    code = fields.Char(string="Code X3", required=True)

    @api.depends('company_id', 'code')
    def _compute_name(self):
        for rec in self:
            rec.name = f"{rec.company_id.name} ({rec.code})"

class SinergisX3SettingsEmail(models.Model):
    _name = "sinergis_x3.settings.email"
    _description = "Email à contacter lors d'un transfère"
    _rec_name = 'email'

    email = fields.Char(string="Email", required=True)
    company_x3_id = fields.Many2one("sinergis_x3.settings.company",string="Agence concernée", required=True)