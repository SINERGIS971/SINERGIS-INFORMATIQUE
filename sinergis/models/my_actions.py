from odoo import api, fields, models, tools
from odoo.exceptions import ValidationError

class MyActions(models.Model):
    _name = "sinergis.myactions"
    _auto = False

    name = fields.Char(string="Nom")

    #@api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'sinergis_myactions')
        query = """
        CREATE OR REPLACE VIEW sinergis_myactions AS (
            SELECT
                ht.id as id,
                ht.name as name
            FROM
                helpdesk_ticket as ht
        )
        """
