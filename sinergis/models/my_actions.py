from odoo import api, fields, models, tools
from odoo.exceptions import ValidationError

class MyActions(models.Model):
    _name = "sinergis.myactions"
    _auto = False

    link_id = fields.Integer()

    name = fields.Char(string="Sujet")

    origin = fields.Selection([('helpdesk', 'Assistance'),('calendar', 'Intervention calendrier')], string="Origine")
    date = fields.Datetime(readonly=True, string="Date")
    client = fields.Many2one("res.partner",string="Client")
    product = fields.Char(string = "Produit",compute="_compute_product")
    billing = fields.Selection([("À définir ultérieurement", "À définir ultérieurement"),("Contrat heure", "Contrat d'heures"),('Temps passé', 'Temps passé'),('Devis', 'Devis'),('Non facturable', 'Non facturable')], string="Facturation")
    time = fields.Float(string = "Temps",compute="_compute_time")
    consultant = fields.Many2one('res.users',string="Consultant")

    #Uniquement pour rapport

    contact = fields.Many2one("res.partner",string="")
    intervention_count = fields.Integer(string="",compute="_compute_intervention_count")
    start_time = fields.Datetime(string="")
    end_time = fields.Datetime(string="")
    task = fields.Many2one("project.task", string="")
    task2 = fields.Many2one("project.task", string="")
    resolution = fields.Html(string="")
    is_solved = fields.Boolean(string="")
    event_trip = fields.Boolean(string="")
    movement_country = fields.Many2one("sinergis.movementcountry", string="")
    movement_area = fields.Many2one("sinergis.movementarea", string="")

    is_printed = fields.Boolean(string="",compute="_compute_is_printed")


    #@api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        query = """
        CREATE OR REPLACE VIEW sinergis_myactions AS (
        SELECT row_number() OVER (ORDER BY 1) AS id,T.origin,T.link_id,
        T.name,T.date,T.client,T.billing,T.consultant,T.contact,T.start_time,T.end_time,T.task,T.task2,T.resolution,T.is_solved,T.event_trip,T.movement_country,T.movement_area FROM
            (SELECT
                'helpdesk' as origin,
                ht.id as id,
                ht.id as link_id,
                ht.name as name,
                ht.create_date as date,
                ht.partner_id as client,
                REPLACE(ht.x_sinergis_helpdesk_ticket_facturation,'heures','heure') as billing,
                ht.user_id as consultant,
                ht.x_sinergis_helpdesk_ticket_contact as contact,
                ht.x_sinergis_helpdesk_ticket_start_time as start_time,
                ht.x_sinergis_helpdesk_ticket_end_time as end_time,
                ht.x_sinergis_helpdesk_ticket_tache as task,
                ht.x_sinergis_helpdesk_ticket_tache2 as task2,
                ht.x_sinergis_helpdesk_ticket_ticket_resolution as resolution,
                ht.x_sinergis_helpdesk_ticket_is_solved as is_solved,
                NULL as event_trip,
                NULL as movement_country,
                NULL as movement_area
            FROM
                helpdesk_ticket as ht
            WHERE
                ht.x_sinergis_helpdesk_ticket_facturation != ''
            UNION ALL
            SELECT
                'calendar' as origin,
                ce.id as id,
                ce.id as link_id,
                ce.name as name,
                ce.start as date,
                ce.x_sinergis_calendar_event_client as client,
                REPLACE(ce.x_sinergis_calendar_event_facturation,'heures','heure') as billing,
                ce.user_id as consultant,
                ce.x_sinergis_calendar_event_contact as contact,
                ce.x_sinergis_calendar_event_start_time as start_time,
                ce.x_sinergis_calendar_event_end_time as end_time,
                ce.x_sinergis_calendar_event_tache as task,
                ce.x_sinergis_calendar_event_tache2 as task2,
                ce.x_sinergis_calendar_event_desc_intervention as resolution,
                ce.x_sinergis_calendar_event_is_solved as is_solved,
                ce.x_sinergis_calendar_event_trip as event_trip,
                ce.x_sinergis_calendar_event_trip_movementcountry as movement_country,
                ce.x_sinergis_calendar_event_trip_movementarea as movement_area
            FROM
                calendar_event as ce
            WHERE
                ce.x_sinergis_calendar_event_facturation != ''
            ) AS T
        )
        """
        self._cr.execute(query)

    @api.depends('is_printed')
    def _compute_is_printed (self):
        for rec in self:
            if self.env['sinergis.myactions.printed'].search_count([('user_id', '=', self.env.user.id),('model_type', '=', rec.origin),('model_id', '=', rec.link_id)]) > 0:
                rec.is_printed = True
            else:
                rec.is_printed = False

    @api.depends('product')
    def _compute_product (self):
        for rec in self:
            if rec.origin == "helpdesk":
                ticket = rec.env['helpdesk.ticket'].search([('id', '=', rec.link_id)])
                if ticket.x_sinergis_helpdesk_ticket_produits == "CEGID":
                    rec.product = ticket.x_sinergis_helpdesk_ticket_produits + " " + ticket.x_sinergis_helpdesk_ticket_produits_cegid if ticket.x_sinergis_helpdesk_ticket_produits_cegid else ticket.x_sinergis_helpdesk_ticket_produits
                elif ticket.x_sinergis_helpdesk_ticket_produits == "SAGE 100":
                    rec.product = ticket.x_sinergis_helpdesk_ticket_produits + " " + ticket.x_sinergis_helpdesk_ticket_produits_sage100 if ticket.x_sinergis_helpdesk_ticket_produits_sage100 else ticket.x_sinergis_helpdesk_ticket_produits
                elif ticket.x_sinergis_helpdesk_ticket_produits == "SAGE 1000":
                    rec.product = ticket.x_sinergis_helpdesk_ticket_produits + " " + ticket.x_sinergis_helpdesk_ticket_produits_sage1000 if ticket.x_sinergis_helpdesk_ticket_produits_sage1000 else ticket.x_sinergis_helpdesk_ticket_produits
                elif ticket.x_sinergis_helpdesk_ticket_produits == "SAP":
                    rec.product = ticket.x_sinergis_helpdesk_ticket_produits + " " + ticket.x_sinergis_helpdesk_ticket_produits_sap if ticket.x_sinergis_helpdesk_ticket_produits_sap else ticket.x_sinergis_helpdesk_ticket_produits
                elif ticket.x_sinergis_helpdesk_ticket_produits == "X3":
                    rec.product = ticket.x_sinergis_helpdesk_ticket_produits + " " + ticket.x_sinergis_helpdesk_ticket_produits_x3 if ticket.x_sinergis_helpdesk_ticket_produits_x3 else ticket.x_sinergis_helpdesk_ticket_produits
                elif ticket.x_sinergis_helpdesk_ticket_produits == "DIVERS":
                    rec.product = ticket.x_sinergis_helpdesk_ticket_produits_divers if ticket.x_sinergis_helpdesk_ticket_produits_divers else ''
                else:
                    rec.product = ticket.x_sinergis_helpdesk_ticket_produits if ticket.x_sinergis_helpdesk_ticket_produits else ''
            else:
                calendar = rec.env['calendar.event'].search([('id', '=', rec.link_id)])
                if calendar.x_sinergis_calendar_event_produits == "CEGID":
                    rec.product = calendar.x_sinergis_calendar_event_produits + " " + calendar.x_sinergis_calendar_event_produits_cegid if calendar.x_sinergis_calendar_event_produits_cegid else calendar.x_sinergis_calendar_event_produits
                elif calendar.x_sinergis_calendar_event_produits == "SAGE 100":
                    rec.product = calendar.x_sinergis_calendar_event_produits + " " + calendar.x_sinergis_calendar_event_produits_sage100 if calendar.x_sinergis_calendar_event_produits_sage100 else calendar.x_sinergis_calendar_event_produits
                elif calendar.x_sinergis_calendar_event_produits == "SAGE 1000":
                    rec.product = calendar.x_sinergis_calendar_event_produits + " " + calendar.x_sinergis_calendar_event_produits_sage1000 if calendar.x_sinergis_calendar_event_produits_sage1000 else calendar.x_sinergis_calendar_event_produits
                elif calendar.x_sinergis_calendar_event_produits == "SAP":
                    rec.product = calendar.x_sinergis_calendar_event_produits + " " + calendar.x_sinergis_calendar_event_produits_sap if calendar.x_sinergis_calendar_event_produits_sap else calendar.x_sinergis_calendar_event_produits
                elif calendar.x_sinergis_calendar_event_produits == "X3":
                    rec.product = calendar.x_sinergis_calendar_event_produits + " " + calendar.x_sinergis_calendar_event_produits_x3 if calendar.x_sinergis_calendar_event_produits_x3 else calendar.x_sinergis_calendar_event_produits
                elif calendar.x_sinergis_calendar_event_produits == "DIVERS":
                    rec.product = calendar.x_sinergis_calendar_event_produits_divers if calendar.x_sinergis_calendar_event_produits_divers else ''
                else:
                    rec.product = calendar.x_sinergis_calendar_event_produits if calendar.x_sinergis_calendar_event_produits else ''

    @api.depends('time')
    def _compute_time (self):
        for rec in self:
            if rec.origin == "helpdesk":
                ticket = rec.env['helpdesk.ticket'].search([('id', '=', rec.link_id)])
                if ticket.x_sinergis_helpdesk_ticket_facturation == "Contrat heures" or ticket.x_sinergis_helpdesk_ticket_facturation == "Devis":
                    rec.time = sum(rec.env['account.analytic.line'].search([('x_sinergis_account_analytic_line_ticket_id', '=', rec.link_id)]).mapped('unit_amount'))
                else :
                    rec.time = ticket.x_sinergis_helpdesk_ticket_temps_passe
            elif rec.origin == "calendar":
                calendar = rec.env['calendar.event'].search([('id', '=', rec.link_id)])
                if calendar.x_sinergis_calendar_event_facturation == "Contrat heure" or calendar.x_sinergis_calendar_event_facturation == "Devis":
                    rec.time = sum(rec.env['account.analytic.line'].search([('x_sinergis_account_analytic_line_event_id', '=', rec.link_id)]).mapped('unit_amount'))
                else :
                    rec.time = calendar.x_sinergis_calendar_duree_facturee

    @api.depends('intervention_count')
    def _compute_intervention_count (self):
        for rec in self:
            if rec.origin == "helpdesk":
                rec.intervention_count = self.env['account.analytic.line'].search_count([('x_sinergis_account_analytic_line_ticket_id', '=', rec.link_id)])
            elif rec.origin == "calendar":
                rec.intervention_count = self.env['account.analytic.line'].search_count([('x_sinergis_account_analytic_line_event_id', '=', rec.link_id)])

    def open(self):
        if self.origin == "helpdesk":
            return {
            'name': 'Assistance',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'helpdesk.ticket',
            'res_id': self.env['helpdesk.ticket'].search([('id', '=', self.link_id)]).id,
            'target': 'new',
            }
        elif self.origin == "calendar":
            return {
            'name': 'Calendrier',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'calendar.event',
            'res_id': self.env['calendar.event'].search([('id', '=', self.link_id)]).id,
            'target': 'new',
            }

    def print_report(self):
        ids = []
        for rec in self:
            ids.append(rec.id)
            #Fonctionnalité "a été imprimé"
            if self.env['sinergis.myactions.printed'].search_count([('user_id', '=', self.env.user.id),('model_type', '=', rec.origin),('model_id', '=', rec.link_id)]) == 0:
                data = {
                    'user_id': self.env.user.id,
                    'model_type': rec.origin,
                    'model_id': rec.link_id,
                }
                self.env['sinergis.myactions.printed'].create(data)
        return self.env.ref('sinergis.sinergis_report_myactions').report_action(self.env['sinergis.myactions'].search([('id', '=', ids)]))

class MyActionsPrinted(models.Model):
    _name = "sinergis.myactions.printed"
    _description = "Activités imprimées"
    user_id = fields.Many2one("res.users")
    model_type = fields.Selection([('helpdesk', 'Assistance'),('calendar', 'Intervention calendrier')])
    model_id = fields.Integer(string="")
