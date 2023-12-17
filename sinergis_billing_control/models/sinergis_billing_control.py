from odoo import api, models, fields, _, tools, SUPERUSER_ID
from odoo.exceptions import ValidationError

from datetime import datetime, timedelta

class SinergisSensitiveData(models.Model):
    _name = "sinergis_billing_control"
    _description = "Controle de facturation Sinergis"
    _auto = False

    partner_id = fields.Many2one("res.partner", string="Société")
    code_x3 = fields.Char(string="Code X3")
    order_id = fields.Many2one("sale.order", string="Société")
    order_ttc_amount = fields.Float(string="Montant TTC de la commande")
    order_billed_amount = fields.Float(string="Montant facturé")
    order_billed_remaining = fields.Float(string="Montant restant à facturer dans X3")

    #Compute
    is_project_ended = fields.Boolean(string="Projet terminé ?")

    company_id = fields.Many2one("res.company", string="Agence client")

    #Compute
    billing_step = fields.Selection([('', ''),('a_facturer', 'A facturer'),('acompte_facture', 'Acompte facturé'),('totalement_facture', 'Totalement facturé')], string="État de la facturation")
    billing_odoo_flag = fields.Selection([('billed', 'Facturé'),('not_billed', 'Non facturé')], string="Flag facturé dans Odoo")
    
    user_id = fields.Many2one("res.users", string="Vendeur")

    #Compute
    scheduled_days = fields.Float(string="Jours prévus", compute="_compute_scheduled_days")
    completed_days = fields.Float(string="Jours réalisés", compute="_compute_completed_days")
    remaining_days = fields.Float(string="Jours restants", compute="_compute_remaining_days")
    is_overtime = fields.Boolean(string="Devis dépassé", compute="_compute_is_overtime")

    #Compute
    project_archived = fields.Boolean(string="Projet archivé")

    #TO-DO : A mettre en place après validation fonctionnement
    # Date de premier mouvement et dernier mouvement pour le filtrage
    #date_first_move = fields.Datetime(string="Date de premier mouvement")
    #date_last_move = fields.Datetime(string="Date de dernier mouvement")

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        query = """
            CREATE OR REPLACE VIEW sinergis_myactions AS (
            SELECT T.partner_id, T.code_x3, T.order_id, T.order_ttc_amount, T.order_billed_amount, T.order_billed_remaining, T.company_id, T.user_id  FROM
                (SELECT
                    so.partner_id as partner_id,
                    rp.sinergis_x3_code as code_x3,
                    so.id as order_id,
                    # TO DO : TOTAL TTC PRICE
                    # TO DO : BILLED AMOUNT
                    # TO DO : BILLED REMAINING
                    rp.company_id as company_id,
                    so.user_id as user_id
                FROM
                    sale_order as so
                FULL JOIN
                    res_partner AS rp
                ON
                    rp.id = so.partner_id
                GROUP BY
                    so.id, rp.id
                ) AS T
            )
            """
        self._cr.execute(query)

    @api.depends("scheduled_days")
    def _compute_scheduled_days (self):
        for rec in self:
            rec.scheduled_days = False

    @api.depends("completed_days")
    def _compute_scheduled_days (self):
        for rec in self:
            rec.scheduled_days = False

    @api.depends("remaining_days")
    def _compute_scheduled_days (self):
        for rec in self:
            rec.scheduled_days = False

    @api.depends("is_overtime")
    def _compute_is_overtime (self):
        for rec in self:
            rec.overtime = rec.remaining_days < 0