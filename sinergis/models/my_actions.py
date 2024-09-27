from odoo import api, fields, models, tools
from odoo.exceptions import ValidationError
from datetime import datetime

class MyActionsReinvoiced(models.Model):
    _name = "sinergis.myactions.reinvoiced"
    _description = "Interventions refacturées"
    model_type = fields.Selection([('helpdesk', 'Assistance'),('calendar', 'Intervention calendrier')])
    model_id = fields.Integer(string="")
    reinvoiced_company_id = fields.Many2one("res.company",string="Agence")

class MyActionsReinvoiced(models.Model):
    _name = "sinergis.myactions.transfer_x3"
    _description = "Detail du transfert au temps passé vers X3"

    model_type = fields.Selection([('helpdesk', 'Assistance'),('calendar', 'Intervention calendrier')])
    model_id = fields.Integer(string="")
    sinergis_x3_id = fields.Char(string="Numéro X3")
    sinergis_x3_price_subtotal = fields.Float(string="Total HT")
    sinergis_x3_price_total = fields.Float(string="Total TTC")

class MyActions(models.Model):
    _name = "sinergis.myactions"
    _auto = False

    link_id = fields.Integer(string="Identifiant")

    name = fields.Char(string="Sujet")

    origin = fields.Selection([('helpdesk', 'Assistance'),('calendar', 'Intervention calendrier')], string="Origine")
    date = fields.Datetime(readonly=True, string="Date")
    client = fields.Many2one("res.partner",string="Client")
    client_sinergis_x3_code = fields.Char(string='Code X3')
    sinergis_product_id = fields.Many2one("sale.products",string="Produit")
    sinergis_subproduct_id = fields.Many2one("sale.products.subproducts",string="Sous-produit")
    product = fields.Char(string = "Produit",compute="_compute_product")
    billing = fields.Selection([("À définir ultérieurement", "À définir ultérieurement"),("Contrat heure", "Contrat d'heures"),('Temps passé', 'Temps passé'),('Devis', 'Devis'),('Non facturable interne', 'Non facturable interne'),('Non facturable', 'Non facturable'),("Facturable à 0", "Facturable à 0"),("Avant-vente", "Avant-vente"),("Congés", "Congés")], string="Facturation")
    billing_type = fields.Selection([('Non facturable', 'Non facturable'),('Facturable', 'Facturable'),('Congés', 'Congés')], string="Facturable/Non facturable/Congés")
    billing_last_date = fields.Datetime(string="Date màj facturation")
    billing_order = fields.Many2one("sale.order",string="Commande", compute="_compute_billing_order")
    billing_order_margin = fields.Float(string="Marge de la commande", compute="_compute_billing_order_margin")
    billing_order_line = fields.Many2one("sale.order.line",string="Ligne de commande", compute="_compute_billing_order")
    has_project = fields.Boolean(string="A un projet ?", compute="_compute_has_project")
    time = fields.Float(string = "Temps")
    consultant = fields.Many2one('res.users',string="Consultant")
    company_id = fields.Many2one("res.company",string="Agence du consultant")
    partner_company_id = fields.Many2one("res.company",string="Agence associée au client")
    country_id = fields.Many2one("res.country",readonly=True,string="Pays du client")

    #Uniquement pour les activités du calendrier
    rapport_intervention_sent = fields.Boolean(String="RI envoyé")
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
    is_revised_billing = fields.Boolean(string="")

    # Refacturation

    is_rebillable = fields.Boolean(compute="_compute_is_rebillable")
    is_reinvoiced = fields.Boolean(string="")
    reinvoiced_company_id = fields.Many2one("res.company")

    # Transfert de commande vers X3 pour le temps passé

    is_transfered_x3 = fields.Boolean(string="")

    # Date de modification du ticket ou de l'évènement

    action_write_date = fields.Datetime(compute="_compute_action_write_date")

    #@api.model_cr
    #[16/10/22] Helpdesk : Variable 'date' fixée à 'start_time' pour ne pas voir la date de création mais la date de traitement du ticket
    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        query = """
            CREATE OR REPLACE VIEW sinergis_myactions AS (
            SELECT T.id AS id,T.origin,T.link_id,
            T.name,T.date,T.client,T.client_sinergis_x3_code,T.sinergis_product_id,T.sinergis_subproduct_id,T.billing,T.billing_type,T.billing_last_date,CAST(T.time AS float),T.consultant,T.company_id,T.partner_company_id,T.rapport_intervention_sent,T.contact,T.start_time,T.end_time,T.task,T.task2,T.resolution,T.is_solved,T.event_trip,T.movement_country,T.movement_area,T.country_id,T.is_billed,T.is_revised_billing,T.is_reinvoiced,T.reinvoiced_company_id,T.is_transfered_x3 FROM
                ((SELECT
                    'helpdesk' as origin,
                    2*ht.id as id,
                    ht.id as link_id,
                    ht.name as name,
                    ht.x_sinergis_helpdesk_ticket_start_time as date,
                    ht.partner_id as client,
                    rp.sinergis_x3_code as client_sinergis_x3_code,
                    ht.x_sinergis_helpdesk_ticket_produits_new as sinergis_product_id,
                    ht.x_sinergis_helpdesk_ticket_sous_produits_new as sinergis_subproduct_id,
                    REPLACE(ht.x_sinergis_helpdesk_ticket_facturation,'heures','heure') as billing,
                    CASE
                        WHEN ht.x_sinergis_helpdesk_ticket_facturation = 'À définir ultérieurement' OR ht.x_sinergis_helpdesk_ticket_facturation = 'Non facturable interne' OR ht.x_sinergis_helpdesk_ticket_facturation = 'Non facturable' OR ht.x_sinergis_helpdesk_ticket_facturation = 'Facturable à 0' OR ht.x_sinergis_helpdesk_ticket_facturation = 'Avant-vente'
                            THEN 'Non facturable'
                            ELSE 'Facturable'
                    END AS billing_type,
                    ht.x_sinergis_helpdesk_ticket_billing_last_date as billing_last_date,
                    CASE
                        WHEN ht.x_sinergis_helpdesk_ticket_facturation = 'Contrat heures' OR ht.x_sinergis_helpdesk_ticket_facturation = 'Devis'
                            THEN SUM(aal.unit_amount)::TEXT
                            ELSE ht.x_sinergis_helpdesk_ticket_temps_passe::TEXT
                    END AS time,
                    
                    ht.user_id as consultant,
                    ru.company_id as company_id,
                    rp.company_id as partner_company_id,
                    ht.x_sinergis_helpdesk_ticket_is_sent as rapport_intervention_sent,
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
                    CASE WHEN (SELECT count(id) FROM sinergis_myactions_billed AS bld WHERE bld.model_type='helpdesk' and bld.model_id=ht.id and bld.create_date < ht.x_sinergis_helpdesk_ticket_billing_last_date) > 0 THEN True else False END as is_revised_billing,
                    CASE WHEN (SELECT count(id) FROM sinergis_myactions_reinvoiced AS reinv WHERE reinv.model_type='helpdesk' and reinv.model_id=ht.id) > 0 THEN True else False END as is_reinvoiced,
                    CASE WHEN (SELECT count(id) FROM sinergis_myactions_reinvoiced AS reinv WHERE reinv.model_type='helpdesk' and reinv.model_id=ht.id) > 0 THEN (SELECT reinvoiced_company_id FROM sinergis_myactions_reinvoiced AS reinv WHERE reinv.model_type='helpdesk' and reinv.model_id=ht.id) else NULL END as reinvoiced_company_id,
                    CASE WHEN (SELECT count(id) FROM sinergis_myactions_transfer_x3 AS x3_transfer WHERE x3_transfer.model_type='helpdesk' and x3_transfer.model_id=ht.id) > 0 THEN True else False END as is_transfered_x3
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
                    rp.sinergis_x3_code as client_sinergis_x3_code,
                    ce.x_sinergis_calendar_event_produits_new as sinergis_product_id,
                    ce.x_sinergis_calendar_event_sous_produits_new as sinergis_subproduct_id,
                    REPLACE(ce.x_sinergis_calendar_event_facturation,'heures','heure') as billing,
                    CASE
                        WHEN ce.x_sinergis_calendar_event_facturation = 'À définir ultérieurement' OR ce.x_sinergis_calendar_event_facturation = 'Non facturable interne' OR ce.x_sinergis_calendar_event_facturation = 'Non facturable' OR ce.x_sinergis_calendar_event_facturation = 'Facturable à 0' OR ce.x_sinergis_calendar_event_facturation = 'Avant-vente'
                            THEN 'Non facturable'
                        WHEN ce.x_sinergis_calendar_event_facturation = 'Congés'
                            THEN 'Congés'
                        ELSE 'Facturable'
                    END AS billing_type,
                    ce.x_sinergis_calendar_event_billing_last_date as billing_last_date,
                    CASE
                        WHEN ce.x_sinergis_calendar_event_facturation = 'Contrat heure' OR ce.x_sinergis_calendar_event_facturation = 'Devis'
                            THEN SUM(aal.unit_amount)::TEXT
                            ELSE ce.x_sinergis_calendar_duree_facturee::TEXT
                    END AS time,
                    ce.user_id as consultant,
                    ru.company_id as company_id,
                    rp.company_id as partner_company_id,
                    ce.x_sinergis_calendar_event_is_sent as rapport_intervention_sent,
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
                    CASE WHEN (SELECT count(id) FROM sinergis_myactions_billed AS bld WHERE bld.model_type='calendar' and bld.model_id=ce.id and bld.create_date < ce.x_sinergis_calendar_event_billing_last_date) > 0 THEN True else False END as is_revised_billing,
                    CASE WHEN (SELECT count(id) FROM sinergis_myactions_reinvoiced AS reinv WHERE reinv.model_type='calendar' and reinv.model_id=ce.id) > 0 THEN True else False END as is_reinvoiced,
                    CASE WHEN (SELECT count(id) FROM sinergis_myactions_reinvoiced AS reinv WHERE reinv.model_type='calendar' and reinv.model_id=ce.id) > 0 THEN (SELECT reinvoiced_company_id FROM sinergis_myactions_reinvoiced AS reinv WHERE reinv.model_type='calendar' and reinv.model_id=ce.id) else NULL END as reinvoiced_company_id,
                    CASE WHEN (SELECT count(id) FROM sinergis_myactions_transfer_x3 AS x3_transfer WHERE x3_transfer.model_type='calendar' and x3_transfer.model_id=ce.id) > 0 THEN True else False END as is_transfered_x3
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
            rec.product = f"{rec.sinergis_product_id.name if rec.sinergis_product_id.name else ''} {rec.sinergis_subproduct_id.name if rec.sinergis_subproduct_id.name else ''}"

    @api.depends('intervention_count')
    def _compute_intervention_count (self):
        for rec in self:
            if rec.origin == "helpdesk":
                rec.intervention_count = self.env['account.analytic.line'].search_count([('x_sinergis_account_analytic_line_ticket_id', '=', rec.link_id)])
            elif rec.origin == "calendar":
                rec.intervention_count = self.env['account.analytic.line'].search_count([('x_sinergis_account_analytic_line_event_id', '=', rec.link_id)])

    @api.depends('has_project')
    def _compute_has_project(self):
        for rec in self:
            has_project=False
            if rec.billing_order_line:
                project_ids = self.env['project.project'].search([('sale_line_id','=',rec.billing_order_line.id)])
                if len(project_ids) > 0:
                    has_project = True
            rec.has_project = has_project

    @api.depends('billing_order_margin')
    def _compute_billing_order_margin(self):
        for rec in self:
            # Nombre d'activités dans la commande concernée
            count = len(self.env['sinergis.myactions'].search([('billing_order', '=', rec.billing_order.id)]))
            if count > 0: # Pour ne pas diviser par 0
                rec.billing_order_margin = rec.billing_order.margin/count
            else :
                rec.billing_order_margin = 0

    @api.depends('billing_order')
    def _compute_billing_order(self):
        for rec in self:
            if rec.origin == "helpdesk":
                rec.billing_order = self.env['helpdesk.ticket'].search([('id','=',rec.link_id)]).x_sinergis_helpdesk_ticket_sale_order
                rec.billing_order_line = self.env['helpdesk.ticket'].search([('id','=',rec.link_id)]).x_sinergis_helpdesk_ticket_sale_order_line
            else:
                rec.billing_order = self.env['calendar.event'].search([('id','=',rec.link_id)]).x_sinergis_calendar_event_sale_order
                rec.billing_order_line = self.env['calendar.event'].search([('id','=',rec.link_id)]).x_sinergis_calendar_event_sale_order_line

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

    @api.depends('is_rebillable')
    def _compute_is_rebillable (self):
        for rec in self:
            if (rec.billing == "Contrat heure" or rec.billing == "Devis" or rec.billing == "Temps passé") and rec.partner_company_id != rec.company_id:
                rec.is_rebillable = True
            else:
                rec.is_rebillable = False

    @api.depends('action_write_date')
    def _compute_action_write_date(self):
        for rec in self:
            if rec.origin == "helpdesk":
                rec.action_write_date = self.env['helpdesk.ticket'].search([('id','=',rec.link_id)]).write_date
            elif rec.origin == "calendar":
                rec.action_write_date = self.env['calendar.event'].search([('id','=',rec.link_id)]).write_date
            else:
                rec.action_write_date = False

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
        if self.env.user.has_group('sinergis.group_myactions_employee') == False or self.env.user.has_group('sinergis_x3.group_myactivity_transfer') == True :
            if self.env['sinergis.myactions.billed'].search_count([('model_type', '=', self.origin),('model_id', '=', self.link_id)]) == 0:
                if self.origin == "helpdesk":
                    billing_type = self.env['helpdesk.ticket'].search([('id','=',self.link_id)]).x_sinergis_helpdesk_ticket_facturation
                    time = self.env['helpdesk.ticket'].search([('id','=',self.link_id)]).x_sinergis_helpdesk_ticket_temps_cumule
                elif self.origin == "calendar":
                    billing_type = self.env['calendar.event'].search([('id','=',self.link_id)]).x_sinergis_calendar_event_facturation
                    time = self.env['calendar.event'].search([('id','=',self.link_id)]).x_sinergis_calendar_event_temps_cumule
                data = {
                    'model_type': self.origin,
                    'model_id': self.link_id,
                    'billing_type': billing_type,
                    'time': time
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

    def show_revised_billing (self):
        context = {
            'name': 'Changement des données de facturation',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'sinergis.myactions.billed',
            'res_id': self.env['sinergis.myactions.billed'].search([('model_type', '=', self.origin),('model_id', '=', self.link_id)]).id,
            'target': 'new',
            'flags':{'mode':'readonly'},
            }
        return context
        

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

    # Bouton depuis la tree view
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

    def send_reports(self):
        template_id = self.env['ir.model.data']._xmlid_to_res_id('sinergis.sinergis_mail_myactions_report', raise_if_not_found=False)
        report_action = self.env.ref('sinergis.sinergis_mail_calendar_rapport_intervention').report_action(
            self.env['sinergis.myactions'].search([('id', '=', self.ids)])
        )
        
        report_pdf = self.env['ir.actions.report'].sudo()._get_report_from_name('sinergis.sinergis_report_myactions')._render_qweb_pdf(self.ids)[0]
        attachment = self.env['ir.attachment'].create({
            'name': 'myactions_report.pdf',
            'type': 'binary',
            'datas': base64.b64encode(report_pdf),
            'mimetype': 'application/pdf'
        })

        compose_ctx = dict(
            default_composition_mode='comment',
            default_model='sinergis.myactions',
            default_res_ids=self.ids,
            default_use_template=bool(template_id),
            default_template_id=template_id,
            default_attachment_ids=[attachment.id],
            default_partner_ids=False,
            mail_tz=self.env.user.tz,
        )

        return {
            'type': 'ir.actions.act_window',
            'name': "Envoyer Rapport",
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': compose_ctx,
        }


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

    # DEV EN COURS : Transfert de la presta vers X3 pour les temps passé

    def start_x3_transfer_button(self):
        #Vérification du produit et du sous-produit
        if not self.sinergis_product_id:
            raise ValidationError("Il manque le produit de cette activité pour pouvoir la transférer vers X3.")
        if not self.sinergis_subproduct_id:
            raise ValidationError("Il manque le produit de cette activité pour pouvoir la transférer vers X3.")
        result = self._send_order_for_x3()
        if result[0] == False:
            raise ValidationError(result[1])
        else:
            # Création de l'objet contenant toutes les informations sur le transfert X3
            self.env["sinergis.myactions.transfer_x3"].create({
                "model_type": self.origin,
                "model_id": self.link_id,
                "sinergis_x3_id": result[1]['sinergis_x3_id'],
                "sinergis_x3_price_subtotal": result[1]['sinergis_x3_price_subtotal'],
                "sinergis_x3_price_total": result[1]['sinergis_x3_price_total'],
            })
            # On marque la ligne comme facturée
            self.invoiced_button()

    def open_x3_transfer_button(self):
        return {
            'name': 'Detail du transfert',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'sinergis.myactions.transfer_x3',
            'res_id': self.env['sinergis.myactions.transfer_x3'].search([('model_id', '=', self.link_id),('model_type', '=', self.origin)],limit=1).id,
            'target': 'new',
            'flags':{'mode':'readonly'},
            }

    def order_verification_for_x3 (self):
        # Vérification des éléments manquants
        missing_elements = []
        if not self.client:
            missing_elements.append("client")
        if not self.sinergis_product_id:
            missing_elements.append("produit Sinergis")
        if not self.sinergis_subproduct_id:
            missing_elements.append("sous-produit Sinergis")
        if not self.consultant:
            missing_elements.append("consultant")
        if not self.company_id:
            missing_elements.append("société Sinergis")
        if not self.date:
            missing_data.append("date de l'activité")

        # Vérification du transcodage
        if self.sinergis_product_id and self.sinergis_subproduct_id:
            if not self.client.sinergis_x3_code:
                missing_elements.append("code X3 du client")
            if not self.env["sinergis_x3.settings.sinergis_product"].search([("sinergis_product_id","=",self.sinergis_product_id.id)]):
                missing_elements.append(f"transcodage du produit ({self.sinergis_product_id.name})")
            if not self.env["sinergis_x3.settings.sinergis_subproduct"].search([("sinergis_subproduct_id","=",self.sinergis_subproduct_id.id)]):
                missing_elements.append(f"transcodage du sous-produit ({self.sinergis_subproduct_id.name})")
            if not self.env["sinergis_x3.settings.commercial"].search([("user_id","=",self.consultant.id)]):
                missing_elements.append(f"transcodage du consultant ({self.consultant.name})")
            if not self.env["sinergis_x3.settings.company"].search([("company_id","=",self.company_id.id)]):
                missing_elements.append(f"transcodage de la société Sinergis ({self.company_id.name})")

        return {
            "state": len(missing_elements) == 0,
            "missing_elements": missing_elements
        }

    # Bouton depuis la tree view
    # Envoyer plusieurs "temps passé" vers X3
    def send_orders_for_x3 (self):
        enable = self.env['ir.config_parameter'].sudo().get_param('sinergis_x3.enable')
        if not enable:
            raise ValidationError("Le module de transfert d'X3 n'est pas activé. Veuillez l'activer dans les paramètres.")
        # Vérification pour chaque client des données
        for rec in self:
            if rec.billing != "Temps passé":
                continue
            verif = rec.order_verification_for_x3()
            if not verif["status"] :
                raise ValidationError(f"L'activité '{rec.name}' ne peut pas être transférée. Les données manquantes sont les suivantes: {' ,'.join(verif['missing_elements'])}.")
        # Démarage du transfert
        for rec in self:
            if rec.billing != "Temps passé":
                continue
            start_x3_transfer_button()
            

class MyActionsPrinted(models.Model):
    _name = "sinergis.myactions.printed"
    _description = "Activités imprimées"
    user_id = fields.Many2one("res.users")
    model_type = fields.Selection([('helpdesk', 'Assistance'),('calendar', 'Intervention calendrier')])
    model_id = fields.Integer(string="")
    last_date = fields.Datetime(string='Dernière édition')

class MyActionsValidFlag(models.Model):
    _name = "sinergis.myactions.valid_flag"
    _description = "Dossiers validés"
    user_id = fields.Many2one("res.users")
    model_type = fields.Selection([('helpdesk', 'Assistance'),('calendar', 'Intervention calendrier')])
    model_id = fields.Integer(string="")

class MyActionsBilled(models.Model):
    _name = "sinergis.myactions.billed"
    _description = "Interventions facturées"
    model_type = fields.Selection([('helpdesk', 'Assistance'),('calendar', 'Intervention calendrier')])
    model_id = fields.Integer(string="")
    # Sauvegardes de la facturation en cas de modification
    billing_type = fields.Char(string="Ancienne facturation")
    new_billing_type = fields.Char(string="Nouvelle facturation", compute="_compute_new_values")
    time = fields.Float(string="Ancien temps")
    new_time = fields.Float(string="Nouveau temps", compute="_compute_new_values")

    # Confirmer là MàJ sur X3 de la facturation après changement du côté du consultant
    def confirm_billing_change(self):
        data = {
                    'model_type': self.model_type,
                    'model_id': self.model_id,
                    'billing_type': self.new_billing_type,
                    'time': self.new_time
                }
        self.env['sinergis.myactions.billed'].create(data)
        self.unlink()

    @api.depends("new_time")
    def _compute_new_values(self):
        for rec in self:
            if rec.model_type == "helpdesk":
                ticket = self.env['helpdesk.ticket'].search([('id','=',rec.model_id)])
                rec.new_billing_type = ticket.x_sinergis_helpdesk_ticket_facturation
                rec.new_time = ticket.x_sinergis_helpdesk_ticket_temps_cumule
            elif rec.model_type == "calendar":
                event = self.env['calendar.event'].search([('id','=',rec.model_id)])
                rec.new_billing_type = event.x_sinergis_calendar_event_facturation
                rec.new_time = event.x_sinergis_calendar_event_temps_cumule