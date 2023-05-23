from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
from datetime import datetime
import re


class CalendarEvent(models.Model):
    _inherit = "calendar.event"

    #Provenance de l'evenement
    x_sinergis_calendar_event_is_commercial_appointment = fields.Boolean()
    x_sinergis_calendar_event_is_technical_appointment = fields.Boolean()

    x_sinergis_calendar_event_client = fields.Many2one("res.partner",string="Client")
    x_sinergis_calendar_event_client_name = fields.Char(related="x_sinergis_calendar_event_client.name")
    x_sinergis_calendar_event_contact = fields.Many2one("res.partner",string="Contact")
    x_sinergis_calendar_event_contact_transfered = fields.Many2one("res.partner",string="") #Utilisé lors du transfert de client et contact depuis la planification de l'assistance. Permet de ne pas rentrer en conflit avec le onchange du client qui supprime le contact au demarrage
    x_sinergis_calendar_event_contact_note = fields.Text(compute="_compute_x_sinergis_calendar_event_contact_note")
    

#ZONE PRODUITS
    #Ancien système de produits
    x_sinergis_calendar_event_produits = fields.Selection([('CEGID', 'CEGID'), ('E2TIME', 'E2TIME'), ('MESBANQUES', 'MESBANQUES'), ('OPEN BEE', 'OPEN BEE'), ('QUARKSUP', 'QUARKSUP'), ('SAGE 100', 'SAGE 100'), ('SAGE 1000', 'SAGE 1000'), ('SAP', 'SAP'), ('VIF', 'VIF'), ('X3', 'SAGE X3'), ('XLSOFT', 'XLSOFT'), ('XRT', 'XRT'), ('SILAE','SILAE'), ('DIVERS', 'DIVERS')], string="Produits")
    #Nouveau système de produits
    x_sinergis_calendar_event_produits_new = fields.Many2one("sale.products",string="Produit")
    x_sinergis_calendar_event_sous_produits_new = fields.Many2one("sale.products.subproducts",string="Sous-produit")

    x_sinergis_calendar_event_produits_cegid = fields.Selection([('LIASSE', 'LIASSE')], string="Module CEGID")
    x_sinergis_calendar_event_produits_sage100 = fields.Selection([('CPT', 'CPT'),('GES', 'GES'),('IMM', 'IMM'),('MDP', 'MDP'),('TRE', 'TRE'),('SCD', 'SCD'),('BI', 'BI'),('ECF', 'ECF'),('PAI', 'PAI'),('SEE', 'SEE'),('BATIGEST', 'BATIGEST'),('DEV', 'DEV'),('SRC', 'SRC'),('CRM', 'CRM')], string="Module Sage 100")
    x_sinergis_calendar_event_produits_sage1000 = fields.Selection([('CPT', 'CPT'),('IMM', 'IMM'),('TRE', 'TRE'),('BP', 'BP'),('RAPPRO', 'RAPPRO'),('ENGA', 'ENGA'),('SCB', 'SCB'),('BI', 'BI'),('DEV', 'DEV')], string="Module Sage 1000")
    x_sinergis_calendar_event_produits_sap = fields.Selection([('CPT', 'CPT'),('GES', 'GES'),('DEV', 'DEV')], string="Module SAP")
    x_sinergis_calendar_event_produits_x3 = fields.Selection([('CPT', 'CPT'),('GES', 'GES'),('CRYSTAL', 'CRYSTAL'),('BI', 'BI'),('DEV', 'DEV'),('HRM', 'HRM')], string="Module Sage X3")
    x_sinergis_calendar_event_produits_divers = fields.Selection([('ODOO', 'ODOO'),('SCANFACT', 'SCANFACT'),('WINDEV', 'WINDEV'),('AUTRE', 'AUTRE')], string="Module Divers")

    x_sinergis_calendar_event_produit_nom_complet = fields.Char(string="Produit", readonly=True, compute="_compute_x_sinergis_calendar_event_produit_nom_complet")

    x_sinergis_calendar_event_type_client = fields.Selection([('PME', 'PME'),('MGE', 'MGE')], string="Type de client")

    #PAGE FACTURATION
    x_sinergis_calendar_event_object = fields.Char(string="Objet")

    x_sinergis_calendar_event_start_time = fields.Datetime(string="Début et fin de l'intervention")
    x_sinergis_calendar_event_end_time = fields.Datetime(string='')

    x_sinergis_calendar_event_desc_intervention = fields.Html(string="Description d'intervention")
    x_sinergis_calendar_event_trip = fields.Boolean(string="Déplacement")
    x_sinergis_calendar_event_trip_movementcountry = fields.Many2one("sinergis.movementcountry", string="Pays de déplacement")
    x_sinergis_calendar_event_trip_movementarea = fields.Many2one("sinergis.movementarea", string="Zone du pays")

    x_sinergis_calendar_event_facturation = fields.Selection([("À définir ultérieurement", "À définir ultérieurement"),("Contrat heure", "Contrat d'heures"),("Temps passé", "Temps passé"),("Devis", "Devis"),('Non facturable interne', 'Non facturable interne'),("Non facturable", "Non facturable"),("Avant-vente", "Avant-vente")], string="Facturation")
    x_sinergis_calendar_event_project = fields.Many2one("project.project", string="Projet")
    x_sinergis_calendar_event_project_transfered = fields.Many2one("project.project",string="") #Utilisé lors du transfert de client et contact depuis la planification de l'assistance. Permet de ne pas rentrer en conflit avec le onchange du client qui supprime le contact au demarrage

    x_sinergis_calendar_event_tache = fields.Many2one("project.task", string="Tâche")
    x_sinergis_calendar_event_tache_transfered = fields.Many2one("project.task",string="") #Utilisé lors du transfert de client et contact depuis la planification de l'assistance. Permet de ne pas rentrer en conflit avec le onchange du client qui supprime le contact au demarrage

    x_sinergis_calendar_event_tache2 = fields.Many2one("project.task", string="Contrat d'heures")
    x_sinergis_calendar_event_tache_information = fields.Char(string="")


    x_sinergis_calendar_event_taches = fields.One2many('project.task',compute="_compute_tasks",readonly=True)

    x_sinergis_calendar_duree_facturee = fields.Float(string="Temps passé")

    x_sinergis_calendar_event_is_solved = fields.Boolean(string="L'intervention est-elle terminée ?'",default=False)

    x_sinergis_calendar_event_intervention_count = fields.Integer(string="Nombre d'interventions", compute="_compute_x_sinergis_calendar_event_intervention_count")
    x_sinergis_calendar_event_temps_cumule = fields.Float(string="Temps cumulé", compute="_compute_x_sinergis_calendar_event_temps_cumule", group_operator='sum')

    # Prise en compte uniquement de la facturation CH ou devis
    x_sinergis_calendar_event_is_facturee = fields.Boolean(string="",default=False)
    # Prise en compte de chaque type de facturation.
    # Pour valider cette facturation : Soit on décompte, soit on renseigne un type de facturation sans décomptage et on regarde si il y a du temps passé présent
    x_sinergis_calendar_event_is_facturee_total = fields.Boolean(string="",compute="_compute_x_sinergis_calendar_event_is_facturee_total")

    #Pour la vue list
    x_sinergis_calendar_event_is_downloaded = fields.Boolean(string="Téléchargé",default=False,readonly=True)
    x_sinergis_calendar_event_is_sent = fields.Boolean(string="Envoyé",default=False,readonly=True)
    x_sinergis_calendar_event_is_deducted = fields.Boolean(string="Décompté",compute="_compute_x_sinergis_calendar_event_is_deducted")

    # Rapport d'intervention validé :
    #Ancien système < 11/02/23
    x_sinergis_calendar_event_rapport_intervention_valide = fields.Binary(string="Rapport d'intervention validé")
    #Nouveau système > 11/02/23
    #Champ qui détecte si un rapport est dans l'évènement. Est utilisé en JS pour l'affichage en mode calendrier.
    x_sinergis_calendar_event_intervention_report_done_exists = fields.Boolean(string="",compute="_compute_x_sinergis_calendar_event_intervention_report_done_exists", store="True")
    x_sinergis_calendar_event_intervention_report_done = fields.One2many('calendar.sinergis_intervention_report_done', 'event_id', string="Rapports d'intervention validés")

    # 5 Avril : Ajout d'un lien vers le ticket si l'évènement provient de l'assistance
    x_sinergis_calendar_event_helpdesk_ticket_id = fields.Many2one("helpdesk.ticket")

    @api.depends('x_sinergis_calendar_event_taches')
    def _compute_tasks (self):
        CalendarEvent.updateTasks(self)

    @api.depends('x_sinergis_calendar_event_intervention_count')
    def _compute_x_sinergis_calendar_event_intervention_count (self):
        for rec in self:
            rec.x_sinergis_calendar_event_intervention_count = self.env['account.analytic.line'].search_count([('x_sinergis_account_analytic_line_event_id', '=', rec.id)])

    @api.depends('x_sinergis_calendar_event_temps_cumule')
    def _compute_x_sinergis_calendar_event_temps_cumule (self):
        for rec in self:
            if rec.x_sinergis_calendar_event_facturation == "Contrat heure" or rec.x_sinergis_calendar_event_facturation == "Devis":
                rec.x_sinergis_calendar_event_temps_cumule = sum(rec.env['account.analytic.line'].search([('x_sinergis_account_analytic_line_event_id', '=', rec.id)]).mapped('unit_amount'))
            else :
                rec.x_sinergis_calendar_event_temps_cumule = rec.x_sinergis_calendar_duree_facturee

    @api.depends('x_sinergis_calendar_event_is_deducted')
    def _compute_x_sinergis_calendar_event_is_deducted (self):
        for rec in self:
            state = False
            if rec.x_sinergis_calendar_event_facturation and rec.x_sinergis_calendar_event_temps_cumule > 0:
                state = True
            rec.x_sinergis_calendar_event_is_deducted = state

    @api.depends('x_sinergis_calendar_event_intervention_report_done_exists')
    def _compute_x_sinergis_calendar_event_intervention_report_done_exists (self):
        for rec in self:
            if len(rec.x_sinergis_calendar_event_intervention_report_done) > 0 :
                rec.x_sinergis_calendar_event_intervention_report_done_exists = True
            else :
                rec.x_sinergis_calendar_event_intervention_report_done_exists = False

    @api.depends('x_sinergis_calendar_event_is_facturee_total')
    def _compute_x_sinergis_calendar_event_is_facturee_total (self):
        for rec in self:
            state = False
            #Si décomptage sur CH ou devis
            if rec.x_sinergis_calendar_event_is_facturee:
                state = True
            elif rec.x_sinergis_calendar_event_facturation:
                if rec.x_sinergis_calendar_event_facturation != "Contrat heure" and rec.x_sinergis_calendar_event_facturation != "Devis" and rec.x_sinergis_calendar_event_facturation != "À définir ultérieurement":
                    if rec.x_sinergis_calendar_duree_facturee:
                        state = True
            rec.x_sinergis_calendar_event_is_facturee_total = state

    @api.depends("x_sinergis_calendar_event_contact_note")
    def _compute_x_sinergis_calendar_event_contact_note(self):
        text = re.compile('<.*?>')
        for ticket in self :
            comment = re.sub(text, '', ticket.x_sinergis_calendar_event_contact.comment)
            if len(comment) <= 2 :
                ticket.x_sinergis_calendar_event_contact_note = False
            else :
                ticket.x_sinergis_calendar_event_contact_note = comment

    @api.depends('x_sinergis_calendar_event_produit_nom_complet')
    def _compute_x_sinergis_calendar_event_produit_nom_complet (self):
        for rec in self:
            if rec.x_sinergis_calendar_event_produits_new and rec.x_sinergis_calendar_event_sous_produits_new:
                rec.x_sinergis_calendar_event_produit_nom_complet = rec.x_sinergis_calendar_event_produits_new.name + " " + rec.x_sinergis_calendar_event_sous_produits_new.name
            elif rec.x_sinergis_calendar_event_produits_new:
                rec.x_sinergis_calendar_event_produit_nom_complet = rec.x_sinergis_calendar_event_produits_new.name
            else: 
                rec.x_sinergis_calendar_event_produit_nom_complet = ""



    def updateTasks (self):
        for event in self:
            domain = []
            if self.x_sinergis_calendar_event_facturation != "Contrat heure":
                if self.x_sinergis_calendar_event_client:
                    domain.append(('name','not ilike','HEURES'))
                    domain.append(('partner_id', '=', self.x_sinergis_calendar_event_client.id))
                    if self.x_sinergis_calendar_event_project:
                        domain.append(('project_id', '=', self.x_sinergis_calendar_event_project.id))
                        if self.x_sinergis_calendar_event_tache:
                            domain.append(('id', '=', self.x_sinergis_calendar_event_tache.id))
            else :
                if self.x_sinergis_calendar_event_client:
                    domain.append(('name','ilike','HEURES'))
                    domain.append(('partner_id', '=', self.x_sinergis_calendar_event_client.id))
                    if self.x_sinergis_calendar_event_tache2:
                            domain.append(('id', '=', self.x_sinergis_calendar_event_tache2.id))
            self.x_sinergis_calendar_event_taches = self.env["project.task"].search(domain)

    @api.onchange("x_sinergis_calendar_event_is_commercial_appointment")
    def on_change_x_sinergis_calendar_event_is_commercial_appointment(self):
        is_commercial = False
        for line in self.activity_ids:
            if line.activity_type_id.name == "RDV Commercial":
                is_commercial = True
        self.x_sinergis_calendar_event_is_commercial_appointment = is_commercial
        is_technical = False
        for line in self.activity_ids:
            if line.activity_type_id.name == "RDV Intervention":
                is_technical = True
        self.x_sinergis_calendar_event_is_technical_appointment = is_technical


    @api.onchange("x_sinergis_calendar_event_client")
    def on_change_x_sinergis_calendar_event_client(self):
        if self.x_sinergis_calendar_event_client.x_sinergis_societe_litige_bloque and not self.x_sinergis_calendar_event_is_commercial_appointment:
            raise ValidationError("Le client est bloqué pour la raison suivante : "+ self.x_sinergis_calendar_event_client.x_sinergis_societe_litige_bloque_remarques +". Vous ne pouvez pas intervenir, merci de vous rapprocher d'un commercial.")
            self.x_sinergis_calendar_event_client = False
        if self.x_sinergis_calendar_event_contact_transfered :
            self.x_sinergis_calendar_event_contact = self.x_sinergis_calendar_event_contact_transfered
            self.x_sinergis_calendar_event_contact_transfered = False
        else :
            self.x_sinergis_calendar_event_contact = False
            self.x_sinergis_calendar_event_project = False
            self.x_sinergis_calendar_event_tache = False
            self.x_sinergis_calendar_event_tache2 = False
            self.x_sinergis_calendar_event_tache_information = False
        CalendarEvent.updateTasks(self)

    @api.onchange("duration")
    def on_change_duration(self):
        self.x_sinergis_calendar_duree_facturee = self.duration
        if self.x_sinergis_calendar_event_start_time == False and self.x_sinergis_calendar_event_end_time == False :
            self.x_sinergis_calendar_event_start_time = self.start
            self.x_sinergis_calendar_event_end_time = self.stop

    @api.onchange("x_sinergis_calendar_event_produits_new")
    def on_change_x_sinergis_calendar_event_produits_new(self):
        self.x_sinergis_calendar_event_sous_produits_new = False
        CalendarEvent.update_type_client(self)

    @api.onchange("x_sinergis_calendar_event_sous_produits_new")
    def on_change_x_sinergis_calendar_event_sous_produits_new(self):
        CalendarEvent.update_type_client(self)

    def update_type_client (self):
        if self.x_sinergis_calendar_event_produits_new:
            value = self.x_sinergis_calendar_event_produits_new.name
            if value == "CEGID":
                self.x_sinergis_calendar_event_type_client = "MGE"
            elif value == "E2TIME":
                self.x_sinergis_calendar_event_type_client = "PME"
            elif value == "MESBANQUES":
                self.x_sinergis_calendar_event_type_client = "PME"
            elif value == "OPEN BEE":
                self.x_sinergis_calendar_event_type_client = "PME"
            elif value == "QUARKSUP":
                self.x_sinergis_calendar_event_type_client = "MGE"
            elif value == "SAGE 100":
                self.x_sinergis_calendar_event_type_client = "PME"
            elif value == "SAGE 1000":
                self.x_sinergis_calendar_event_type_client = "MGE"
            elif value == "SAP":
                self.x_sinergis_calendar_event_type_client = "MGE"
            elif value == "VIF":
                self.x_sinergis_calendar_event_type_client = "MGE"
            elif value == "SAGE X3":
                self.x_sinergis_calendar_event_type_client = "MGE"
            elif value == "XLSOFT":
                self.x_sinergis_calendar_event_type_client = "MGE"
            elif value == "XRT":
                self.x_sinergis_calendar_event_type_client = "MGE"
            elif value == "DIVERS":
                if self.x_sinergis_calendar_event_sous_produits_new:
                    subvalue = self.x_sinergis_calendar_event_sous_produits_new.name
                    if subvalue == "SCANFACT":
                        self.x_sinergis_calendar_event_type_client = "PME"
                    elif subvalue == "WINDEV":
                        self.x_sinergis_calendar_event_type_client = "PME"
                    elif subvalue == "AUTRE":
                        self.x_sinergis_calendar_event_type_client = "PME"

    @api.onchange("x_sinergis_calendar_event_facturation")
    def on_change_x_sinergis_calendar_event_facturation(self):
        if self.x_sinergis_calendar_event_project_transfered :
            if self.x_sinergis_calendar_event_facturation == "Devis":
                self.x_sinergis_calendar_event_project = self.x_sinergis_calendar_event_project_transfered
            self.x_sinergis_calendar_event_project_transfered = False
        else :
            self.x_sinergis_calendar_event_project = False
            self.x_sinergis_calendar_event_tache = False
            self.x_sinergis_calendar_event_tache2 = False
            self.x_sinergis_calendar_event_tache_information = False
        if self.x_sinergis_calendar_event_start_time == False and self.x_sinergis_calendar_event_end_time == False :
            self.x_sinergis_calendar_event_start_time = self.start
            self.x_sinergis_calendar_event_end_time = self.stop
        CalendarEvent.updateTasks(self)

    @api.onchange("x_sinergis_calendar_event_project")
    def on_change_x_sinergis_calendar_event_project(self):
        if self.x_sinergis_calendar_event_tache_transfered :
            if self.x_sinergis_calendar_event_facturation == "Devis":
                self.x_sinergis_calendar_event_tache = self.x_sinergis_calendar_event_tache_transfered
            elif self.x_sinergis_calendar_event_facturation == "Contrat heure":
                self.x_sinergis_calendar_event_tache2 = self.x_sinergis_calendar_event_tache_transfered
            self.x_sinergis_calendar_event_tache_transfered = False
        else :
            self.x_sinergis_calendar_event_tache = False
            self.x_sinergis_calendar_event_tache = False
            self.x_sinergis_calendar_event_tache2 = False
            self.x_sinergis_calendar_event_tache_information = False
        CalendarEvent.updateTasks(self)

    @api.onchange("x_sinergis_calendar_event_tache")
    def on_change_x_sinergis_calendar_event_tache(self):
        if self.x_sinergis_calendar_event_tache:
            if self.x_sinergis_calendar_event_is_commercial_appointment:
                self.x_sinergis_calendar_event_tache = False
            if not self.x_sinergis_calendar_event_tache.project_id.x_sinergis_project_project_acompte_verse and not self.x_sinergis_calendar_event_is_commercial_appointment:
                raise ValidationError("Vous ne pouvez rien planifier sur cette tâche si l'acompte n'a pas encore été versé. Il faut cocher 'Acompte verse' dans la page du projet.")
        CalendarEvent.updateTasks(self)
        CalendarEvent.set_task_information(self)

    @api.onchange("x_sinergis_calendar_event_tache2")
    def on_change_x_sinergis_calendar_event_tache2(self):
        CalendarEvent.updateTasks(self)
        CalendarEvent.set_task_information(self)

    @api.onchange("name")
    def on_change_name (self):
        if self.x_sinergis_calendar_event_object == self.name or self.x_sinergis_calendar_event_object == False:
            self.x_sinergis_calendar_event_object = self.name
        if self.x_sinergis_calendar_event_desc_intervention == self.name or self.x_sinergis_calendar_event_desc_intervention == False:
            self.x_sinergis_calendar_event_desc_intervention = self.name

    def set_task_information(self):
        if self.x_sinergis_calendar_event_tache :
            tache = self.x_sinergis_calendar_event_tache
        elif self.x_sinergis_calendar_event_tache2 :
            tache = self.x_sinergis_calendar_event_tache2
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
            self.x_sinergis_calendar_event_tache_information = "Attention ! Le contrat d'heures est périmé !"
            return

        if tache.effective_hours>=tache.planned_hours:
            self.x_sinergis_calendar_event_tache_information = "Attention ! Le contrat est terminé, merci de consulter un commercial."
        elif tache.effective_hours>=0.9*tache.planned_hours:
            hours = int(tache.remaining_hours)
            minutes = int((tache.remaining_hours - hours)*60)
            self.x_sinergis_calendar_event_tache_information = "Attention ! Il reste uniquement " + str(hours) + " heures et " + str(minutes) + " minutes sur le contrat"
        else : self.x_sinergis_calendar_event_tache_information = False

    def x_sinergis_calendar_event_duree_button(self):
        if self.x_sinergis_calendar_event_object == False:
            raise ValidationError("Vous devez entrer un objet pour pouvoir décompter des heures.")
        if self.x_sinergis_calendar_duree_facturee <= 0 and self.x_sinergis_calendar_event_is_facturee == False:
            raise ValidationError("Le temps passé doit être supérieur à 0")
        if not self.user_id:
            raise ValidationError("Vous devez assigner une personne pour décompter des heures.")
        if self.x_sinergis_calendar_event_taches :
            self.x_sinergis_calendar_event_is_facturee = True
            self.x_sinergis_calendar_event_taches.timesheet_ids = [(0,0,{'name' : self.x_sinergis_calendar_event_object, 'x_sinergis_account_analytic_line_user_id' : self.user_id.id,'unit_amount' : self.x_sinergis_calendar_duree_facturee,'x_sinergis_account_analytic_line_event_id' : self.id, 'x_sinergis_account_analytic_line_start_time': self.x_sinergis_calendar_event_start_time ,'x_sinergis_account_analytic_line_end_time' : self.x_sinergis_calendar_event_end_time})]
            CalendarEvent.set_task_information(self)

        #OVERRIDE WRITE & CREATE

    """@api.model
    def create(self, values):
        if "x_sinergis_calendar_duree_facturee" in values:
            duree = values["x_sinergis_calendar_duree_facturee"]
        else:
            duree = self.x_sinergis_calendar_duree_facturee

        if "x_sinergis_calendar_event_facturation" in values:
            facturation = values["x_sinergis_calendar_event_facturation"]
        else:
            facturation = self.x_sinergis_calendar_event_facturation

        if "x_sinergis_calendar_event_is_facturee" in values:
            isFacturee = values["x_sinergis_calendar_event_is_facturee"]
        else:
            isFacturee = self.x_sinergis_calendar_event_is_facturee

        if facturation == "Contrat heure" or facturation == "Devis":
            if duree != 0 and not isFacturee:
                raise ValidationError("Vous n'avez pas décompté les heures alors que le nombre d'heures que vous souhaitez facturées est non nul. Veuillez décompter les heures ou les remettre à 0 dans l'onglet facturation.")
        return super(CalendarEvent, self).create(values)

    def write(self, values):
        duree = values.get("x_sinergis_calendar_duree_facturee", self.x_sinergis_calendar_duree_facturee)

        if "x_sinergis_calendar_duree_facturee" in values:
            duree = values["x_sinergis_calendar_duree_facturee"]
        else:
            duree = self.x_sinergis_calendar_duree_facturee

        if "x_sinergis_calendar_event_facturation" in values:
            facturation = values["x_sinergis_calendar_event_facturation"]
        else:
            facturation = self.x_sinergis_calendar_event_facturation

        if "x_sinergis_calendar_event_is_facturee" in values:
            isFacturee = values["x_sinergis_calendar_event_is_facturee"]
        else:
            isFacturee = self.x_sinergis_calendar_event_is_facturee

        if facturation == "Contrat heure" or facturation == "Devis":
            if duree != 0 and not isFacturee:
                raise ValidationError("Vous n'avez pas décompté les heures alors que le nombre d'heures que vous souhaitez facturées est non nul. Veuillez décompter les heures ou les remettre à 0 dans l'onglet facturation.")
        return super(CalendarEvent, self).write(values)
    """

    def write(self, values):
        user_id = self.env.user
        # Pour autoriser la synchronisation Outlook - TODO : Plus étudier la synchro Outlook pour mieux restreindre
        if not "need_sync_m" in values:
            if self.user_id != user_id and self.env.user.has_group('sinergis.group_calendar_admin') == False:
                raise ValidationError("Vous ne pouvez pas modifier un évènement du calendrier qui ne vous appartient pas.")
        return super(CalendarEvent, self).write(values)

    def generer_rapport_intervention(self):
        if self.x_sinergis_calendar_event_object == False:
            raise ValidationError("Vous devez entrer un objet pour pouvoir générer le rapport.")
        if not self.x_sinergis_calendar_event_contact:
            raise UserError("Il vous faut un contact pour envoyer le rapport d'intervention.")
        self.x_sinergis_calendar_event_is_downloaded = True
        return self.env.ref('sinergis.sinergis_intervention_report_calendar').report_action(self)
    
    # Ouvrir le ticket pour les évènements crées à partir de l'assistance
    def action_open_ticket(self):
        return({
            'name': 'Ticket',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'helpdesk.ticket',
            'res_id': self.x_sinergis_calendar_event_helpdesk_ticket_id.id,
            })

    def send_rapport_intervention(self):
        if self.x_sinergis_calendar_event_object == False:
            raise ValidationError("Vous devez entrer un objet pour pouvoir générer le rapport.")
        if not self.x_sinergis_calendar_event_contact:
            raise UserError("Il vous faut un contact pour envoyer le rapport d'intervention.")
        template_id = self.env['ir.model.data']._xmlid_to_res_id('sinergis.sinergis_mail_calendar_rapport_intervention', raise_if_not_found=False)
        composition_mode = self.env.context.get('composition_mode', 'comment')
        self.x_sinergis_calendar_event_is_sent = True
        compose_ctx = dict(
            default_composition_mode=composition_mode,
            default_model='calendar.event',
            default_res_ids=self.ids,
            default_use_template=bool(template_id),
            default_template_id=template_id,
            default_partner_ids=self.partner_ids.ids,
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

    def x_sinergis_calendar_event_reset_button (self):
        if self.x_sinergis_calendar_event_is_facturee:
            self.env["account.analytic.line"].search([('x_sinergis_account_analytic_line_event_id', '=', self.id)]).unlink()
            self.x_sinergis_calendar_event_is_facturee = not self.x_sinergis_calendar_event_is_facturee

    def x_sinergis_calendar_event_start_time_button (self):
        self.x_sinergis_calendar_event_start_time = datetime.now()

    def x_sinergis_calendar_event_stop_time_button (self):
        self.x_sinergis_calendar_event_end_time = datetime.now()
        self.x_sinergis_calendar_duree_facturee = (self.x_sinergis_calendar_event_end_time - self.x_sinergis_calendar_event_start_time).total_seconds() / 3600

    #RPC Functions

    def get_x_sinergis_calendar_event_is_deducted(self, meeting_ids):
        meeting = self.env['calendar.event'].browse(meeting_ids)[0]
        return meeting.x_sinergis_calendar_event_is_deducted
    
    class CalendarSinergisInterventionReportDone(models.Model):
        _name = "calendar.sinergis_intervention_report_done"
        _description = "Rapport d'intervention dans le Calendrier"

        event_id = fields.Many2one("calendar.event",string="Évenement",required=True)
        name = fields.Char(string="Nom",required=True)
        file = fields.Binary(string="Rapport")
