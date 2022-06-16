from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    # --FORM--

    #Override
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company, readonly=True,related='')

    #Colonne de gauche
    x_sinergis_helpdesk_ticket_produits = fields.Selection([('CEGID', 'CEGID'), ('E2TIME', 'E2TIME'), ('MESBANQUES', 'MESBANQUES'), ('OPEN BEE', 'OPEN BEE'), ('QUARKSUP', 'QUARKSUP'), ('SAGE 100', 'SAGE 100'), ('SAGE 1000', 'SAGE 1000'), ('SAP', 'SAP'), ('VIF', 'VIF'), ('X3', 'SAGE X3'), ('XLSOFT', 'XLSOFT'), ('XRT', 'XRT'), ('DIVERS', 'DIVERS')], string="Produits", required=True)

    x_sinergis_helpdesk_ticket_produits_cegid = fields.Selection([('LIASSE', 'LIASSE')], string="Module CEGID")
    x_sinergis_helpdesk_ticket_produits_sage100 = fields.Selection([('CPT', 'CPT'),('GES', 'GES'),('IMM', 'IMM'),('MDP', 'MDP'),('TRE', 'TRE'),('SCD', 'SCD'),('BI', 'BI'),('ECF', 'ECF'),('PAI', 'PAI'),('SEE', 'SEE'),('BATIGEST', 'BATIGEST'),('DEV', 'DEV'),('SRC', 'SRC'),('CRM', 'CRM')], string="Module Sage 100")
    x_sinergis_helpdesk_ticket_produits_sage1000 = fields.Selection([('CPT', 'CPT'),('IMM', 'IMM'),('TRE', 'TRE'),('BP', 'BP'),('RAPPRO', 'RAPPRO'),('ENGA', 'ENGA'),('SCB', 'SCB'),('BI', 'BI'),('DEV', 'DEV')], string="Module Sage 1000")
    x_sinergis_helpdesk_ticket_produits_sap = fields.Selection([('CPT', 'CPT'),('GES', 'GES'),('DEV', 'DEV')], string="Module SAP")
    x_sinergis_helpdesk_ticket_produits_x3 = fields.Selection([('CPT', 'CPT'),('GES', 'GES'),('CRYSTAL', 'CRYSTAL'),('BI', 'BI'),('DEV', 'DEV')], string="Module Sage X3")
    x_sinergis_helpdesk_ticket_produits_divers = fields.Selection([('SCANFACT', 'SCANFACT'),('WINDEV', 'WINDEV'),('AUTRE', 'AUTRE')], string="Module Divers")


    x_sinergis_helpdesk_ticket_type_client = fields.Selection([('PME', 'PME'),('MGE', 'MGE')], string="Type de client")


    fields.Char(string="Type de client")

    x_sinergis_helpdesk_ticket_show_facturation = fields.Boolean(default=0)

    x_sinergis_helpdesk_ticket_ticket_resolution = fields.Html(string="Description de l'intervention")

    x_sinergis_helpdesk_ticket_facturation = fields.Selection([("Contrat heures", "Contrat d'heures"),('Temps passé', 'Temps passé'),('Devis', 'Devis'),('Non facturable', 'Non facturable')], string="Facturation")
    x_sinergis_helpdesk_ticket_project = fields.Many2one("project.project", string="Projet")
    x_sinergis_helpdesk_ticket_tache = fields.Many2one("project.task", string="Tâche")
    x_sinergis_helpdesk_ticket_tache2 = fields.Many2one("project.task", string="Contrat d'heures")
    x_sinergis_helpdesk_ticket_tache_information = fields.Char(string="")

    x_sinergis_helpdesk_ticket_temps_passe = fields.Float(string="Temps passé")

    x_sinergis_helpdesk_ticket_is_solved = fields.Boolean(string="Le ticket est-il résolu ?",default=False)

    x_sinergis_helpdesk_ticket_intervention_count = fields.Integer(string="Nombre d'interventions", compute="_compute_x_sinergis_helpdesk_ticket_intervention_count")

    x_sinergis_helpdesk_ticket_is_facturee = fields.Boolean(string="",default=False)


    #Colonne de droite
    x_sinergis_helpdesk_ticket_contact = fields.Many2one("res.partner",string="Contact")
    x_sinergis_helpdesk_ticket_contact_fixe = fields.Char(string="Fixe contact", readonly=True)
    x_sinergis_helpdesk_ticket_contact_mobile = fields.Char(string="Mobile contact", readonly=True)
    x_sinergis_helpdesk_ticket_contact_mail = fields.Char(string="Mail contact", readonly=True)

    @api.depends('x_sinergis_helpdesk_ticket_intervention_count')
    def _compute_x_sinergis_helpdesk_ticket_intervention_count (self):
        x_sinergis_helpdesk_ticket_intervention_count = self.env['account.analytic.line'].search_count([('x_sinergis_account_analytic_line_ticket_id', '=', self.id)])

    @api.onchange("x_sinergis_helpdesk_ticket_produits")
    def on_change_x_sinergis_helpdesk_ticket_produits(self):
        HelpdeskTicket.update_type_client(self)

    @api.onchange("x_sinergis_helpdesk_ticket_produits_divers")
    def on_change_x_sinergis_helpdesk_ticket_produits_divers(self):
        HelpdeskTicket.update_type_client(self)


    def update_type_client (self):
        value = self.x_sinergis_helpdesk_ticket_produits
        if value == "CEGID":
            self.x_sinergis_helpdesk_ticket_type_client = "MGE"
        elif value == "E2TIME":
            self.x_sinergis_helpdesk_ticket_type_client = "PME"
        elif value == "MESBANQUES":
            self.x_sinergis_helpdesk_ticket_type_client = "PME"
        elif value == "OPEN BEE":
            self.x_sinergis_helpdesk_ticket_type_client = "PME"
        elif value == "QUARKSUP":
            self.x_sinergis_helpdesk_ticket_type_client = "MGE"
        elif value == "SAGE 100":
            self.x_sinergis_helpdesk_ticket_type_client = "PME"
        elif value == "SAGE 1000":
            self.x_sinergis_helpdesk_ticket_type_client = "MGE"
        elif value == "SAP":
            self.x_sinergis_helpdesk_ticket_type_client = "MGE"
        elif value == "VIF":
            self.x_sinergis_helpdesk_ticket_type_client = "MGE"
        elif value == "X3":
            self.x_sinergis_helpdesk_ticket_type_client = "MGE"
        elif value == "XLSOFT":
            self.x_sinergis_helpdesk_ticket_type_client = "MGE"
        elif value == "XRT":
            self.x_sinergis_helpdesk_ticket_type_client = "MGE"
        elif value == "DIVERS":
            subvalue = self.x_sinergis_helpdesk_ticket_produits_divers
            if subvalue == "SCANFACT":
                self.x_sinergis_helpdesk_ticket_type_client = "PME"
            elif subvalue == "WINDEV":
                self.x_sinergis_helpdesk_ticket_type_client = "PME"
            elif subvalue == "AUTRE":
                self.x_sinergis_helpdesk_ticket_type_client = "PME"

    @api.onchange("x_sinergis_helpdesk_ticket_contact")
    def on_change_x_sinergis_helpdesk_ticket_contact(self):
        if self.x_sinergis_helpdesk_ticket_contact:
            self.x_sinergis_helpdesk_ticket_contact_fixe = self.x_sinergis_helpdesk_ticket_contact.phone
            self.x_sinergis_helpdesk_ticket_contact_mobile = self.x_sinergis_helpdesk_ticket_contact.mobile
            self.x_sinergis_helpdesk_ticket_contact_mail = self.x_sinergis_helpdesk_ticket_contact.email


    #Taches
    x_sinergis_helpdesk_ticket_taches = fields.One2many('project.task',compute="_compute_tasks",readonly=True)

    @api.depends('x_sinergis_helpdesk_ticket_taches')
    def _compute_tasks (self):
        HelpdeskTicket.updateTasks(self)


    @api.onchange("partner_id")
    def on_change_partner_id(self):
        self.x_sinergis_helpdesk_ticket_contact = False
        self.x_sinergis_helpdesk_ticket_type_client = False
        self.x_sinergis_helpdesk_ticket_project = False
        self.x_sinergis_helpdesk_ticket_tache = False
        self.x_sinergis_helpdesk_ticket_tache2 = False
        self.x_sinergis_helpdesk_ticket_tache_information = False
        HelpdeskTicket.updateTasks(self)

    @api.onchange("x_sinergis_helpdesk_ticket_facturation")
    def on_change_x_sinergis_helpdesk_ticket_facturation(self):
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
        HelpdeskTicket.setTacheInformation(self)

    @api.onchange("x_sinergis_helpdesk_ticket_tache2")
    def on_change_x_sinergis_helpdesk_ticket_tache2(self):
        HelpdeskTicket.updateTasks(self)
        HelpdeskTicket.setTacheInformation(self)

    @api.onchange("x_sinergis_helpdesk_ticket_is_solved")
    def on_change_x_sinergis_helpdesk_ticket_is_solved(self):
        if self.x_sinergis_helpdesk_ticket_is_solved:
            self.stage_id = self.env['helpdesk.stage'].search([('name','=',"Résolu")])
        #else if self.name != False: #Pour eviter un changement d'état à la création d'un ticket
    #        self.stage_id = self.env['helpdesk.stage'].search([('name','=',"En cours")])

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

    def setTacheInformation(self):
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

    def x_sinergis_helpdesk_ticket_duree_button(self):
        if self.x_sinergis_helpdesk_ticket_temps_passe <= 0 and self.x_sinergis_helpdesk_ticket_is_facturee == False:
            raise ValidationError("Le temps passé doit être supérieur à 0")
        if self.x_sinergis_helpdesk_ticket_taches :
            self.x_sinergis_helpdesk_ticket_is_facturee = True
            name = self.name
            self.x_sinergis_helpdesk_ticket_taches.timesheet_ids = [(0,0,{'name' : name, 'x_sinergis_account_analytic_line_user_id' : self.user_id.id,'unit_amount' : self.x_sinergis_helpdesk_ticket_temps_passe,'x_sinergis_account_analytic_line_ticket_id' : self.id})]
            HelpdeskTicket.setTacheInformation(self)

    #BOUTONS

    def x_sinergis_helpdesk_ticket_show_facturation_button (self):
        self.x_sinergis_helpdesk_ticket_show_facturation = not self.x_sinergis_helpdesk_ticket_show_facturation
