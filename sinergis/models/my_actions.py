from odoo import api, fields, models, tools
from odoo.exceptions import ValidationError
from datetime import datetime

class MyActionsReinvoiced(models.Model):
    _name = "sinergis.myactions.reinvoiced"
    _description = "Interventions refacturées"
    model_type = fields.Selection([('helpdesk', 'Assistance'),('calendar', 'Intervention calendrier')])
    model_id = fields.Integer(string="")
    reinvoiced_company_id = fields.Many2one("res.company",string="Agence")

class MyActions(models.Model):
    _name = "sinergis.myactions"
    _auto = False

    link_id = fields.Integer()

    name = fields.Char(string="Sujet")

    origin = fields.Selection([('helpdesk', 'Assistance'),('calendar', 'Intervention calendrier')], string="Origine")
    date = fields.Datetime(readonly=True, string="Date")
    client = fields.Many2one("res.partner",string="Client")
    product = fields.Char(string = "Produit",compute="_compute_product")
    billing = fields.Selection([("À définir ultérieurement", "À définir ultérieurement"),("Contrat heure", "Contrat d'heures"),('Temps passé', 'Temps passé'),('Devis', 'Devis'),('Non facturable interne', 'Non facturable interne'),('Non facturable', 'Non facturable'),("Avant-vente", "Avant-vente")], string="Facturation")
    billing_type = fields.Selection([('Non facturable', 'Non facturable'),('Facturable', 'Facturable')], string="Facturable/Non facturable")
    time = fields.Float(string = "Temps")
    consultant = fields.Many2one('res.users',string="Consultant")
    consultant_company_id = fields.Many2one("res.company",string="Société SINERGIS")
    country_id = fields.Many2one("res.country",readonly=True,string="Pays du client")

    #Uniquement pour les activités du calendrier
    rapport_intervention_valide = fields.Boolean(compute="_compute_rapport_intervention_valide")

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
    printed_datetime = fields.Datetime(string='Dernière édition',compute="_compute_printed_datetime")
    is_billed = fields.Boolean(string="")

    # Refacturation

    is_reinvoiced = fields.Boolean(string="")
    reinvoiced_company_id = fields.Many2one("res.company")

    #@api.model_cr
    #[16/10/22] Helpdesk : Variable 'date' fixée à 'start_time' pour ne pas voir la date de création mais la date de traitement du ticket
    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        query = """
            CREATE OR REPLACE VIEW sinergis_myactions AS (
            SELECT T.id AS id,T.origin,T.link_id,
            T.name,T.date,T.client,T.billing,T.billing_type,CAST(T.time AS float),T.consultant,T.consultant_company_id,T.contact,T.start_time,T.end_time,T.task,T.task2,T.resolution,T.is_solved,T.event_trip,T.movement_country,T.movement_area,T.country_id,T.is_billed,T.is_reinvoiced,T.reinvoiced_company_id FROM
                ((SELECT
                    'helpdesk' as origin,
                    2*ht.id as id,
                    ht.id as link_id,
                    ht.name as name,
                    ht.x_sinergis_helpdesk_ticket_start_time as date,
                    ht.partner_id as client,
                    REPLACE(ht.x_sinergis_helpdesk_ticket_facturation,'heures','heure') as billing,
                    CASE
                        WHEN ht.x_sinergis_helpdesk_ticket_facturation = 'À définir ultérieurement' OR ht.x_sinergis_helpdesk_ticket_facturation = 'Non facturable interne' OR ht.x_sinergis_helpdesk_ticket_facturation = 'Non facturable' OR ht.x_sinergis_helpdesk_ticket_facturation = 'Avant-vente'
                            THEN 'Non facturable'
                            ELSE 'Facturable'
                    END AS billing_type,
                    CASE
                        WHEN ht.x_sinergis_helpdesk_ticket_facturation = 'Contrat heures' OR ht.x_sinergis_helpdesk_ticket_facturation = 'Devis'
                            THEN SUM(aal.unit_amount)::TEXT
                            ELSE ht.x_sinergis_helpdesk_ticket_temps_passe::TEXT
                    END AS time,
                    
                    ht.user_id as consultant,
                    ru.company_id as consultant_company_id,
                    ht.x_sinergis_helpdesk_ticket_contact as contact,
                    ht.x_sinergis_helpdesk_ticket_start_time as start_time,
                    ht.x_sinergis_helpdesk_ticket_end_time as end_time,
                    ht.x_sinergis_helpdesk_ticket_tache as task,
                    ht.x_sinergis_helpdesk_ticket_tache2 as task2,
                    ht.x_sinergis_helpdesk_ticket_ticket_resolution as resolution,
                    ht.x_sinergis_helpdesk_ticket_is_solved as is_solved,
                    NULL as event_trip,
                    NULL as movement_country,
                    NULL as movement_area,
                    rp.country_id as country_id,
                    CASE WHEN (SELECT count(id) FROM sinergis_myactions_billed AS bld WHERE bld.model_type='helpdesk' and bld.model_id=ht.id) > 0 THEN True else False END as is_billed,
                    CASE WHEN (SELECT count(id) FROM sinergis_myactions_reinvoiced AS reinv WHERE reinv.model_type='helpdesk' and reinv.model_id=ht.id) > 0 THEN True else False END as is_reinvoiced,
                    CASE WHEN (SELECT count(id) FROM sinergis_myactions_reinvoiced AS reinv WHERE reinv.model_type='helpdesk' and reinv.model_id=ht.id) > 0 THEN (SELECT reinvoiced_company_id FROM sinergis_myactions_reinvoiced AS reinv WHERE reinv.model_type='helpdesk' and reinv.model_id=ht.id) else NULL END as reinvoiced_company_id
                FROM
                    helpdesk_ticket as ht
                FULL JOIN
                    account_analytic_line AS aal
                ON
                    aal.x_sinergis_account_analytic_line_ticket_id = ht.id
                FULL JOIN
                    res_users AS ru
                ON
                    ht.user_id = ru.id
                FULL JOIN
                    res_partner AS rp
                ON
                    ht.partner_id = rp.id
                WHERE
                    ht.x_sinergis_helpdesk_ticket_facturation != ''
                GROUP BY
                    ht.id,ru.id,rp.id)
                UNION ALL
                (
                SELECT
                    'calendar' as origin,
                    2*ce.id+1 as id,
                    ce.id as link_id,
                    ce.name as name,
                    ce.start as date,
                    ce.x_sinergis_calendar_event_client as client,
                    REPLACE(ce.x_sinergis_calendar_event_facturation,'heures','heure') as billing,
                    CASE
                        WHEN ce.x_sinergis_calendar_event_facturation = 'À définir ultérieurement' OR ce.x_sinergis_calendar_event_facturation = 'Non facturable interne' OR ce.x_sinergis_calendar_event_facturation = 'Non facturable' OR ce.x_sinergis_calendar_event_facturation = 'Avant-vente'
                            THEN 'Non facturable'
                            ELSE 'Facturable'
                    END AS billing_type,
                    CASE
                        WHEN ce.x_sinergis_calendar_event_facturation = 'Contrat heure' OR ce.x_sinergis_calendar_event_facturation = 'Devis'
                            THEN SUM(aal.unit_amount)::TEXT
                            ELSE ce.x_sinergis_calendar_duree_facturee::TEXT
                    END AS time,
                    ce.user_id as consultant,
                    ru.company_id as consultant_company_id,
                    ce.x_sinergis_calendar_event_contact as contact,
                    ce.x_sinergis_calendar_event_start_time as start_time,
                    ce.x_sinergis_calendar_event_end_time as end_time,
                    ce.x_sinergis_calendar_event_tache as task,
                    ce.x_sinergis_calendar_event_tache2 as task2,
                    ce.x_sinergis_calendar_event_desc_intervention as resolution,
                    ce.x_sinergis_calendar_event_is_solved as is_solved,
                    ce.x_sinergis_calendar_event_trip as event_trip,
                    ce.x_sinergis_calendar_event_trip_movementcountry as movement_country,
                    ce.x_sinergis_calendar_event_trip_movementarea as movement_area,
                    rp.country_id as country_id,
                    Case WHEN (SELECT count(id) FROM sinergis_myactions_billed AS bld WHERE bld.model_type='calendar' and bld.model_id=ce.id) > 0 THEN True else False END as is_billed,
                                        CASE WHEN (SELECT count(id) FROM sinergis_myactions_reinvoiced AS reinv WHERE reinv.model_type='calendar' and reinv.model_id=ce.id) > 0 THEN True else False END as is_reinvoiced,
                    CASE WHEN (SELECT count(id) FROM sinergis_myactions_reinvoiced AS reinv WHERE reinv.model_type='calendar' and reinv.model_id=ce.id) > 0 THEN (SELECT reinvoiced_company_id FROM sinergis_myactions_reinvoiced AS reinv WHERE reinv.model_type='calendar' and reinv.model_id=ce.id) else NULL END as reinvoiced_company_id
                FROM
                    calendar_event as ce
                FULL JOIN
                    account_analytic_line AS aal
                ON
                    aal.x_sinergis_account_analytic_line_event_id = ce.id
                FULL JOIN
                    res_users AS ru
                ON
                    ru.id = ce.user_id
                FULL JOIN
                    res_partner AS rp
                ON
                    ce.x_sinergis_calendar_event_client = rp.id
                WHERE
                    ce.x_sinergis_calendar_event_facturation != ''
                GROUP BY
                    ce.id,ru.id,rp.id
                    )
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

    @api.depends('printed_datetime')
    def _compute_printed_datetime (self):
        for rec in self:
            if self.env['sinergis.myactions.printed'].search_count([('user_id', '=', self.env.user.id),('model_type', '=', rec.origin),('model_id', '=', rec.link_id)]) > 0:
                rec.printed_datetime = rec.env['sinergis.myactions.printed'].search([('user_id', '=', self.env.user.id),('model_type', '=', rec.origin),('model_id', '=', rec.link_id)]).last_date
            else:
                rec.printed_datetime = False

    @api.depends('product')
    def _compute_product (self):
        for rec in self:
            if rec.origin == "helpdesk":
                ticket = rec.env['helpdesk.ticket'].search([('id', '=', rec.link_id)])
                if ticket.x_sinergis_helpdesk_ticket_produits_new and ticket.x_sinergis_helpdesk_ticket_sous_produits_new:
                    rec.product = ticket.x_sinergis_helpdesk_ticket_produits_new.name + " " + ticket.x_sinergis_helpdesk_ticket_sous_produits_new.name
                elif ticket.x_sinergis_helpdesk_ticket_produits_new:
                    rec.product = ticket.x_sinergis_helpdesk_ticket_produits_new.name
                else: 
                    rec.product = ""
            else:
                calendar = rec.env['calendar.event'].search([('id', '=', rec.link_id)])
                if calendar.x_sinergis_calendar_event_produits_new and calendar.x_sinergis_calendar_event_sous_produits_new:
                    rec.product = calendar.x_sinergis_calendar_event_produits_new.name + " " + calendar.x_sinergis_calendar_event_sous_produits_new.name
                elif calendar.x_sinergis_calendar_event_produits_new:
                    rec.product = calendar.x_sinergis_calendar_event_produits_new.name
                else: 
                    rec.product = ""

    @api.depends('intervention_count')
    def _compute_intervention_count (self):
        for rec in self:
            if rec.origin == "helpdesk":
                rec.intervention_count = self.env['account.analytic.line'].search_count([('x_sinergis_account_analytic_line_ticket_id', '=', rec.link_id)])
            elif rec.origin == "calendar":
                rec.intervention_count = self.env['account.analytic.line'].search_count([('x_sinergis_account_analytic_line_event_id', '=', rec.link_id)])


    # Vrai si l'évènement vient du calendrier et qu'il y a un rapport d'intervention valide sur celui-ci
    @api.depends('rapport_intervention_valide')
    def _compute_rapport_intervention_valide (self):
        for rec in self:
            if rec.origin == "calendar":
                if self.env['calendar.sinergis_intervention_report_done'].search([('event_id', '=', rec.link_id)]):
                    rec.rapport_intervention_valide = True
                else:
                    rec.rapport_intervention_valide = False
            else:
                rec.rapport_intervention_valide = False


    def open(self):
        context = {}
        if self.origin == "helpdesk":
            context = {
            'name': 'Assistance',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'helpdesk.ticket',
            'res_id': self.env['helpdesk.ticket'].search([('id', '=', self.link_id)]).id,
            'target': 'new',
            'flags':{'mode':'readonly'},
            }
        elif self.origin == "calendar":
            context = {
            'name': 'Calendrier',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'calendar.event',
            'res_id': self.env['calendar.event'].search([('id', '=', self.link_id)]).id,
            'target': 'new',
            'flags':{'mode':'readonly'},
            }
        return context

    # Marquer la facturation

    def invoiced_button (self):
        if self.env.user.has_group('sinergis.group_myactions_employee') == False:
            if self.env['sinergis.myactions.billed'].search_count([('model_type', '=', self.origin),('model_id', '=', self.link_id)]) == 0:
                data = {
                    'model_type': self.origin,
                    'model_id': self.link_id,
                }
                self.env['sinergis.myactions.billed'].create(data)
        else:
            raise ValidationError("Vous n'avez pas l'accès pour changer le statut de la facturation. Merci de vous rapprocher de la direction.")

    def no_invoiced_button (self):
        if self.env.user.has_group('sinergis.group_myactions_employee') == False:
            if self.env['sinergis.myactions.billed'].search_count([('model_type', '=', self.origin),('model_id', '=', self.link_id)]) == 1:
                self.env["sinergis.myactions.billed"].search([('model_type', '=', self.origin),('model_id', '=', self.link_id)]).unlink()
        else:
            raise ValidationError("Vous n'avez pas l'accès pour changer le statut de la facturation. Merci de vous rapprocher de la direction.")

    def no_invoiced_button_default(self):
        raise ValidationError("Vous ne pouvez pas modifier l'état de cette facturation avec ce mode de facturation.")

    def invoiced_button_default(self):
        raise ValidationError("Vous ne pouvez pas modifier l'état de cette facturation avec ce mode de facturation.")

    # Marquer la refacturation

    def reinvoiced_button (self):
        if self.env.user.has_group('sinergis.group_myactions_employee') == False:
            if self.env['sinergis.myactions.reinvoiced'].search_count([('model_type', '=', self.origin),('model_id', '=', self.link_id)]) == 0:
                data = {
                    'model_type': self.origin,
                    'model_id': self.link_id,
                    'reinvoiced_company_id': self.env.user.company_id.id,
                }
                self.env['sinergis.myactions.reinvoiced'].create(data)
        else:
            raise ValidationError("Vous n'avez pas l'accès pour changer le statut de la facturation. Merci de vous rapprocher de la direction.")

    def no_reinvoiced_button (self):
        if self.env.user.has_group('sinergis.group_myactions_employee') == False:
            if self.env['sinergis.myactions.reinvoiced'].search_count([('model_type', '=', self.origin),('model_id', '=', self.link_id)]) == 1:
                self.env["sinergis.myactions.reinvoiced"].search([('model_type', '=', self.origin),('model_id', '=', self.link_id)]).unlink()
        else:
            raise ValidationError("Vous n'avez pas l'accès pour changer le statut de la refacturation. Merci de vous rapprocher de la direction.")

    # Impression de rapports en sélectionnant un par un les activités
    def print_reports(self):
        ids = []
        for rec in self:
            ids.append(rec.id)
            #Fonctionnalité d'affichage "a été imprimé"
            if self.env['sinergis.myactions.printed'].search_count([('user_id', '=', self.env.user.id),('model_type', '=', rec.origin),('model_id', '=', rec.link_id)]) == 0:
                data = {
                    'user_id': self.env.user.id,
                    'model_type': rec.origin,
                    'model_id': rec.link_id,
                    'last_date': datetime.now(),
                }
                self.env['sinergis.myactions.printed'].create(data)
            else:
                ticket = rec.env['sinergis.myactions.printed'].search([('user_id', '=', self.env.user.id),('model_type', '=', rec.origin),('model_id', '=', rec.link_id)])
                ticket.last_date = datetime.now()

        return self.env.ref('sinergis.sinergis_report_myactions').report_action(self.env['sinergis.myactions'].search([('id', '=', ids)]))

    # Impression de rapports via le bouton "Éditer" de la ligne d'activité
    def print_report(self):
        #Fonctionnalité d'affichage "a été imprimé"
        if self.env['sinergis.myactions.printed'].search_count([('user_id', '=', self.env.user.id),('model_type', '=', self.origin),('model_id', '=', self.link_id)]) == 0:
            data = {
                'user_id': self.env.user.id,
                'model_type': self.origin,
                'model_id': self.link_id,
                'last_date': datetime.now(),
            }
            self.env['sinergis.myactions.printed'].create(data)
        else:
            ticket = self.env['sinergis.myactions.printed'].search([('user_id', '=', self.env.user.id),('model_type', '=', self.origin),('model_id', '=', self.link_id)])
            ticket.last_date = datetime.now()

        return self.env.ref('sinergis.sinergis_report_myactions').report_action(self.env['sinergis.myactions'].search([('id', '=', self.id)]))
        

    def download_rapport_intervention_valide (self):
        report_count = self.env['calendar.sinergis_intervention_report_done'].search_count([('event_id', '=', self.link_id)])
        if report_count == 1 :
            report_id = self.env['calendar.sinergis_intervention_report_done'].search([('event_id', '=', self.link_id)]).id
            return {
                'name': 'Rapport',
                'type': 'ir.actions.act_url',
                'url': '/web/content/?model=calendar.sinergis_intervention_report_done&id={}&field=file&download=true'.format(
                    report_id
                ),
                'target': 'self',
            }
        raise ValidationError(f"Cet évènement comporte {str(report_count)} rapport(s) d'intervention validé(s). Pour y accéder veuillez ouvrir (bouton OUVRIR) l'évènement et cliquer sur l'onglet \"Rapport validé\" afin d’accéder à l’ensemble des rapports validés.")
        # Pour le moment pas de solution pour pouvoir télécharger plusieurs rapport d'intervention dans le champ one2Many du calendrier.
        #return {
        #    'name': 'Rapport',
        #    'type': 'ir.actions.act_url',
        #    'url': '/web/content/?model=calendar.event&id={}&field=x_sinergis_calendar_event_rapport_intervention_valide&download=true'.format(
        #        self.link_id
        #    ),
        #    'target': 'self',
        #}

class MyActionsPrinted(models.Model):
    _name = "sinergis.myactions.printed"
    _description = "Activités imprimées"
    user_id = fields.Many2one("res.users")
    model_type = fields.Selection([('helpdesk', 'Assistance'),('calendar', 'Intervention calendrier')])
    model_id = fields.Integer(string="")
    last_date = fields.Datetime(string='Dernière édition')

class MyActionsBilled(models.Model):
    _name = "sinergis.myactions.billed"
    _description = "Interventions facturées"
    model_type = fields.Selection([('helpdesk', 'Assistance'),('calendar', 'Intervention calendrier')])
    model_id = fields.Integer(string="")