from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    # --FORM--

    #Override
    #company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company, readonly=True,related='')
    team_id = fields.Many2one(default=lambda self: self.env['helpdesk.team'].search([('name','=',"Service Clientèle")]))

    stage_id = fields.Many2one(domain=False)

    x_sinergis_helpdesk_ticket_planned_intervention = fields.Boolean(default=0)
    x_sinergis_helpdesk_ticket_planned_intervention_text = fields.Char(string=" ", compute="_compute_x_sinergis_helpdesk_ticket_planned_intervention_text")

    #Colonne de gauche
    x_sinergis_helpdesk_ticket_produits = fields.Selection([('CEGID', 'CEGID'), ('E2TIME', 'E2TIME'), ('MESBANQUES', 'MESBANQUES'), ('OPEN BEE', 'OPEN BEE'), ('QUARKSUP', 'QUARKSUP'), ('SAGE 100', 'SAGE 100'), ('SAGE 1000', 'SAGE 1000'), ('SAP', 'SAP'), ('VIF', 'VIF'), ('X3', 'SAGE X3'), ('XLSOFT', 'XLSOFT'), ('XRT', 'XRT'), ('DIVERS', 'DIVERS')], string="Produits")

    x_sinergis_helpdesk_ticket_produits_cegid = fields.Selection([('LIASSE', 'LIASSE')], string="Module CEGID")
    x_sinergis_helpdesk_ticket_produits_sage100 = fields.Selection([('CPT', 'CPT'),('GES', 'GES'),('IMM', 'IMM'),('MDP', 'MDP'),('TRE', 'TRE'),('SCD', 'SCD'),('BI', 'BI'),('ECF', 'ECF'),('PAI', 'PAI'),('SEE', 'SEE'),('BATIGEST', 'BATIGEST'),('DEV', 'DEV'),('SRC', 'SRC'),('CRM', 'CRM')], string="Module Sage 100")
    x_sinergis_helpdesk_ticket_produits_sage1000 = fields.Selection([('CPT', 'CPT'),('IMM', 'IMM'),('TRE', 'TRE'),('BP', 'BP'),('RAPPRO', 'RAPPRO'),('ENGA', 'ENGA'),('SCB', 'SCB'),('BI', 'BI'),('DEV', 'DEV')], string="Module Sage 1000")
    x_sinergis_helpdesk_ticket_produits_sap = fields.Selection([('CPT', 'CPT'),('GES', 'GES'),('DEV', 'DEV')], string="Module SAP")
    x_sinergis_helpdesk_ticket_produits_x3 = fields.Selection([('CPT', 'CPT'),('GES', 'GES'),('CRYSTAL', 'CRYSTAL'),('BI', 'BI'),('DEV', 'DEV'),('HRM', 'HRM')], string="Module Sage X3")
    x_sinergis_helpdesk_ticket_produits_divers = fields.Selection([('SCANFACT', 'SCANFACT'),('WINDEV', 'WINDEV'),('AUTRE', 'AUTRE')], string="Module Divers")

    x_sinergis_helpdesk_ticket_produit_nom_complet = fields.Char(string="Produit", readonly=True, compute="_compute_x_sinergis_helpdesk_ticket_produit_nom_complet")

    x_sinergis_helpdesk_ticket_type_client = fields.Selection([('PME', 'PME'),('MGE', 'MGE')], string="Type de client")

    x_sinergis_helpdesk_ticket_show_facturation = fields.Boolean(default=0)

    x_sinergis_helpdesk_ticket_start_time = fields.Datetime(string="Début et fin de l'intervention")
    x_sinergis_helpdesk_ticket_end_time = fields.Datetime(string='')

    x_sinergis_helpdesk_ticket_ticket_resolution = fields.Html(string="Description de l'intervention")

    x_sinergis_helpdesk_ticket_facturation = fields.Selection([("À définir ultérieurement", "À définir ultérieurement"),("Contrat heures", "Contrat d'heures"),('Temps passé', 'Temps passé'),('Devis', 'Devis'),('Non facturable', 'Non facturable')], string="Facturation")
    x_sinergis_helpdesk_ticket_project = fields.Many2one("project.project", string="Projet")
    x_sinergis_helpdesk_ticket_tache = fields.Many2one("project.task", string="Tâche")
    x_sinergis_helpdesk_ticket_tache2 = fields.Many2one("project.task", string="Contrat d'heures")
    x_sinergis_helpdesk_ticket_tache_information = fields.Char(string="")

    x_sinergis_helpdesk_ticket_temps_passe = fields.Float(string="Temps passé")

    x_sinergis_helpdesk_ticket_is_solved = fields.Boolean(string="Le ticket est-il résolu ?",default=False)

    x_sinergis_helpdesk_ticket_intervention_count = fields.Integer(string="Nombre d'interventions", compute="_compute_x_sinergis_helpdesk_ticket_intervention_count", group_operator="sum")
    x_sinergis_helpdesk_ticket_temps_cumule = fields.Float(string="Temps cumulé", compute="_compute_x_sinergis_helpdesk_ticket_temps_cumule")

    x_sinergis_helpdesk_ticket_is_facturee = fields.Boolean(string="",default=False)


    #Colonne de droite
    x_sinergis_helpdesk_ticket_contact = fields.Many2one("res.partner",string="Contact")
    x_sinergis_helpdesk_ticket_contact_fixe = fields.Char(string="Fixe contact", readonly=True)
    x_sinergis_helpdesk_ticket_contact_mobile = fields.Char(string="Mobile contact", readonly=True)
    x_sinergis_helpdesk_ticket_contact_mail = fields.Char(string="Mail contact", readonly=True)

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
            if rec.x_sinergis_helpdesk_ticket_produits == "CEGID":
                rec.x_sinergis_helpdesk_ticket_produit_nom_complet = rec.x_sinergis_helpdesk_ticket_produits + " " + rec.x_sinergis_helpdesk_ticket_produits_cegid if rec.x_sinergis_helpdesk_ticket_produits_cegid else rec.x_sinergis_helpdesk_ticket_produits
            elif rec.x_sinergis_helpdesk_ticket_produits == "SAGE 100":
                rec.x_sinergis_helpdesk_ticket_produit_nom_complet = rec.x_sinergis_helpdesk_ticket_produits + " " + rec.x_sinergis_helpdesk_ticket_produits_sage100 if rec.x_sinergis_helpdesk_ticket_produits_sage100 else rec.x_sinergis_helpdesk_ticket_produits
            elif rec.x_sinergis_helpdesk_ticket_produits == "SAGE 1000":
                rec.x_sinergis_helpdesk_ticket_produit_nom_complet = rec.x_sinergis_helpdesk_ticket_produits + " " + rec.x_sinergis_helpdesk_ticket_produits_sage1000 if rec.x_sinergis_helpdesk_ticket_produits_sage1000 else rec.x_sinergis_helpdesk_ticket_produits
            elif rec.x_sinergis_helpdesk_ticket_produits == "SAP":
                rec.x_sinergis_helpdesk_ticket_produit_nom_complet = rec.x_sinergis_helpdesk_ticket_produits + " " + rec.x_sinergis_helpdesk_ticket_produits_sap if rec.x_sinergis_helpdesk_ticket_produits_sap else rec.x_sinergis_helpdesk_ticket_produits
            elif rec.x_sinergis_helpdesk_ticket_produits == "X3":
                rec.x_sinergis_helpdesk_ticket_produit_nom_complet = rec.x_sinergis_helpdesk_ticket_produits + " " + rec.x_sinergis_helpdesk_ticket_produits_x3 if rec.x_sinergis_helpdesk_ticket_produits_x3 else rec.x_sinergis_helpdesk_ticket_produits
            elif rec.x_sinergis_helpdesk_ticket_produits == "DIVERS":
                rec.x_sinergis_helpdesk_ticket_produit_nom_complet = rec.x_sinergis_helpdesk_ticket_produits_divers if rec.x_sinergis_helpdesk_ticket_produits_divers else ''
            else:
                rec.x_sinergis_helpdesk_ticket_produit_nom_complet = rec.x_sinergis_helpdesk_ticket_produits if rec.x_sinergis_helpdesk_ticket_produits else ''


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


    @api.onchange("user_id")
    def on_change_user_id(self):
        self.x_sinergis_helpdesk_ticket_start_time = datetime.now()
        self.x_sinergis_helpdesk_ticket_end_time = datetime.now()


    @api.onchange("stage_id")
    def on_change_stage_id_sinergis(self):
        if self.stage_id.name == "En cours":
            self.x_sinergis_helpdesk_ticket_is_solved = False
        elif self.stage_id.name == "Résolu":
            user_id = self.user_id
            if user_id != self.env.user :
                raise ValidationError("Vous ne pouvez pas marquer un ticket que ne vous est pas assigné comme résolu.")

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
            if self.x_sinergis_helpdesk_ticket_produits_divers:
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
        self.x_sinergis_helpdesk_ticket_planned_intervention = True

    def x_sinergis_intervention_unplanned(self):
        self.x_sinergis_helpdesk_ticket_planned_intervention = False

    def x_sinergis_helpdesk_ticket_show_facturation_button (self):
        self.x_sinergis_helpdesk_ticket_show_facturation = not self.x_sinergis_helpdesk_ticket_show_facturation

    def x_sinergis_helpdesk_ticket_duree_button(self):
        if self.x_sinergis_helpdesk_ticket_temps_passe <= 0 and self.x_sinergis_helpdesk_ticket_is_facturee == False:
            raise ValidationError("Le temps passé doit être supérieur à 0.")
        if not self.user_id:
            raise ValidationError("Vous devez assigner une personne pour décompter des heures.")
        if self.x_sinergis_helpdesk_ticket_taches :
            self.x_sinergis_helpdesk_ticket_is_facturee = True
            name = self.name
            self.x_sinergis_helpdesk_ticket_taches.timesheet_ids = [(0,0,{'name' : name, 'x_sinergis_account_analytic_line_user_id' : self.user_id.id,'unit_amount' : self.x_sinergis_helpdesk_ticket_temps_passe,'x_sinergis_account_analytic_line_ticket_id' : self.id, 'x_sinergis_account_analytic_line_start_time': self.x_sinergis_helpdesk_ticket_start_time ,'x_sinergis_account_analytic_line_end_time': self.x_sinergis_helpdesk_ticket_end_time})]
            HelpdeskTicket.setTacheInformation(self)

    def x_sinergis_helpdesk_ticket_reset_button (self):
        if self.x_sinergis_helpdesk_ticket_is_facturee:
            self.env["account.analytic.line"].search([('x_sinergis_account_analytic_line_ticket_id', '=', self.id)]).unlink()
            self.x_sinergis_helpdesk_ticket_is_facturee = not self.x_sinergis_helpdesk_ticket_is_facturee

    def x_sinergis_helpdesk_ticket_start_time_button (self):
        self.x_sinergis_helpdesk_ticket_start_time = datetime.now()

    def x_sinergis_helpdesk_ticket_stop_time_button (self):
        self.x_sinergis_helpdesk_ticket_end_time = datetime.now()
        self.x_sinergis_helpdesk_ticket_temps_passe = (self.x_sinergis_helpdesk_ticket_end_time - self.x_sinergis_helpdesk_ticket_start_time).total_seconds() / 3600

    #L'objectif est d'empecher les gens non assignés de changer le ticket une fois celui-ci terminé
    def write(self, values):
        user_id = self.user_id
        if user_id != self.env.user and self.stage_id.name == "Résolu":
            raise ValidationError("Vous ne pouvez pas modifier un ticket cloturé qui ne vous est pas assigné.")
        return super(HelpdeskTicket, self).write(values)

    #Lors de la création de ticket via mail, ajouter automatiquement le contact et la société attribuée
    @api.model_create_multi
    def create(self, list_value):
        for vals in list_value:
            if self.env['res.partner'].search([('id','=',vals["partner_id"])]).is_company == False:
                vals["x_sinergis_helpdesk_ticket_contact"] = vals["partner_id"]
                vals["partner_id"] = self.env['res.partner'].search([('id','=',vals["partner_id"])]).parent_id.id
        tickets = super(HelpdeskTicket, self).create(list_value)
        return tickets
