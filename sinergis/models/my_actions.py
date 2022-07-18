from odoo import api, fields, models, tools
from odoo.exceptions import ValidationError

class MyActions(models.Model):
    _name = "sinergis.myactions"
    _auto = False

    name = fields.Char(string="Nom")

    @api.model.cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'sinergis_myactions')
        query = """
        CREATE VIEW sinergis_myactions AS (
            SELECT
                id as id,
                name as name
            FROM
                helpdesk_ticket
        )
        """
