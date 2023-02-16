from odoo import http
from odoo.http import request
from datetime import date

class StatisticsDashboard(http.Controller):
    @http.route('/sinergis/statistics_dashboard', auth='user', methods=['GET','POST'])
    def index (self, **kw):
        uid = request.uid

        #DEBUG
        #Add user group verification
        today = date.today()
        data = ""
        #Filtre pour tâches CH non archivées et archivées
        n = 0
        #END DEBUG

        total_hours = 0

        tasks = request.env["project.task"].search(['|','&','&',('active','=',False),('active','=',True),('create_date','<=','2023-02-16'),'&',('project_id.name','ilike','HEURES'),('project_id.name','ilike','CONTRAT D')])
        for task in tasks :
            #Par on fixe le nombre d'heures au temps prévu par le CH
            task_hours = task.planned_hours
            timesheet_ids = task.timesheet_ids
            # On soustrait ensuite chaque intervention avant la date demandée
            timesheet_ids = request.env["account.analytic.line"].search([('task_id', '=', task.id)])
            for timesheet_id in timesheet_ids :
                task_hours -= timesheet_id.unit_amount
            total_hours += task_hours
        return total_hours