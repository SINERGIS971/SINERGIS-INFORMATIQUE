from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime
import math


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

    x_sinergis_project_task_planned_hours = fields.Float(compute="_compute_x_sinergis_project_task_planned_hours")

    #Date du premier évènement du calendrier associé à la tâche
    x_sinergis_project_task_first_date = fields.Datetime(compute="_compute_x_sinergis_project_task_first_date", string="Date premier évènement")
    #Employé du premier évènement du calendrier associé à la tâche
    x_sinergis_project_task_first_date_user_id = fields.Many2one("res.users", compute="_compute_x_sinergis_project_task_first_date_user_id", string="Premier évènement par")

    #Onglet "SUIVI" -  Boutton télécharger la feuille de temps
    def print_timesheet_button(self):
        return self.env.ref('sinergis.sinergis_report_timesheet').report_action(self)

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


class ProjectProject(models.Model):
    _inherit = "project.project"

    x_sinergis_project_project_acompte_verse = fields.Boolean(default=0, string="Acompte versé")

    x_sinergis_project_project_sale_order_contact = fields.Many2one("res.partner", string="Contact de la vente",compute="_compute_x_sinergis_project_project_sale_order_contact")
    x_sinergis_project_project_sale_order_contact_phone = fields.Char(string="Téléphone du contact",compute="_compute_x_sinergis_project_project_sale_order_contact_phone")

    x_sinergis_project_project_etat_projet = fields.Selection([("Projet en cours", "Projet en cours"),('Projet terminé', 'Projet terminé')], string="Etat du projet")
    x_sinergis_project_project_technical_manager = fields.Many2one("res.users")

    x_sinergis_project_project_planned_hours = fields.Float(compute="_compute_x_sinergis_project_project_planned_hours")

    x_sinergis_project_res_users_job = fields.Selection(related="user_id.x_sinergis_res_users_job") #Type du vendeur : Consultant ou commercial

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

    @api.onchange("tag_ids")
    def on_change_tag_ids (self):
        if "ACOMPTE VERSE (A PLANIFIER)" in self.tag_ids.mapped('name'):
            self.x_sinergis_project_project_acompte_verse = True

    def write(self, values):
        #Si on change le responsable technique du projet, mettre les assignés des tâches associées au même utilisateur si la tâche n'a pas d'assigné.
        if "x_sinergis_project_project_technical_manager" in values:
            if values["x_sinergis_project_project_technical_manager"] != False:
                task_ids = self.env['project.task'].search([('project_id','=',self.id)])
                for task in task_ids:
                    if not task.user_ids:
                        task.user_ids = [(4,values["x_sinergis_project_project_technical_manager"])]
        return super(ProjectProject, self).write(values)
