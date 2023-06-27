from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime
import math
import pytz


class ProjectTask(models.Model):
    _inherit = "project.task"

    x_sinergis_project_task_etat_tache = fields.Selection([("Tâche en cours", "Tâche en cours"),('Tâche terminée', 'Tâche terminée')], string="Etat de la tâche")
    x_sinergis_project_task_details_ch = fields.Char(string="Détails contrat d'heures")
    x_sinergis_project_task_alerte = fields.Char(compute="_compute_x_sinergis_project_task_alerte")

    #Variables pour les filtres
    x_sinergis_project_task_done = fields.Boolean(default=False,compute="_compute_x_sinergis_project_task_done", store=False)
    x_sinergis_project_task_soon_done = fields.Boolean(default=False,compute="_compute_x_sinergis_project_task_soon_done", store=False)

    #Tags lié au projet
    x_sinergis_project_task_tag_ids = fields.Many2many(related="project_id.tag_ids", string="Tags du projet")

    x_sinergis_project_task_planned_hours = fields.Float(compute="_compute_x_sinergis_project_task_planned_hours", string="Heures planifiées")

    #Date du premier évènement du calendrier associé à la tâche
    x_sinergis_project_task_first_date = fields.Datetime(compute="_compute_x_sinergis_project_task_first_date", string="Date premier évènement")
    #Employé du premier évènement du calendrier associé à la tâche
    x_sinergis_project_task_first_date_user_id = fields.Many2one("res.users", compute="_compute_x_sinergis_project_task_first_date_user_id", string="Premier évènement par")

    #Indique si la tâche est un CH
    x_sinergis_project_task_contract_type = fields.Selection([('CH', 'CH'), ('DEVIS', 'DEVIS')], compute="_compute_x_sinergis_project_task_contract_type", store=False)
    x_sinergis_project_task_contract_type_stored = fields.Selection([('CH', 'CH'), ('DEVIS', 'DEVIS')], related="x_sinergis_project_task_contract_type", store=True)

    #Récupère le produit et le sous-produit du devis et de la ligne de vente
    x_sinergis_project_task_product_id = fields.Many2one("sale.products",string="Produit", related="sale_order_id.x_sinergis_sale_order_product_new", store=True)
    x_sinergis_project_task_subproduct_id = fields.Many2one("sale.products.subproducts",string="Sous-Produit", related="sale_line_id.x_sinergis_sale_order_line_subproduct_id", store=True)

    #4/03/2023 : Ajout d'un bouton éditer pour éditer chaque feuille d'intervention des intervenitons passées
    # Champ booléen pour savoir s'il y a des interventions dans le calendriers attachés à cette tache
    x_sinergis_project_task_is_calendar_event = fields.Boolean(compute="_compute_x_sinergis_project_task_is_calendar_event")

    #4/03/2023 : Permettre le transfert du solde du CH
    x_sinergis_project_task_transfer_task_id = fields.Many2one("project.task",string="Nouveau contrat d'heures")
    x_sinergis_project_task_transfer_archive = fields.Boolean(default=True, string="Archiver ensuite ce contrat")

    # 7 Mars 2023 - Ajout d'un vendeur
    x_sinergis_project_task_seller_id = fields.Many2one("res.users", related="sale_line_id.order_id.user_id",string='Vendeur')
    x_sinergis_project_task_seller_id_stored = fields.Many2one("res.users", related="x_sinergis_project_task_seller_id",string='Vendeur', store=True)


    #Onglet "SUIVI" -  Boutton télécharger la feuille de temps
    def print_timesheet_button(self):
        return self.env.ref('sinergis.sinergis_report_timesheet').report_action(self)
    
    def calendar_events_button(self):
        return {
            'name': ('Évènements'),
            'type': 'ir.actions.act_window',
            "views": [[False, "tree"],[False, "form"]],
            'res_model': 'calendar.event',
            'domain': f"['|',('x_sinergis_calendar_event_tache', '=', {self.id}),('x_sinergis_calendar_event_tache2', '=', {self.id})]",
        }
        pass

    def print_calendar_reports(self):
        ids = []
        events = self.env['calendar.event'].search([('x_sinergis_calendar_event_tache', '=', self.id)], order='x_sinergis_calendar_event_start_time desc')
        for event in events:
            ids.append(event.id)
        return self.env.ref('sinergis.sinergis_intervention_report_calendar').report_action(self.env['calendar.event'].search([('id', '=', ids)]))
    
    # Bouton de transfert de contrat d'heures
    def transfer_ch_button (self):
        if not self.x_sinergis_project_task_transfer_task_id :
            raise ValidationError("Vous devez sélectionner un contrat d'heures afin de transférer le solde de celui-ci.")
        if self.remaining_hours == 0:
            raise ValidationError("Vous ne pouvez pas transférer le solde de ce contrat d'heures car il est actuellement à zéro.")
        name = f"Transfert du contrat du contrat d'heures : {self.name} vers {self.x_sinergis_project_task_transfer_task_id.name}"
        time = self.remaining_hours
        self.timesheet_ids = [(0,0,{'name' : name, 'x_sinergis_account_analytic_line_user_id' : self.env.user.id, 'unit_amount' : time})]
        self.x_sinergis_project_task_transfer_task_id.timesheet_ids = [(0,0,{'name' : name, 'x_sinergis_account_analytic_line_user_id' : self.env.user.id, 'unit_amount' : -time})]
        self.x_sinergis_project_task_transfer_task_id = False
        #Archiver le contrat d'heures si on souhaite l'archiver après transfert
        if self.x_sinergis_project_task_transfer_archive :
            self.active = False

    @api.depends('x_sinergis_project_task_done')
    def _compute_x_sinergis_project_task_done (self):
        for rec in self :
            rec.x_sinergis_project_task_done = rec.effective_hours >= rec.planned_hours

    @api.depends('x_sinergis_project_task_soon_done')
    def _compute_x_sinergis_project_task_soon_done (self):
        for rec in self :
            rec.x_sinergis_project_task_soon_done = rec.effective_hours >= rec.planned_hours

    @api.depends('x_sinergis_project_task_alerte')
    def _compute_x_sinergis_project_task_alerte (self):
        tache = self
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
            self.x_sinergis_project_task_alerte = "Attention ! Le contrat d'heures est périmé !"
            return

        if tache.effective_hours>=tache.planned_hours:
            self.x_sinergis_project_task_alerte = "Attention ! Le contrat est terminé, merci de consulter un commercial."
        elif tache.effective_hours>=0.9*tache.planned_hours:
            hours = int(tache.remaining_hours)
            minutes = math.ceil((tache.remaining_hours - hours)*60)
            self.x_sinergis_project_task_alerte = "Attention ! Il reste uniquement " + str(hours) + " heures et " + str(minutes) + " minutes sur le contrat"
        else : self.x_sinergis_project_task_alerte = False

    @api.depends('x_sinergis_project_task_planned_hours')
    def _compute_x_sinergis_project_task_planned_hours (self):
        for rec in self:
            rec.x_sinergis_project_task_planned_hours = sum(rec.env['calendar.event'].search(['|',('x_sinergis_calendar_event_tache', '=', rec.id),('x_sinergis_calendar_event_tache2', '=', rec.id)]).mapped('duration'))

    @api.depends('x_sinergis_project_task_first_date')
    def _compute_x_sinergis_project_task_first_date (self):
        for rec in self:
            firstDate = rec.env['calendar.event'].search(['|',('x_sinergis_calendar_event_tache', '=', rec.id),('x_sinergis_calendar_event_tache2', '=', rec.id)], order='start asc')
            if firstDate :
                rec.x_sinergis_project_task_first_date = firstDate[0].start
            else:
                rec.x_sinergis_project_task_first_date = False

    @api.depends('x_sinergis_project_task_first_date_user_id')
    def _compute_x_sinergis_project_task_first_date_user_id (self):
        for rec in self:
            firstDate = rec.env['calendar.event'].search(['|',('x_sinergis_calendar_event_tache', '=', rec.id),('x_sinergis_calendar_event_tache2', '=', rec.id)], order='start asc')
            if firstDate :
                rec.x_sinergis_project_task_first_date_user_id = firstDate[0].user_id
            else:
                rec.x_sinergis_project_task_first_date_user_id = False

    @api.depends('x_sinergis_project_task_contract_type')
    def _compute_x_sinergis_project_task_contract_type (self):
        for rec in self :
            if "CONTRAT D'HEURE" in rec.project_id.name:
                rec.x_sinergis_project_task_contract_type = 'CH'
            else :
                rec.x_sinergis_project_task_contract_type = 'DEVIS'

    @api.depends('x_sinergis_project_task_is_calendar_event')
    def _compute_x_sinergis_project_task_is_calendar_event (self):
        for rec in self:
            count = self.env['calendar.event'].search_count([('x_sinergis_calendar_event_tache', '=', rec.id)])
            if count > 0 :
                rec.x_sinergis_project_task_is_calendar_event = True
            else:
                rec.x_sinergis_project_task_is_calendar_event = False

    @api.onchange("x_sinergis_project_task_etat_tache")
    def on_change_x_sinergis_project_task_etat_tache(self):
        if self.x_sinergis_project_task_etat_tache :
            completedTasks = True
            if self.x_sinergis_project_task_etat_tache != 'Tâche terminée' :
                completedTasks = False
            for record in self.project_id.task_ids:
                if record.name != self.name:
                    if record.x_sinergis_project_task_etat_tache != 'Tâche terminée' :
                        completedTasks = False
            if completedTasks :
                self.project_id.x_sinergis_project_project_etat_projet = "Projet terminé"
        
    def write(self, values_list):
        for values in values_list:
            if "active" in values :
                if values["active"] :
                    body = f"Cette tâche a été désarchivée le {datetime.now(pytz.timezone('America/Guadeloupe')).strftime('%Y/%m/%d à %H:%M:%S')} (horaire de Guadeloupe)."
                else:
                    body = f"Cette tâche a été archivée le {datetime.now(pytz.timezone('America/Guadeloupe')).strftime('%Y/%m/%d à %H:%M:%S')} (horaire de Guadeloupe)."
                self.message_post(body=body)
        return super(ProjectTask, self).write(values_list)


class ProjectProject(models.Model):
    _inherit = "project.project"

    x_sinergis_project_project_acompte_verse = fields.Boolean(string="Acompte versé", compute="_compute_x_sinergis_project_project_acompte_verse")

    x_sinergis_project_project_sale_order_contact = fields.Many2one("res.partner", string="Contact de la vente",compute="_compute_x_sinergis_project_project_sale_order_contact")
    x_sinergis_project_project_sale_order_contact_phone = fields.Char(string="Téléphone du contact",compute="_compute_x_sinergis_project_project_sale_order_contact_phone")

    x_sinergis_project_project_etat_projet = fields.Selection([("Projet en cours", "Projet en cours"),('Projet terminé', 'Projet terminé')], string="Etat du projet")
    x_sinergis_project_project_technical_manager = fields.Many2one("res.users", string="Responsable technique")

    x_sinergis_project_project_planned_hours = fields.Float(compute="_compute_x_sinergis_project_project_planned_hours", string="Heures planifiées")

    x_sinergis_project_res_users_job = fields.Selection(related="user_id.x_sinergis_res_users_job") #Type du vendeur : Consultant ou commercial

    # 7 Mars 2023 - Ajout des heures prévues initialement et des heures passées
    x_sinergis_project_project_initial_hours = fields.Float(compute="_compute_x_sinergis_project_project_initial_hours", string="Heures prévues initialement")
    x_sinergis_project_project_effective_hours = fields.Float(compute="_compute_x_sinergis_project_project_effective_hours", string="Heures passées")

    # 7 Mars 2023 - Ajout d'un vendeur
    x_sinergis_project_project_seller_id = fields.Many2one("res.users", related="sale_line_id.order_id.user_id",string='Vendeur')
    x_sinergis_project_project_seller_id_stored = fields.Many2one("res.users", related="x_sinergis_project_project_seller_id",string='Vendeur', store=True)

    @api.depends('x_sinergis_project_project_sale_order_contact')
    def _compute_x_sinergis_project_project_sale_order_contact (self):
        for rec in self:
            if rec.sale_order_id:
                if rec.sale_order_id.x_sinergis_sale_order_contact:
                    rec.x_sinergis_project_project_sale_order_contact = rec.sale_order_id.x_sinergis_sale_order_contact.id
                else :
                    rec.x_sinergis_project_project_sale_order_contact = False
            else:
                rec.x_sinergis_project_project_sale_order_contact = False

    @api.depends('x_sinergis_project_project_sale_order_contact_phone')
    def _compute_x_sinergis_project_project_sale_order_contact_phone (self):
        for rec in self:
            if rec.x_sinergis_project_project_sale_order_contact:
                rec.x_sinergis_project_project_sale_order_contact_phone = rec.x_sinergis_project_project_sale_order_contact.phone
            else :
                rec.x_sinergis_project_project_sale_order_contact_phone = rec.x_sinergis_project_project_sale_order_contact_phone

    @api.depends('x_sinergis_project_project_planned_hours')
    def _compute_x_sinergis_project_project_planned_hours (self):
        for rec in self:
            rec.x_sinergis_project_project_planned_hours = sum(rec.env['calendar.event'].search([('x_sinergis_calendar_event_project', '=', rec.id)]).mapped('duration'))

    @api.depends('x_sinergis_project_project_acompte_verse')
    def _compute_x_sinergis_project_project_acompte_verse (self):
        for rec in self :
            if rec.sale_line_id:
                rec.x_sinergis_project_project_acompte_verse = rec.sale_line_id.order_id.x_sinergis_sale_order_acompte_verse
            else:
                rec.x_sinergis_project_project_acompte_verse = False

    @api.depends('x_sinergis_project_project_initial_hours')
    def _compute_x_sinergis_project_project_initial_hours (self):
        for rec in self:
            task_ids = self.env['project.task'].search([('project_id','=',rec.id)])
            initial_hours = 0.0
            for task_id in task_ids:
                initial_hours += task_id.planned_hours
            rec.x_sinergis_project_project_initial_hours = initial_hours

    @api.depends('x_sinergis_project_project_effective_hours')
    def _compute_x_sinergis_project_project_effective_hours (self):
        for rec in self:
            task_ids = self.env['project.task'].search([('project_id','=',rec.id)])
            effective_hours = 0.0
            for task_id in task_ids:
                effective_hours += task_id.effective_hours
            rec.x_sinergis_project_project_effective_hours = effective_hours

    #@api.onchange("tag_ids")
    #def on_change_tag_ids (self):
    #    if "ACOMPTE VERSE (A PLANIFIER)" in self.tag_ids.mapped('name'):
    #        self.x_sinergis_project_project_acompte_verse = True

    def write(self, values):
        #Si on change le responsable technique du projet, mettre les assignés des tâches associées au même utilisateur si la tâche n'a pas d'assigné.
        if "x_sinergis_project_project_technical_manager" in values:
            if values["x_sinergis_project_project_technical_manager"] != False:
                task_ids = self.env['project.task'].search([('project_id','=',self.id)])
                for task in task_ids:
                    if not task.user_ids:
                        task.user_ids = [(4,values["x_sinergis_project_project_technical_manager"])]
        if "active" in values :
            if "CONTRAT D'HEURES" in self.name and values["active"] == False:
                raise ValidationError("Attention, vous ne pouvez pas archiver un projet contenant tous les contrats d'heures.")
        return super(ProjectProject, self).write(values)

    #Lors de la création de ticket via mail, ajouter automatiquement le contact et la société attribuée
    @api.model_create_multi
    def create(self, list_value):
        for vals in list_value:
            if "sale_line_id" in vals:
                sale_order_id = self.env['sale.order.line'].search([('id','=',vals["sale_line_id"])]).order_id
                if sale_order_id.partner_id:
                    vals["partner_id"] = sale_order_id.partner_id.id
                if "name" in vals:
                    vals["name"] = f"{vals['name']} - {sale_order_id.x_sinergis_sale_order_objet}"
        projects = super(ProjectProject, self).create(list_value)
        return projects
