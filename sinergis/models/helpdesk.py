from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import pytz
import re


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    # --FORM--
    
    # Date nécessaire pour trier les tickets
    sort_date = fields.Datetime("Date de tri", default=lambda self: datetime.now().strftime("%Y-%m-%d %H:%M:%S"), readonly=True)

    #Override
    #company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company, readonly=True,related='')
    team_id = fields.Many2one(default=lambda self: self.env['helpdesk.team'].search([], limit=1))

    stage_id = fields.Many2one(domain=False)

    x_sinergis_helpdesk_ticket_planned_intervention = fields.Boolean(default=0)
    x_sinergis_helpdesk_ticket_planned_intervention_text = fields.Char(string=" ", compute="_compute_x_sinergis_helpdesk_ticket_planned_intervention_text")
    x_sinergis_helpdesk_ticket_planned_intervention_user_id = fields.Many2one("res.users",string='Dernier utilisateur: Intervention à planifier')

    x_sinergis_helpdesk_ticket_client_douteux = fields.Boolean(related="partner_id.x_sinergis_societe_litige_douteux",default=False)
    x_sinergis_helpdesk_ticket_client_bloque = fields.Boolean(related="partner_id.x_sinergis_societe_litige_bloque",default=False)
    x_sinergis_helpdesk_ticket_client_bloque_remarques = fields.Text(related="partner_id.x_sinergis_societe_litige_bloque_remarques",default=False)

    #Colonne de gauche
    #Ancien système de produits, à ne plus utiliser
    x_sinergis_helpdesk_ticket_produits = fields.Selection([('CEGID', 'CEGID'), ('E2TIME', 'E2TIME'), ('MESBANQUES', 'MESBANQUES'), ('OPEN BEE', 'OPEN BEE'), ('QUARKSUP', 'QUARKSUP'), ('SAGE 100', 'SAGE 100'), ('SAGE 1000', 'SAGE 1000'), ('SAP', 'SAP'), ('VIF', 'VIF'), ('X3', 'SAGE X3'), ('XLSOFT', 'XLSOFT'), ('XRT', 'XRT'), ('SILAE','SILAE'), ('DIVERS', 'DIVERS')], string="Produits")
    #Nouveau système de produits
    x_sinergis_helpdesk_ticket_produits_new = fields.Many2one("sale.products",string="Produit")
    x_sinergis_helpdesk_ticket_sous_produits_new = fields.Many2one("sale.products.subproducts",string="Sous-produit")

    x_sinergis_helpdesk_ticket_produits_cegid = fields.Selection([('LIASSE', 'LIASSE')], string="Module CEGID")
    x_sinergis_helpdesk_ticket_produits_sage100 = fields.Selection([('CPT', 'CPT'),('GES', 'GES'),('IMM', 'IMM'),('MDP', 'MDP'),('TRE', 'TRE'),('SCD', 'SCD'),('BI', 'BI'),('ECF', 'ECF'),('PAI', 'PAI'),('SEE', 'SEE'),('BATIGEST', 'BATIGEST'),('DEV', 'DEV'),('SRC', 'SRC'),('CRM', 'CRM')], string="Module Sage 100")
    x_sinergis_helpdesk_ticket_produits_sage1000 = fields.Selection([('CPT', 'CPT'),('IMM', 'IMM'),('TRE', 'TRE'),('BP', 'BP'),('RAPPRO', 'RAPPRO'),('ENGA', 'ENGA'),('SCB', 'SCB'),('BI', 'BI'),('DEV', 'DEV')], string="Module Sage 1000")
    x_sinergis_helpdesk_ticket_produits_sap = fields.Selection([('CPT', 'CPT'),('GES', 'GES'),('DEV', 'DEV')], string="Module SAP")
    x_sinergis_helpdesk_ticket_produits_x3 = fields.Selection([('CPT', 'CPT'),('GES', 'GES'),('CRYSTAL', 'CRYSTAL'),('BI', 'BI'),('DEV', 'DEV'),('HRM', 'HRM')], string="Module Sage X3")
    x_sinergis_helpdesk_ticket_produits_divers = fields.Selection([('ODOO', 'ODOO'),('SCANFACT', 'SCANFACT'),('WINDEV', 'WINDEV'),('AUTRE', 'AUTRE')], string="Module Divers")

    x_sinergis_helpdesk_ticket_produit_nom_complet = fields.Char(string="Produit", readonly=True, compute="_compute_x_sinergis_helpdesk_ticket_produit_nom_complet")

    x_sinergis_helpdesk_ticket_type_client = fields.Selection(related="x_sinergis_helpdesk_ticket_produits_new.type")

    x_sinergis_helpdesk_ticket_show_facturation = fields.Boolean(default=0)

    x_sinergis_helpdesk_ticket_start_time = fields.Datetime(string="Début et fin de l'intervention")
    x_sinergis_helpdesk_ticket_end_time = fields.Datetime(string='')

    x_sinergis_helpdesk_ticket_ticket_resolution = fields.Html(string="Description de l'intervention")

    x_sinergis_helpdesk_ticket_facturation = fields.Selection([("À définir ultérieurement", "À définir ultérieurement"),("Contrat heures", "Contrat d'heures"),('Temps passé', 'Temps passé'),('Devis', 'Devis'),('Non facturable interne', 'Non facturable interne'),('Non facturable', 'Non facturable'),("Facturable à 0", "Facturable à 0"),("Avant-vente", "Avant-vente")], string="Facturation")
    x_sinergis_helpdesk_ticket_project = fields.Many2one("project.project", string="Projet")
    x_sinergis_helpdesk_ticket_tache = fields.Many2one("project.task", string="Tâche")
    x_sinergis_helpdesk_ticket_tache2 = fields.Many2one("project.task", string="Contrat d'heures")
    x_sinergis_helpdesk_ticket_tache_information = fields.Char(string="")
    x_sinergis_helpdesk_ticket_sale_order = fields.Many2one("sale.order", string="Commande", compute="_compute_x_sinergis_helpdesk_ticket_sale_order")
    x_sinergis_helpdesk_ticket_sale_order_line = fields.Many2one("sale.order.line", string="Ligne de commande", compute="_compute_x_sinergis_helpdesk_ticket_sale_order")

    x_sinergis_helpdesk_ticket_temps_passe = fields.Float(string="Temps passé")

    x_sinergis_helpdesk_ticket_is_solved = fields.Boolean(string="Le ticket est-il résolu ?",default=False)

    # Ajout de la notion de rapport d'intervention envoyé
    x_sinergis_helpdesk_ticket_is_sent = fields.Boolean(string="Rapport Envoyé")
    x_sinergis_helpdesk_ticket_sent_date = fields.Datetime(string="Date d'envoie")
    x_sinergis_helpdesk_ticket_sent_mail = fields.Many2one("mail.mail", string="Mail")
    x_sinergis_helpdesk_ticket_sent_emails = fields.Char(string="Emails", related="x_sinergis_helpdesk_ticket_sent_mail.x_sinergis_email_list")

    x_sinergis_helpdesk_ticket_intervention_count = fields.Integer(string="Nombre d'interventions", compute="_compute_x_sinergis_helpdesk_ticket_intervention_count", group_operator="sum")
    x_sinergis_helpdesk_ticket_temps_cumule = fields.Float(string="Temps cumulé", compute="_compute_x_sinergis_helpdesk_ticket_temps_cumule")

    x_sinergis_helpdesk_ticket_is_facturee = fields.Boolean(string="Présence d'un contrat d'heures chez le client :",default=False)

    # 14 Aout 2023 : Ajout d'une date de modification de la facturation poru vérifier si cela n'a pas déjà été facturé
    x_sinergis_helpdesk_ticket_billing_last_date = fields.Datetime(string="Date de modification des données de facturation", default=False)

    #Colonne de droite
    x_sinergis_helpdesk_ticket_partner_company_id = fields.Many2one('res.company', string="Agence rattachée", compute="_compute_x_sinergis_helpdesk_ticket_partner_company_id", store=True)
    x_sinergis_helpdesk_ticket_partner_company_name = fields.Char(compute="_compute_x_sinergis_helpdesk_ticket_partner_company_name")
    
    x_sinergis_helpdesk_ticket_contact = fields.Many2one("res.partner",string="Contact")
    x_sinergis_helpdesk_ticket_contact_fixe = fields.Char(string="Fixe contact", related="x_sinergis_helpdesk_ticket_contact.phone",default=False)
    x_sinergis_helpdesk_ticket_contact_mobile = fields.Char(string="Mobile contact", related="x_sinergis_helpdesk_ticket_contact.mobile",default=False)
    x_sinergis_helpdesk_ticket_contact_mail = fields.Char(string="Mail contact", related="x_sinergis_helpdesk_ticket_contact.email",default=False)
    x_sinergis_helpdesk_ticket_contact_note = fields.Text(compute="_compute_x_sinergis_helpdesk_ticket_contact_note")

    x_sinergis_helpdesk_ticket_contrat_heures = fields.One2many('project.task',compute="_compute_x_sinergis_helpdesk_ticket_contrat_heures",readonly=True,string="Contrats d'heures du client :")

    #Taches
    x_sinergis_helpdesk_ticket_taches = fields.One2many('project.task',compute="_compute_tasks",readonly=True)

    # 3 Février 2023 : Ajout de l'alerte si le client a répondu après avoir envoyé le ticket
    x_sinergis_helpdesk_ticket_client_answer = fields.Boolean(string="Réponse client", compute="_compute_x_sinergis_helpdesk_ticket_client_answer", store=True)
    x_sinergis_helpdesk_ticket_client_answer_date = fields.Datetime(string="Dernier mail le")

    x_sinergis_helpdesk_last_call = fields.Datetime(string="Date et heure du dernier appel",default=False)
    x_sinergis_helpdesk_last_call_user_id = fields.Many2one("res.users",string="Dernier utilisateur: le client n'a pas répondu")

    @api.depends('x_sinergis_helpdesk_ticket_planned_intervention_text')
    def _compute_x_sinergis_helpdesk_ticket_planned_intervention_text (self):
        for rec in self:
            if rec.x_sinergis_helpdesk_ticket_planned_intervention:
                rec.x_sinergis_helpdesk_ticket_planned_intervention_text = "Intervention à planifier"
            else:
                rec.x_sinergis_helpdesk_ticket_planned_intervention_text = False

    @api.depends('x_sinergis_helpdesk_ticket_produit_nom_complet')
    def _compute_x_sinergis_helpdesk_ticket_produit_nom_complet (self):
        for rec in self:
            if rec.x_sinergis_helpdesk_ticket_produits_new and rec.x_sinergis_helpdesk_ticket_sous_produits_new:
                rec.x_sinergis_helpdesk_ticket_produit_nom_complet = rec.x_sinergis_helpdesk_ticket_produits_new.name + " " + rec.x_sinergis_helpdesk_ticket_sous_produits_new.name
            elif rec.x_sinergis_helpdesk_ticket_produits_new:
                rec.x_sinergis_helpdesk_ticket_produit_nom_complet = rec.x_sinergis_helpdesk_ticket_produits_new.name
            else:
                rec.x_sinergis_helpdesk_ticket_produit_nom_complet = ""

    @api.depends("x_sinergis_helpdesk_ticket_sale_order", "x_sinergis_helpdesk_ticket_sale_order_line")
    def _compute_x_sinergis_helpdesk_ticket_sale_order (self):
        for rec in self:
            if rec.x_sinergis_helpdesk_ticket_facturation == "Devis":
                rec.x_sinergis_helpdesk_ticket_sale_order = rec.x_sinergis_helpdesk_ticket_project.sale_line_id.order_id
                rec.x_sinergis_helpdesk_ticket_sale_order_line = rec.x_sinergis_helpdesk_ticket_project.sale_line_id
            elif rec.x_sinergis_helpdesk_ticket_facturation == "Contrat heures":
                rec.x_sinergis_helpdesk_ticket_sale_order = rec.x_sinergis_helpdesk_ticket_tache2.sale_line_id.order_id
                rec.x_sinergis_helpdesk_ticket_sale_order_line = rec.x_sinergis_helpdesk_ticket_tache2.sale_line_id
            else:
                rec.x_sinergis_helpdesk_ticket_sale_order = False
                rec.x_sinergis_helpdesk_ticket_sale_order_line = False

    #@api.depends('x_sinergis_helpdesk_ticket_is_sent','x_sinergis_helpdesk_ticket_sent_date','x_sinergis_helpdesk_ticket_sent_mail')
    #def _compute_x_sinergis_helpdesk_ticket_sent_report (self):
    #    for rec in self:
    #        mail = self.env['mail.mail'].search([("model","=","helpdesk.ticket"),("res_id","=",rec.id),("subject","ilike","Rapport d'intervention")],limit=1)
    #        if mail :
    #            rec.x_sinergis_helpdesk_ticket_is_sent = True
    #            rec.x_sinergis_helpdesk_ticket_sent_date = mail.date
    #            rec.x_sinergis_helpdesk_ticket_sent_mail = mail
    #        else:
    #            rec.x_sinergis_helpdesk_ticket_is_sent = False
    #            rec.x_sinergis_helpdesk_ticket_sent_date = False
    #            rec.x_sinergis_helpdesk_ticket_sent_mail = False

    def action_x_sinergis_helpdesk_ticket_sent_report(self, mail):
        for rec in self:
            rec.x_sinergis_helpdesk_ticket_is_sent = True
            rec.x_sinergis_helpdesk_ticket_sent_date = mail.date
            rec.x_sinergis_helpdesk_ticket_sent_mail = mail

    @api.depends('x_sinergis_helpdesk_ticket_intervention_count')
    def _compute_x_sinergis_helpdesk_ticket_intervention_count (self):
        for rec in self:
            rec.x_sinergis_helpdesk_ticket_intervention_count = self.env['account.analytic.line'].search_count([('x_sinergis_account_analytic_line_ticket_id', '=', rec.id)])

    @api.depends('x_sinergis_helpdesk_ticket_temps_cumule')
    def _compute_x_sinergis_helpdesk_ticket_temps_cumule (self):
        for rec in self:
            if rec.x_sinergis_helpdesk_ticket_facturation == "Contrat heures" or rec.x_sinergis_helpdesk_ticket_facturation == "Devis":
                rec.x_sinergis_helpdesk_ticket_temps_cumule = sum(rec.env['account.analytic.line'].search([('x_sinergis_account_analytic_line_ticket_id', '=', rec.id)]).mapped('unit_amount'))
            else :
                rec.x_sinergis_helpdesk_ticket_temps_cumule = rec.x_sinergis_helpdesk_ticket_temps_passe

    @api.depends("x_sinergis_helpdesk_ticket_partner_company_id","partner_id")
    def _compute_x_sinergis_helpdesk_ticket_partner_company_id(self):
        for ticket in self:
            ticket.x_sinergis_helpdesk_ticket_partner_company_id = ticket.partner_id.company_id
            
    @api.depends("x_sinergis_helpdesk_ticket_partner_company_id")
    def _compute_x_sinergis_helpdesk_ticket_partner_company_name(self):
        for ticket in self:
            ticket.x_sinergis_helpdesk_ticket_partner_company_name = ticket.x_sinergis_helpdesk_ticket_partner_company_id.name
    
    @api.depends("x_sinergis_helpdesk_ticket_contact_note","x_sinergis_helpdesk_ticket_contact")
    def _compute_x_sinergis_helpdesk_ticket_contact_note(self):
        text = re.compile('<.*?>')
        for ticket in self :
            if ticket.x_sinergis_helpdesk_ticket_contact.comment:
                comment = re.sub(text, '', ticket.x_sinergis_helpdesk_ticket_contact.comment)
                if len(comment) <= 2 :
                    ticket.x_sinergis_helpdesk_ticket_contact_note = False
                else :
                    ticket.x_sinergis_helpdesk_ticket_contact_note = comment
            else:
                ticket.x_sinergis_helpdesk_ticket_contact_note = False
    
    @api.depends("x_sinergis_helpdesk_ticket_contrat_heures")
    def _compute_x_sinergis_helpdesk_ticket_contrat_heures(self):
        for task in self:
            domain = []
            domain.append(('name','ilike','HEURES'))
            domain.append(('partner_id', '=', task.partner_id.id))
            task.x_sinergis_helpdesk_ticket_contrat_heures = self.env["project.task"].search(domain)
            
    @api.onchange("user_id")
    def on_change_user_id(self):
        if not self.x_sinergis_helpdesk_ticket_start_time and not self.x_sinergis_helpdesk_ticket_end_time:
            self.x_sinergis_helpdesk_ticket_start_time = datetime.now()
            self.x_sinergis_helpdesk_ticket_end_time = datetime.now()


    @api.onchange("stage_id")
    def on_change_stage_id_sinergis(self):
        if self.stage_id.name == "En cours":
            self.x_sinergis_helpdesk_ticket_is_solved = False
        elif self.stage_id.name == "Résolu":
            user_id = self.user_id
            if user_id != self.env.user and not self.env.user.has_group('sinergis.group_helpdesk_admin'):
                raise ValidationError("Vous ne pouvez pas marquer un ticket que ne vous est pas assigné comme résolu.")
            self.x_sinergis_helpdesk_ticket_is_solved = True

    @api.onchange("x_sinergis_helpdesk_ticket_produits_new")
    def on_change_x_sinergis_helpdesk_ticket_produits_new(self):
        self.x_sinergis_helpdesk_ticket_sous_produits_new = False

    @api.onchange("x_sinergis_helpdesk_ticket_start_time", "x_sinergis_helpdesk_ticket_end_time")
    def _update_temps_passe (self):
        if self.x_sinergis_helpdesk_ticket_end_time and self.x_sinergis_helpdesk_ticket_start_time:
            self.x_sinergis_helpdesk_ticket_temps_passe = (self.x_sinergis_helpdesk_ticket_end_time - self.x_sinergis_helpdesk_ticket_start_time).total_seconds() / 3600

    @api.depends('x_sinergis_helpdesk_ticket_taches')
    def _compute_tasks (self):
        HelpdeskTicket.updateTasks(self)

    @api.depends('message_ids')
    def _compute_x_sinergis_helpdesk_ticket_client_answer (self):
        for rec in self:
            all_messages = self.env["mail.message"].search(["&", ("res_id", "=", rec.id), ("model", "=", "helpdesk.ticket")])
            email_count = 0
            if all_messages:
                last_mail_date = False
                for message in all_messages:
                    if message.message_type == "email":
                        email_count += 1
                        if not last_mail_date:
                            last_mail_date = message.date
                # Mise à jour de la date du dernier message
                rec.x_sinergis_helpdesk_ticket_client_answer_date = last_mail_date
                if email_count >= 2 :
                    rec.x_sinergis_helpdesk_ticket_client_answer = True
                    # Mise à jour de la date de tri uniquement si le dernier message est un mail
                    message = self.env["mail.message"].search(["&", ("res_id", "=", rec.id), ("model", "=", "helpdesk.ticket")], limit=1, order='id desc')
                    if message.message_type == "email":
                        self.sort_date = message.date.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    rec.x_sinergis_helpdesk_ticket_client_answer = False
            else:
                rec.x_sinergis_helpdesk_ticket_client_answer = False

    @api.onchange("partner_id")
    def on_change_partner_id(self):
        self.x_sinergis_helpdesk_ticket_contact = False
        self.x_sinergis_helpdesk_ticket_project = False
        self.x_sinergis_helpdesk_ticket_tache = False
        self.x_sinergis_helpdesk_ticket_tache2 = False
        self.x_sinergis_helpdesk_ticket_tache_information = False
        if self.partner_id:
            if self.partner_id.x_sinergis_societe_litige_bloque:
                raise ValidationError("Le client est bloqué pour la raison suivante : "+ self.partner_id.x_sinergis_societe_litige_bloque_remarques +". Vous ne pouvez pas intervenir, merci de vous rapprocher d'un commercial.")
            if self.partner_id.x_sinergis_societe_suspect:
                raise ValidationError("Le client est un suspect. Vous ne pouvez pas intervenir, merci de vous rapprocher d'un commercial.")
            for tag in self.partner_id.category_id:
                if tag.name == "PROSPECT":
                    raise ValidationError("Le client est un prospect. Vous ne pouvez pas intervenir, merci de vous rapprocher d'un commercial.")
        # Si le ticket est un ticket d'un client PARINET : Mettre automatiquement en "Non facturable" la facturation
        if self.partner_id.company_id.name == "PARINET":
            self.x_sinergis_helpdesk_ticket_facturation = "Temps passé"
        
        HelpdeskTicket.updateTasks(self)

    @api.onchange("x_sinergis_helpdesk_ticket_facturation")
    def on_change_x_sinergis_helpdesk_ticket_facturation(self):
        # Si le client est douteux, on autorise uniquement la facturation sur devis
        if self.x_sinergis_helpdesk_ticket_client_douteux:
            if self.x_sinergis_helpdesk_ticket_facturation != "Devis":
                raise ValidationError("Le client est douteux, vous ne pouvez séléctionner que la facturation sur Devis.")
        self.x_sinergis_helpdesk_ticket_project = False
        self.x_sinergis_helpdesk_ticket_tache = False
        self.x_sinergis_helpdesk_ticket_tache2 = False
        self.x_sinergis_helpdesk_ticket_tache_information = False
        HelpdeskTicket.updateTasks(self)

    @api.onchange("x_sinergis_helpdesk_ticket_project")
    def on_change_x_sinergis_helpdesk_ticket_project(self):
        self.x_sinergis_helpdesk_ticket_tache = False
        self.x_sinergis_helpdesk_ticket_tache2 = False
        self.x_sinergis_helpdesk_ticket_tache_information = False
        HelpdeskTicket.updateTasks(self)

    @api.onchange("x_sinergis_helpdesk_ticket_tache")
    def on_change_x_sinergis_helpdesk_ticket_tache(self):
        HelpdeskTicket.updateTasks(self)
        HelpdeskTicket.set_task_information(self)

    @api.onchange("x_sinergis_helpdesk_ticket_tache2")
    def on_change_x_sinergis_helpdesk_ticket_tache2(self):
        HelpdeskTicket.updateTasks(self)
        HelpdeskTicket.set_task_information(self)

    @api.onchange("x_sinergis_helpdesk_ticket_is_solved")
    def on_change_x_sinergis_helpdesk_ticket_is_solved(self):
        if self.x_sinergis_helpdesk_ticket_is_solved:
            self.stage_id = self.env['helpdesk.stage'].search([('name','=',"Résolu")])
        elif self.x_sinergis_helpdesk_ticket_show_facturation: #Pour eviter un changement d'état à la création d'un ticket
            self.stage_id = self.env['helpdesk.stage'].search([('name','=',"En cours")])

    @api.onchange("x_sinergis_helpdesk_ticket_is_sent")
    def on_change_x_sinergis_helpdesk_ticket_is_sent(self):
        event = self.env['calendar.event'].search([("x_sinergis_calendar_event_helpdesk_ticket_id","=",self.id)], limit=1)
        if event :
            event.x_sinergis_calendar_event_is_sent = self.x_sinergis_helpdesk_ticket_is_sent
            event.x_sinergis_calendar_event_sent_date = self.x_sinergis_helpdesk_ticket_sent_date
            event.x_sinergis_calendar_event_sent_mail = self.x_sinergis_helpdesk_ticket_sent_mail

    def updateTasks (self):
        for event in self:
            domain = []
            if self.x_sinergis_helpdesk_ticket_facturation != "Contrat heures":
                if self.partner_id:
                    domain.append(('name','not ilike','HEURES'))
                    domain.append(('partner_id', '=', self.partner_id.id))
                    if self.x_sinergis_helpdesk_ticket_project:
                        domain.append(('project_id', '=', self.x_sinergis_helpdesk_ticket_project.id))
                        if self.x_sinergis_helpdesk_ticket_tache:
                            domain.append(('id', '=', self.x_sinergis_helpdesk_ticket_tache.id))
            else :
                if self.partner_id:
                    domain.append(('name','ilike','HEURES'))
                    domain.append(('partner_id', '=', self.partner_id.id))
                    if self.x_sinergis_helpdesk_ticket_tache2:
                            domain.append(('id', '=', self.x_sinergis_helpdesk_ticket_tache2.id))

            self.x_sinergis_helpdesk_ticket_taches = self.env["project.task"].search(domain)

    def set_task_information(self):
        if self.x_sinergis_helpdesk_ticket_tache :
            tache = self.x_sinergis_helpdesk_ticket_tache
        elif self.x_sinergis_helpdesk_ticket_tache2 :
            tache = self.x_sinergis_helpdesk_ticket_tache2
        else :
            return

        #DETERMINER SI LE CONTRAT D'HEURES EST PERIME OU NON
        perime = False
        if "CONTRAT D'HEURES" in tache.name:
            if datetime.now().year - tache.create_date.year == 2:
                if datetime.now().month == tache.create_date.month:
                    if datetime.now().day >= tache.create_date.day:
                        perime = True
                elif datetime.now().month > tache.create_date.month:
                    perime = True
            elif datetime.now().year - tache.create_date.year > 2:
                perime = True
        if perime :
            self.x_sinergis_helpdesk_ticket_tache_information = "Attention ! Le contrat d'heures est périmé !"
            return

        if tache.effective_hours>=tache.planned_hours:
            self.x_sinergis_helpdesk_ticket_tache_information = "Attention ! Le contrat est terminé, merci de consulter un commercial."
        elif tache.effective_hours>=0.9*tache.planned_hours:
            hours = int(tache.remaining_hours)
            minutes = int((tache.remaining_hours - hours)*60)
            self.x_sinergis_helpdesk_ticket_tache_information = "Attention ! Il reste uniquement " + str(hours) + " heures et " + str(minutes) + " minutes sur le contrat"
        else : self.x_sinergis_helpdesk_ticket_tache_information = False

    #BOUTONS

    def x_sinergis_send_intervention_report_mail(self):
        if not self.x_sinergis_helpdesk_ticket_contact:
            raise ValidationError("Il vous faut un contact pour envoyer le rapport d'intervention.")
        if not self.x_sinergis_helpdesk_ticket_facturation:
            raise ValidationError("Il vous faut sélectionner un type de facturation pour générer un rapport d'intervention")
        if not self.partner_id:
            raise ValidationError("Il vous faut sélectionner une société pour générer un rapport d'intervention")
        template_id = self.env['ir.model.data']._xmlid_to_res_id('sinergis.sinergis_mail_helpdesk_ticket_rapport_intervention', raise_if_not_found=False)
        # The mail is sent with datetime corresponding to the sending user TZ
        composition_mode = self.env.context.get('composition_mode', 'comment')
        compose_ctx = dict(
            default_composition_mode=composition_mode,
            default_model='helpdesk.ticket',
            default_res_ids=self.ids,
            default_use_template=bool(template_id),
            default_template_id=template_id,
            mail_tz=self.env.user.tz,
        )
        return {
            'type': 'ir.actions.act_window',
            'name': "Rapport d'intervention",
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': compose_ctx,
        }

    def x_sinergis_intervention_planned(self):
        body = f"Une intervention est à planifier."
        self.message_post(body=body)
        self.x_sinergis_helpdesk_ticket_planned_intervention_user_id = self.env.user
        self.x_sinergis_helpdesk_ticket_planned_intervention = True

    def x_sinergis_intervention_unplanned(self):
        body = f"L'intervention n'est plus à planifier."
        self.message_post(body=body)
        self.x_sinergis_helpdesk_ticket_planned_intervention = False

    def x_sinergis_helpdesk_ticket_show_facturation_button (self):
        #if not self.x_sinergis_helpdesk_ticket_contact:
        #    raise ValidationError('Veuillez renseigner le Contact et la Description du ticket pour afficher cette partie.')
        self.x_sinergis_helpdesk_ticket_show_facturation = not self.x_sinergis_helpdesk_ticket_show_facturation

    def x_sinergis_helpdesk_ticket_duree_button(self):
        if self.x_sinergis_helpdesk_ticket_temps_passe <= 0 and self.x_sinergis_helpdesk_ticket_is_facturee == False:
            raise ValidationError("Le temps passé doit être supérieur à 0.")
        if not self.user_id:
            raise ValidationError("Vous devez assigner une personne pour décompter des heures.")
        if self.x_sinergis_helpdesk_ticket_taches :
            self.x_sinergis_helpdesk_ticket_billing_last_date = datetime.now() # Mise à jour de la date de modification de la facturation
            self.x_sinergis_helpdesk_ticket_is_facturee = True
            name = self.name
            self.x_sinergis_helpdesk_ticket_taches.timesheet_ids = [(0,0,{'name' : name, 'x_sinergis_account_analytic_line_user_id' : self.user_id.id,'unit_amount' : self.x_sinergis_helpdesk_ticket_temps_passe,'x_sinergis_account_analytic_line_ticket_id' : self.id, 'x_sinergis_account_analytic_line_start_time': self.x_sinergis_helpdesk_ticket_start_time ,'x_sinergis_account_analytic_line_end_time': self.x_sinergis_helpdesk_ticket_end_time})]
            # Creation d'un evenement dans le calendrier si l'utilisateur l'autorise
            if self.user_id.x_sinergis_res_users_tickets_in_calendar:
                start = self.x_sinergis_helpdesk_ticket_start_time
                stop = self.x_sinergis_helpdesk_ticket_end_time
                partner_id = self.partner_id
                contact_id = self.x_sinergis_helpdesk_ticket_contact
                if start and stop and stop > start:
                    if partner_id:
                        event_name = f"ASSISTANCE - {partner_id.name}"
                    else:
                        event_name = "ASSISTANCE"
                    context = {
                        "name" : event_name,
                        "user_id" : self.user_id.id,
                        "start" : start,
                        "stop" : stop,
                        "x_sinergis_calendar_event_client": partner_id.id,
                        "x_sinergis_calendar_event_contact" : contact_id.id,
                        "x_sinergis_calendar_event_helpdesk_ticket_id" : self.id,
                        'need_sync_m': True
                    }
                    self.env["calendar.event"].create(context)
                # Mise à jour des informations de la tâche
                HelpdeskTicket.set_task_information(self)

    def x_sinergis_helpdesk_ticket_reset_button (self):
        if self.x_sinergis_helpdesk_ticket_is_facturee:
            self.env["account.analytic.line"].search([('x_sinergis_account_analytic_line_ticket_id', '=', self.id)]).unlink()
            # Retirer les évènements du calendrier correspondants à ce ticket
            self.env['calendar.event'].search([("x_sinergis_calendar_event_helpdesk_ticket_id","=",self.id)]).unlink()
            # Marquer le ticket comme non facturé
            self.x_sinergis_helpdesk_ticket_is_facturee = not self.x_sinergis_helpdesk_ticket_is_facturee
            # Mise à jour de la date de modification de la facturation
            self.x_sinergis_helpdesk_ticket_billing_last_date = datetime.now()

    def x_sinergis_helpdesk_ticket_start_time_button (self):
        self.x_sinergis_helpdesk_ticket_start_time = datetime.now()
        self._update_temps_passe()

    def x_sinergis_helpdesk_ticket_stop_time_button (self):
        self.x_sinergis_helpdesk_ticket_end_time = datetime.now()
        self._update_temps_passe()

    def x_sinergis_helpdesk_ticket_last_call_button (self):
        self.x_sinergis_helpdesk_last_call_user_id = self.env.user
        self.x_sinergis_helpdesk_last_call = datetime.now()
        body = f"Le client n'a pas répondu le {datetime.now(pytz.timezone('America/Guadeloupe')).strftime('%Y/%m/%d à %H:%M:%S')} (horaire de Guadeloupe)."
        self.message_post(body=body)
        # Création d'un rappel pour le consultant
        self.activity_schedule('mail.mail_activity_data_call',summary='Rappeler le client',note="Rappeler le client car il n'a pas répondu",date_deadline=datetime.today()+timedelta(minutes=30),user_id=self.env.user.id)
        # Envoie du mail au client
        

        if self.x_sinergis_helpdesk_ticket_sous_produits_new :
            product = f"{self.x_sinergis_helpdesk_ticket_produits_new.name} - {self.x_sinergis_helpdesk_ticket_sous_produits_new.name}"
        else:
            product = self.x_sinergis_helpdesk_ticket_produits_new.name

        ctx={
            "title" : self.x_sinergis_helpdesk_ticket_contact.title.name,
            "last_name" : self.x_sinergis_helpdesk_ticket_contact.x_sinergis_societe_contact_lastname,
            "time": datetime.now(pytz.timezone('America/Guadeloupe')).strftime('%H:%M'),
            "company" : self.x_sinergis_helpdesk_ticket_partner_company_id.name,
            "ticket" : self.id,
            "product" : product
        }
        template_id = self.env.ref('sinergis.sinergis_mail_helpdesk_ticket_last_call_button').id
        self.env["mail.template"].browse(template_id).with_context(ctx).send_mail(self.id, force_send=True)
        

    def x_sinergis_helpdesk_ticket_partner_replied (self):
        self.x_sinergis_helpdesk_last_call = False
        body = f"Le client a répondu le {datetime.now(pytz.timezone('America/Guadeloupe')).strftime('%Y/%m/%d à %H:%M:%S')} (horaire de Guadeloupe)."
        self.message_post(body=body)

    def x_sinergis_helpdesk_ticket_partner_reminder (self):
        self.sort_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        body = f"Il y a eu une relance du client le {datetime.now(pytz.timezone('America/Guadeloupe')).strftime('%Y/%m/%d à %H:%M:%S')} (horaire de Guadeloupe)."
        self.message_post(body=body)

        ctx={
            "title" : self.x_sinergis_helpdesk_ticket_contact.title.name,
            "last_name" : self.x_sinergis_helpdesk_ticket_contact.x_sinergis_societe_contact_lastname,
            "ticket" : f"#{self.id}",
        }

        template_id = self.env.ref('sinergis.sinergis_mail_helpdesk_ticket_partner_reminder_button').id
        self.env["mail.template"].browse(template_id).with_context(ctx).send_mail(self.id, force_send=True)
        
    # Bouton dans la tree view qui informe que le client n'a pas répondu.
    def x_sinergis_helpdesk_ticket_tree_last_call_button (self):
        return

    def button_x_sinergis_helpdesk_ticket_client_answer (self):
        raise ValidationError("Le client a envoyé au moins deux mails concernant ce ticket.")

    #L'objectif est d'empecher les gens non assignés de changer le ticket une fois celui-ci terminé
    def write(self, values):
        user_id = self.user_id
        if not self.env.user.has_group('sinergis.group_helpdesk_admin'): #Si l'utilisateur n'est pas dans le groupe des administrateurs de tickets
            if user_id != self.env.user and self.stage_id.name == "Résolu":
                raise ValidationError("Vous ne pouvez pas modifier un ticket cloturé qui ne vous est pas assigné.")
            if self.x_sinergis_helpdesk_ticket_client_bloque :
                raise ValidationError("Vous ne pouvez pas modifier le ticket d'un client bloqué. Merci de contacter un commercial ou un administrateur des tickets.")
        
        # Vérification si on doit modifier la date de dernière facturation
        if "x_sinergis_helpdesk_ticket_facturation" in values or "x_sinergis_helpdesk_ticket_temps_passe" in values:
            self.x_sinergis_helpdesk_ticket_billing_last_date = datetime.now()
        
        # Mise à jour des abonnés au ticket
        if "partner_id" in values or "x_sinergis_helpdesk_ticket_contact" in values:
            contact_id = values.get("x_sinergis_helpdesk_ticket_contact", self.x_sinergis_helpdesk_ticket_contact)
            self.message_unsubscribe(partner_ids=[partner.id for partner in self.message_partner_ids])
            if contact_id:
                self.message_subscribe(partner_ids=[contact_id])

        # Envoyer un mail au consultant lorsqu'il est assigné au ticket
        if "user_id" in values :
            if values["user_id"] != False:
                user_id = self.env['res.users'].search([('id','=',values["user_id"])])
                if user_id != self.env.user:  # Envoyer uniquement si ce n'est pas l'utilisateur connecté qui s'assigne le ticket
                    partner_id = values.get("partner_id", self.partner_id)
                    name = values.get("name", self.name) + f"#{self.id}"
                    ctx = {
                        'email': user_id.login,
                        'name': user_id.name,
                        'ticket_name': name,
                        'partner_name': partner_id.name,
                    }
                    template_id = self.env.ref('sinergis.sinergis_mail_helpdesk_ticket_consultant_assignated').id
                    self.env["mail.template"].browse(template_id).with_context(ctx).send_mail(self.id, force_send=True)

        # Enregistrer l'intervention dans le calendrier si ce n'est pas décompté sur tâche et que l'utilisateur l'autorise
        if self.user_id.x_sinergis_res_users_tickets_in_calendar:
            facturation = values.get("x_sinergis_helpdesk_ticket_facturation", self.x_sinergis_helpdesk_ticket_facturation)
            if facturation:
                if facturation != "Contrat heures" and facturation != "Devis":
                    event = self.env['calendar.event'].search([("x_sinergis_calendar_event_helpdesk_ticket_id","=",self.id)], limit=1)
                    #Chargement des paramètres start et stop
                    start = values.get("x_sinergis_helpdesk_ticket_start_time", self.x_sinergis_helpdesk_ticket_start_time)
                    stop = values.get("x_sinergis_helpdesk_ticket_end_time", self.x_sinergis_helpdesk_ticket_end_time)
                    if type(start) == str:
                        start = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
                    if type(stop) == str:
                        stop = datetime.strptime(stop, '%Y-%m-%d %H:%M:%S')
                    partner_id = self.env['res.partner'].search([('id','=',values.get("partner_id", self.partner_id.id))])
                    contact_id = self.env['res.partner'].search([('id','=',values.get("x_sinergis_helpdesk_ticket_contact", self.x_sinergis_helpdesk_ticket_contact.id))])
                    if start and stop and stop > start:
                        context = {
                            "name" : f"ASSISTANCE - {partner_id.name}",
                            "user_id" : self.user_id.id,
                            "start" : start,
                            "stop" : stop,
                            "x_sinergis_calendar_event_client": partner_id.id,
                            "x_sinergis_calendar_event_contact" : contact_id.id,
                            "x_sinergis_calendar_event_is_sent" : self.x_sinergis_helpdesk_ticket_is_sent,
                            "x_sinergis_calendar_event_sent_date" : self.x_sinergis_helpdesk_ticket_sent_date,
                            "x_sinergis_calendar_event_sent_mail" : self.x_sinergis_helpdesk_ticket_sent_mail,
                            "x_sinergis_calendar_event_helpdesk_ticket_id" : self.id,
                            'need_sync_m': True
                        }
                        if not event :
                            event = self.env["calendar.event"].create(context)
                        else :
                            event.write(context)
                        # Permet de mettre l'activité uniquement dans le calndrier de la personne en charge du ticket
                        event.partner_ids = [(5,)]
                        event.partner_ids = [(4,self.user_id.partner_id.id)]

        return super(HelpdeskTicket, self).write(values)

    #Lors de la création de ticket via mail, ajouter automatiquement le contact et la société attribuée
    @api.model_create_multi
    def create(self, list_value):
        for vals in list_value:
            if self.env['res.partner'].search([('id','=',vals["partner_id"])]).is_company == False:
                vals["x_sinergis_helpdesk_ticket_contact"] = vals["partner_id"]
                vals["partner_id"] = self.env['res.partner'].search([('id','=',vals["partner_id"])]).parent_id.id
            # ANCIENNE FONCTIONALITE
            #if not "team_id" in vals or vals["team_id"] == False :
                #raise ValidationError("Veuillez sélectionner toutes les sociétés Sinergis (en haut à droite) afin de créer un ticket.")

        tickets = super(HelpdeskTicket, self).create(list_value)
        for ticket in tickets :
            ticket.message_unsubscribe(partner_ids=[ticket.partner_id.id])
            ticket.message_subscribe(partner_ids=ticket.x_sinergis_helpdesk_ticket_contact.ids)
            # Envoyer un mail au consultant en charge du ticket pour l'informer de l'assignation.
            if ticket.user_id:
                user_id = self.env['res.users'].search([('id','=',ticket.user_id.id)])
                if user_id != self.env.user:  # Envoyer uniquement si ce n'est pas l'utilisateur connecté qui s'assigne le ticket
                    partner_id = ticket.partner_id
                    name = ticket.name + f" #{ticket.id}"
                    ctx = {
                        'email': user_id.login,
                        'name': user_id.name,
                        'ticket_name': name,
                        'partner_name': partner_id.name,
                    }
                    template_id = self.env.ref('sinergis.sinergis_mail_helpdesk_ticket_consultant_assignated').id
                    self.env["mail.template"].browse(template_id).with_context(ctx).send_mail(ticket.id, force_send=True)


        return tickets
    
    # Ne pas permettre la suppression d'un ticket si l'utilisateur n'est pas un administrateur des tickets
    def unlink(self):
        if not self.env.user.has_group('sinergis.group_helpdesk_admin'):
            raise ValidationError("Vous n'avez pas le droit de suppression d'un ticket. Veuillez vous rapprocher d'un administrateur des tickets.")
        else :
            super(HelpdeskTicket, self).unlink()
        return
