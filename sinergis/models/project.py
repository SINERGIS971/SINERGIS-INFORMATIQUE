from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime


class ProjectTask(models.Model):
    _inherit = "project.task"

    x_sinergis_project_task_etat_tache = fields.Selection([("Tâche en cours", "Tâche en cours"),('Tâche terminée', 'Tâche terminée')], string="Etat de la tâche")
    x_sinergis_project_task_details_ch = fields.Char(string="Détails contrat d'heures")
    x_sinergis_project_task_alerte = fields.Char(compute="_compute_x_sinergis_project_task_alerte")


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
            minutes = int((tache.remaining_hours - hours)*60)
            self.x_sinergis_project_task_alerte = "Attention ! Il reste uniquement " + str(hours) + " heures et " + str(minutes) + " minutes sur le contrat"
        else : self.x_sinergis_project_task_alerte = False

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

    x_sinergis_project_project_etat_projet = fields.Selection([("Projet en cours", "Projet en cours"),('Projet terminé', 'Projet terminé')], string="Etat du projet")
