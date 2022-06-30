from odoo import models, fields, api

class SinergisMovementCountry(models.Model):
    _name = "sinergis.movementcountry"
    _description = "Pays de déplacement"
    x_sinergis_movement_country_name = fields.Char(string="Nom du pays")

class SinergisMovementArea(models.Model):
    _name = "sinergis.movementarea"
    _description = "Zone de déplacement du pays"
    x_sinergis_movement_area_name = fields.Char(string="Nom de la zone")
    x_sinergis_movement_area_country = fields.Many2one("sinergis.movementcountry",string="Pays")
